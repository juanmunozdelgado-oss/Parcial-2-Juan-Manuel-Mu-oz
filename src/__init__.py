"""Simulador de Administración de Memoria - Sistemas Operativos (Univalle).

Paquete raíz que agrupa los dos simuladores:
    - src.memoria      -> Simulador 1: asignación de memoria (First/Best/Worst Fit).
    - src.traduccion   -> Simulador 2: traducción de direcciones (paginación/segmentación).
"""

__all__ = ["memoria", "traduccion", "entrada_salida"]
