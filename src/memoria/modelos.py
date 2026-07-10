"""Modelos de dominio del Simulador 1 (asignación de memoria).

Se aplican principios de POO:
    - Encapsulamiento: los atributos se validan en el constructor.
    - Responsabilidad única: cada clase representa un único concepto.
    - Propiedades derivadas (`@property`) para exponer cálculos sin duplicar estado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proceso:
    """Representa un proceso que solicita memoria.

    Attributes:
        pid: Identificador único del proceso (ej. "P1").
        tamano: Cantidad de memoria (en KB) que el proceso necesita.
    """

    pid: str
    tamano: int

    def __post_init__(self) -> None:
        if not self.pid:
            raise ValueError("El proceso debe tener un identificador (pid).")
        if self.tamano <= 0:
            raise ValueError(f"El tamaño del proceso {self.pid} debe ser positivo.")

    def __str__(self) -> str:  # pragma: no cover - solo presentación
        return f"{self.pid} ({self.tamano} KB)"


@dataclass
class Bloque:
    """Representa un bloque contiguo de memoria (partición dinámica).

    Un bloque puede estar libre (hueco) u ocupado por un proceso.

    Attributes:
        inicio: Dirección base del bloque.
        tamano: Tamaño total del bloque en KB.
        proceso: Proceso alojado, o None si el bloque está libre.
        tamano_solicitado: Memoria realmente pedida por el proceso. Puede ser
            menor que `tamano` cuando se aplica alineación, generando
            fragmentación interna.
    """

    inicio: int
    tamano: int
    proceso: Optional[Proceso] = None
    tamano_solicitado: Optional[int] = field(default=None)

    @property
    def libre(self) -> bool:
        """True si el bloque no tiene un proceso asignado."""
        return self.proceso is None

    @property
    def fin(self) -> int:
        """Última dirección que ocupa el bloque."""
        return self.inicio + self.tamano - 1

    @property
    def fragmentacion_interna(self) -> int:
        """Memoria desperdiciada dentro de un bloque ocupado.

        Ocurre cuando se asigna más memoria que la solicitada por el proceso
        (por ejemplo, por alineación a múltiplos de una unidad).
        """
        if self.libre or self.tamano_solicitado is None:
            return 0
        return self.tamano - self.tamano_solicitado

    def a_dict(self) -> dict:
        """Serializa el bloque para reportes o salida en archivo."""
        return {
            "inicio": self.inicio,
            "fin": self.fin,
            "tamano": self.tamano,
            "estado": "LIBRE" if self.libre else "OCUPADO",
            "proceso": None if self.libre else self.proceso.pid,
            "solicitado": self.tamano_solicitado,
            "frag_interna": self.fragmentacion_interna,
        }

    def __str__(self) -> str:  # pragma: no cover - solo presentación
        estado = "LIBRE" if self.libre else f"OCUPADO por {self.proceso.pid}"
        return f"[{self.inicio}-{self.fin}] {self.tamano} KB -> {estado}"
