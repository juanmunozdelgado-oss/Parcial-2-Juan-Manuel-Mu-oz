"""Simulador 1: Asignación de memoria por particiones dinámicas."""

from .modelos import Proceso, Bloque
from .estrategias import (
    EstrategiaAsignacion,
    FirstFit,
    BestFit,
    WorstFit,
    obtener_estrategia,
)
from .administrador import AdministradorMemoria, ResultadoAsignacion

__all__ = [
    "Proceso",
    "Bloque",
    "EstrategiaAsignacion",
    "FirstFit",
    "BestFit",
    "WorstFit",
    "obtener_estrategia",
    "AdministradorMemoria",
    "ResultadoAsignacion",
]
