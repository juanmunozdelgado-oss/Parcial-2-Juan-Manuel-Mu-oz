"""Estrategias de asignación de memoria (patrón Strategy).

Cada estrategia recibe la lista de huecos (bloques libres) candidatos y decide
cuál usar para alojar un proceso de tamaño `tamano`. Devuelve el bloque elegido
o None si ninguno tiene capacidad suficiente.

Usar el patrón Strategy permite agregar nuevas políticas (ej. Next Fit) sin
modificar el AdministradorMemoria, cumpliendo el principio Abierto/Cerrado.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .modelos import Bloque


class EstrategiaAsignacion(ABC):
    """Interfaz común para todas las políticas de asignación."""

    nombre: str = "Genérica"

    @abstractmethod
    def seleccionar(self, huecos: List[Bloque], tamano: int) -> Optional[Bloque]:
        """Elige un hueco libre capaz de alojar `tamano` KB."""
        raise NotImplementedError

    def _candidatos(self, huecos: List[Bloque], tamano: int) -> List[Bloque]:
        """Filtra los huecos con capacidad suficiente."""
        return [h for h in huecos if h.libre and h.tamano >= tamano]

    def __str__(self) -> str:  # pragma: no cover
        return self.nombre


class FirstFit(EstrategiaAsignacion):
    """Primer ajuste: usa el primer hueco (por dirección) que quepa."""

    nombre = "First Fit"

    def seleccionar(self, huecos: List[Bloque], tamano: int) -> Optional[Bloque]:
        candidatos = self._candidatos(huecos, tamano)
        if not candidatos:
            return None
        # Los huecos ya vienen ordenados por dirección de inicio.
        return min(candidatos, key=lambda h: h.inicio)


class BestFit(EstrategiaAsignacion):
    """Mejor ajuste: usa el hueco más pequeño que quepa (minimiza sobrante)."""

    nombre = "Best Fit"

    def seleccionar(self, huecos: List[Bloque], tamano: int) -> Optional[Bloque]:
        candidatos = self._candidatos(huecos, tamano)
        if not candidatos:
            return None
        # Menor tamaño; ante empate, el de menor dirección para ser determinista.
        return min(candidatos, key=lambda h: (h.tamano, h.inicio))


class WorstFit(EstrategiaAsignacion):
    """Peor ajuste: usa el hueco más grande (deja sobrantes reutilizables)."""

    nombre = "Worst Fit"

    def seleccionar(self, huecos: List[Bloque], tamano: int) -> Optional[Bloque]:
        candidatos = self._candidatos(huecos, tamano)
        if not candidatos:
            return None
        # Mayor tamaño; ante empate, el de menor dirección.
        return max(candidatos, key=lambda h: (h.tamano, -h.inicio))


_ESTRATEGIAS = {
    "first_fit": FirstFit,
    "best_fit": BestFit,
    "worst_fit": WorstFit,
}


def obtener_estrategia(clave: str) -> EstrategiaAsignacion:
    """Factory que devuelve una instancia de estrategia a partir de su clave.

    Args:
        clave: "first_fit", "best_fit" o "worst_fit".

    Raises:
        ValueError: si la clave no corresponde a una estrategia conocida.
    """
    clave_norm = clave.strip().lower().replace(" ", "_")
    if clave_norm not in _ESTRATEGIAS:
        validas = ", ".join(_ESTRATEGIAS)
        raise ValueError(f"Estrategia '{clave}' no válida. Use una de: {validas}")
    return _ESTRATEGIAS[clave_norm]()
