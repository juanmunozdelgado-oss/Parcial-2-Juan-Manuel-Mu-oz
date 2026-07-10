"""Simulador 2: Traducción de direcciones virtuales a físicas."""

from .paginacion import Paginacion, ResultadoTraduccion
from .segmentacion import Segmentacion, Segmento

__all__ = [
    "Paginacion",
    "ResultadoTraduccion",
    "Segmentacion",
    "Segmento",
]
