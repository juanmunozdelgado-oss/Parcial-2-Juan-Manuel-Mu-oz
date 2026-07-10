"""Traducción de direcciones por Segmentación de un solo nivel.

Conceptos:
    - Cada segmento tiene una base (dirección física de inicio) y un límite
      (tamaño del segmento).
    - Una dirección virtual es un par (número de segmento, desplazamiento).
    - Dirección física = base(segmento) + desplazamiento, siempre que
      desplazamiento < límite(segmento). En caso contrario ocurre una violación
      de segmento (segmentation fault).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Segmento:
    """Entrada de la tabla de segmentos."""

    numero: int
    base: int
    limite: int
    nombre: str = ""

    def __post_init__(self) -> None:
        if self.base < 0 or self.limite <= 0:
            raise ValueError(f"Segmento {self.numero}: base>=0 y límite>0.")


@dataclass
class ResultadoTraduccion:
    """Resultado de traducir un par (segmento, desplazamiento)."""

    exito: bool
    numero_segmento: int
    desplazamiento: int
    mensaje: str
    base: Optional[int] = None
    limite: Optional[int] = None
    direccion_fisica: Optional[int] = None

    def a_dict(self) -> dict:
        return {
            "segmento": self.numero_segmento,
            "desplazamiento": self.desplazamiento,
            "base": self.base,
            "limite": self.limite,
            "dir_fisica": self.direccion_fisica,
            "estado": "OK" if self.exito else "FALLO",
            "detalle": self.mensaje,
        }


class Segmentacion:
    """Simulador de segmentación de un nivel."""

    def __init__(self, tamano_memoria_fisica: int, segmentos: List[Segmento]) -> None:
        """Configura el esquema de segmentación.

        Args:
            tamano_memoria_fisica: Tamaño de la memoria física (bytes).
            segmentos: Lista de segmentos con base y límite.
        """
        if tamano_memoria_fisica <= 0:
            raise ValueError("La memoria física debe ser positiva.")
        self.tamano_memoria_fisica = tamano_memoria_fisica
        self.tabla_segmentos: Dict[int, Segmento] = {}
        for seg in segmentos:
            if seg.base + seg.limite > tamano_memoria_fisica:
                raise ValueError(
                    f"Segmento {seg.numero} excede la memoria física."
                )
            if seg.numero in self.tabla_segmentos:
                raise ValueError(f"Segmento {seg.numero} duplicado.")
            self.tabla_segmentos[seg.numero] = seg

    def traducir(self, numero_segmento: int, desplazamiento: int) -> ResultadoTraduccion:
        """Traduce (segmento, desplazamiento) a dirección física."""
        if numero_segmento not in self.tabla_segmentos:
            return ResultadoTraduccion(
                False,
                numero_segmento,
                desplazamiento,
                f"El segmento {numero_segmento} no existe en la tabla.",
            )

        seg = self.tabla_segmentos[numero_segmento]
        if desplazamiento < 0 or desplazamiento >= seg.limite:
            return ResultadoTraduccion(
                False,
                numero_segmento,
                desplazamiento,
                f"Violación de segmento: desplazamiento {desplazamiento} "
                f">= límite {seg.limite}.",
                base=seg.base,
                limite=seg.limite,
            )

        direccion_fisica = seg.base + desplazamiento
        return ResultadoTraduccion(
            True,
            numero_segmento,
            desplazamiento,
            f"Segmento {numero_segmento} (base {seg.base}) + {desplazamiento}.",
            base=seg.base,
            limite=seg.limite,
            direccion_fisica=direccion_fisica,
        )

    def resumen(self) -> dict:
        return {
            "esquema": "Segmentación (un nivel)",
            "memoria_fisica": self.tamano_memoria_fisica,
            "num_segmentos": len(self.tabla_segmentos),
            "tabla_segmentos": [
                {
                    "segmento": s.numero,
                    "nombre": s.nombre,
                    "base": s.base,
                    "limite": s.limite,
                    "rango_fisico": f"{s.base}-{s.base + s.limite - 1}",
                }
                for s in sorted(self.tabla_segmentos.values(), key=lambda x: x.numero)
            ],
        }
