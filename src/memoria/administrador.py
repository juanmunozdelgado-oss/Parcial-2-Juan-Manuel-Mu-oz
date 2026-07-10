"""Administrador de memoria: coordina asignación y liberación de procesos.

Modelo empleado: **particiones dinámicas** con división de huecos (splitting) y
fusión de huecos adyacentes (coalescing) al liberar.

Fragmentación:
    - Externa: memoria libre total que NO está en el hueco contiguo más grande.
      Es memoria disponible pero dispersa en huecos pequeños.
    - Interna: memoria asignada de más a un proceso por efecto de la alineación
      (cada solicitud se redondea al múltiplo de `alineacion`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from .estrategias import EstrategiaAsignacion, FirstFit
from .modelos import Bloque, Proceso


@dataclass
class ResultadoAsignacion:
    """Resultado de intentar asignar un proceso."""

    exito: bool
    mensaje: str
    proceso: Optional[Proceso] = None
    bloque: Optional[Bloque] = None


class AdministradorMemoria:
    """Gestiona un espacio de memoria contiguo mediante particiones dinámicas."""

    def __init__(
        self,
        tamano_total: int,
        estrategia: Optional[EstrategiaAsignacion] = None,
        alineacion: int = 1,
    ) -> None:
        """Inicializa la memoria como un único hueco libre.

        Args:
            tamano_total: Tamaño total de la memoria en KB.
            estrategia: Política de asignación (First/Best/Worst Fit).
            alineacion: Unidad de redondeo de las solicitudes (>=1). Valores >1
                producen fragmentación interna y permiten estudiarla.
        """
        if tamano_total <= 0:
            raise ValueError("El tamaño total de memoria debe ser positivo.")
        if alineacion < 1:
            raise ValueError("La alineación debe ser >= 1.")

        self.tamano_total = tamano_total
        self.alineacion = alineacion
        self.estrategia: EstrategiaAsignacion = estrategia or FirstFit()
        # La memoria arranca como un solo hueco libre que la cubre por completo.
        self.bloques: List[Bloque] = [Bloque(inicio=0, tamano=tamano_total)]

    # ------------------------------------------------------------------ #
    # Operaciones principales
    # ------------------------------------------------------------------ #
    def cambiar_estrategia(self, estrategia: EstrategiaAsignacion) -> None:
        """Cambia la política de asignación en tiempo de ejecución."""
        self.estrategia = estrategia

    def _tamano_alineado(self, tamano: int) -> int:
        """Redondea la solicitud al múltiplo de `alineacion` superior."""
        return int(math.ceil(tamano / self.alineacion) * self.alineacion)

    def asignar(self, proceso: Proceso) -> ResultadoAsignacion:
        """Asigna memoria a un proceso usando la estrategia configurada."""
        if any(not b.libre and b.proceso.pid == proceso.pid for b in self.bloques):
            return ResultadoAsignacion(
                False, f"El proceso {proceso.pid} ya tiene memoria asignada."
            )

        tamano_efectivo = self._tamano_alineado(proceso.tamano)
        if tamano_efectivo > self.tamano_total:
            return ResultadoAsignacion(
                False,
                f"{proceso.pid} necesita {tamano_efectivo} KB, "
                f"mayor que la memoria total ({self.tamano_total} KB).",
            )

        huecos = [b for b in self.bloques if b.libre]
        elegido = self.estrategia.seleccionar(huecos, tamano_efectivo)
        if elegido is None:
            return ResultadoAsignacion(
                False,
                f"No hay un hueco contiguo de {tamano_efectivo} KB para "
                f"{proceso.pid} (fragmentación externa).",
            )

        bloque_asignado = self._ocupar(elegido, proceso, tamano_efectivo)
        return ResultadoAsignacion(
            True,
            f"{proceso.pid} asignado en [{bloque_asignado.inicio}-"
            f"{bloque_asignado.fin}] con {self.estrategia.nombre}.",
            proceso=proceso,
            bloque=bloque_asignado,
        )

    def _ocupar(self, hueco: Bloque, proceso: Proceso, tamano_efectivo: int) -> Bloque:
        """Ocupa un hueco con un proceso, dividiéndolo si sobra espacio."""
        indice = self.bloques.index(hueco)
        sobrante = hueco.tamano - tamano_efectivo

        hueco.tamano = tamano_efectivo
        hueco.proceso = proceso
        hueco.tamano_solicitado = proceso.tamano

        if sobrante > 0:
            # El espacio restante se convierte en un nuevo hueco libre contiguo.
            nuevo_hueco = Bloque(inicio=hueco.inicio + tamano_efectivo, tamano=sobrante)
            self.bloques.insert(indice + 1, nuevo_hueco)
        return hueco

    def liberar(self, pid: str) -> ResultadoAsignacion:
        """Libera la memoria de un proceso y fusiona huecos adyacentes."""
        objetivo = next(
            (b for b in self.bloques if not b.libre and b.proceso.pid == pid), None
        )
        if objetivo is None:
            return ResultadoAsignacion(False, f"No existe el proceso ocupado {pid}.")

        objetivo.proceso = None
        objetivo.tamano_solicitado = None
        self._fusionar_huecos()
        return ResultadoAsignacion(True, f"Memoria de {pid} liberada.")

    def _fusionar_huecos(self) -> None:
        """Une huecos libres contiguos en uno solo (coalescing)."""
        self.bloques.sort(key=lambda b: b.inicio)
        fusionados: List[Bloque] = []
        for bloque in self.bloques:
            if fusionados and fusionados[-1].libre and bloque.libre:
                fusionados[-1].tamano += bloque.tamano
            else:
                fusionados.append(bloque)
        self.bloques = fusionados

    def reiniciar(self) -> None:
        """Restablece la memoria a un único hueco libre."""
        self.bloques = [Bloque(inicio=0, tamano=self.tamano_total)]

    # ------------------------------------------------------------------ #
    # Métricas y consultas
    # ------------------------------------------------------------------ #
    @property
    def bloques_libres(self) -> List[Bloque]:
        return [b for b in self.bloques if b.libre]

    @property
    def bloques_ocupados(self) -> List[Bloque]:
        return [b for b in self.bloques if not b.libre]

    @property
    def memoria_libre(self) -> int:
        """Suma de todos los huecos libres."""
        return sum(b.tamano for b in self.bloques_libres)

    @property
    def memoria_ocupada(self) -> int:
        return sum(b.tamano for b in self.bloques_ocupados)

    @property
    def fragmentacion_externa(self) -> int:
        """Memoria libre que no cabe en el hueco contiguo más grande.

        Métrica clásica: si toda la memoria libre estuviera junta, este valor
        sería 0. Cuanto mayor, más dispersa (fragmentada) está la memoria libre.
        """
        libres = self.bloques_libres
        if not libres:
            return 0
        mayor_hueco = max(b.tamano for b in libres)
        return self.memoria_libre - mayor_hueco

    @property
    def fragmentacion_interna(self) -> int:
        """Suma de la memoria desperdiciada dentro de bloques ocupados."""
        return sum(b.fragmentacion_interna for b in self.bloques_ocupados)

    @property
    def mayor_hueco_libre(self) -> int:
        libres = self.bloques_libres
        return max((b.tamano for b in libres), default=0)

    def resumen(self) -> dict:
        """Devuelve un diccionario con el estado y las métricas actuales."""
        return {
            "estrategia": self.estrategia.nombre,
            "tamano_total": self.tamano_total,
            "memoria_ocupada": self.memoria_ocupada,
            "memoria_libre": self.memoria_libre,
            "mayor_hueco_libre": self.mayor_hueco_libre,
            "fragmentacion_externa": self.fragmentacion_externa,
            "fragmentacion_interna": self.fragmentacion_interna,
            "num_bloques": len(self.bloques),
            "bloques": [b.a_dict() for b in self.bloques],
        }
