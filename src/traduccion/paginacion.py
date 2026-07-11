"""Traducción de direcciones por Paginación de un solo nivel.

Conceptos:
    - Dirección virtual = (número de página) * (tamaño de página) + desplazamiento.
    - La tabla de páginas mapea: página virtual -> marco físico.
    - Dirección física = (marco) * (tamaño de página) + desplazamiento.

Se valida que la dirección virtual esté dentro del espacio virtual, que la
página exista en la tabla y que tenga un marco válido asignado (bit de
presencia). En caso contrario se reporta un fallo de página o dirección inválida.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ResultadoTraduccion:
    """Resultado del proceso de traducción de una dirección virtual."""

    exito: bool
    direccion_virtual: int
    mensaje: str
    numero_pagina: Optional[int] = None
    desplazamiento: Optional[int] = None
    marco: Optional[int] = None
    direccion_fisica: Optional[int] = None

    def a_dict(self) -> dict:
        return {
            "dir_virtual": self.direccion_virtual,
            "pagina": self.numero_pagina,
            "desplazamiento": self.desplazamiento,
            "marco": self.marco,
            "dir_fisica": self.direccion_fisica,
            "estado": "OK" if self.exito else "FALLO",
            "detalle": self.mensaje,
        }


class Paginacion:
    """Simulador de paginación de un nivel."""

    def __init__(
        self,
        tamano_memoria_virtual: int,
        tamano_memoria_fisica: int,
        tamano_pagina: int,
        tabla_paginas: Optional[Dict[int, int]] = None,
    ) -> None:
        """Configura el esquema de paginación.

        Args:
            tamano_memoria_virtual: Tamaño del espacio virtual (bytes).
            tamano_memoria_fisica: Tamaño de la memoria física (bytes).
            tamano_pagina: Tamaño de página = tamaño de marco (bytes).
            tabla_paginas: Mapeo página->marco. Si es None, inicia vacía.
        """
        if min(tamano_memoria_virtual, tamano_memoria_fisica, tamano_pagina) <= 0:
            raise ValueError("Todos los tamaños deben ser positivos.")
        if tamano_memoria_virtual % tamano_pagina != 0:
            raise ValueError("La memoria virtual debe ser múltiplo del tamaño de página.")
        if tamano_memoria_fisica % tamano_pagina != 0:
            raise ValueError("La memoria física debe ser múltiplo del tamaño de página.")

        self.tamano_memoria_virtual = tamano_memoria_virtual
        self.tamano_memoria_fisica = tamano_memoria_fisica
        self.tamano_pagina = tamano_pagina
        self.num_paginas = tamano_memoria_virtual // tamano_pagina
        self.num_marcos = tamano_memoria_fisica // tamano_pagina
        self.tabla_paginas: Dict[int, int] = dict(tabla_paginas or {})
        self._validar_tabla()

    def _validar_tabla(self) -> None:
        """Verifica que las entradas de la tabla de páginas sean coherentes."""
        for pagina, marco in self.tabla_paginas.items():
            if not (0 <= pagina < self.num_paginas):
                raise ValueError(
                    f"Página {pagina} fuera de rango (0..{self.num_paginas - 1})."
                )
            if not (0 <= marco < self.num_marcos):
                raise ValueError(
                    f"Marco {marco} fuera de rango (0..{self.num_marcos - 1})."
                )


    @property
    def marcos_ocupados(self) -> List[int]:
        return sorted(self.tabla_paginas.values())

    @property
    def marcos_disponibles(self) -> List[int]:
        ocupados = set(self.tabla_paginas.values())
        return [m for m in range(self.num_marcos) if m not in ocupados]

    def traducir(self, direccion_virtual: int) -> ResultadoTraduccion:
        """Traduce una dirección virtual a su dirección física."""
        if direccion_virtual < 0 or direccion_virtual >= self.tamano_memoria_virtual:
            return ResultadoTraduccion(
                False,
                direccion_virtual,
                f"Dirección fuera del espacio virtual "
                f"(0..{self.tamano_memoria_virtual - 1}).",
            )

        numero_pagina = direccion_virtual // self.tamano_pagina
        desplazamiento = direccion_virtual % self.tamano_pagina

        if numero_pagina not in self.tabla_paginas:
            return ResultadoTraduccion(
                False,
                direccion_virtual,
                f"Fallo de página: la página {numero_pagina} no está en memoria.",
                numero_pagina=numero_pagina,
                desplazamiento=desplazamiento,
            )

        marco = self.tabla_paginas[numero_pagina]
        direccion_fisica = marco * self.tamano_pagina + desplazamiento
        return ResultadoTraduccion(
            True,
            direccion_virtual,
            f"Página {numero_pagina} -> Marco {marco}.",
            numero_pagina=numero_pagina,
            desplazamiento=desplazamiento,
            marco=marco,
            direccion_fisica=direccion_fisica,
        )

    def resumen(self) -> dict:
        return {
            "esquema": "Paginación (un nivel)",
            "memoria_virtual": self.tamano_memoria_virtual,
            "memoria_fisica": self.tamano_memoria_fisica,
            "tamano_pagina": self.tamano_pagina,
            "num_paginas": self.num_paginas,
            "num_marcos": self.num_marcos,
            "marcos_disponibles": self.marcos_disponibles,
            "tabla_paginas": dict(sorted(self.tabla_paginas.items())),
        }
