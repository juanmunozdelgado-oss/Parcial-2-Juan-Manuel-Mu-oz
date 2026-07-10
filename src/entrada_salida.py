"""Lectura de archivos de entrada y ejecución de escenarios.

Los archivos de entrada están en formato JSON. Se definen dos tipos:

1) Asignación de memoria (Simulador 1)
{
  "tipo": "memoria",
  "tamano_total": 1000,
  "alineacion": 1,
  "estrategia": "best_fit",
  "operaciones": [
    {"accion": "asignar", "pid": "P1", "tamano": 200},
    {"accion": "liberar", "pid": "P1"}
  ]
}

2) Traducción de direcciones (Simulador 2)
   - Paginación:
   {
     "tipo": "paginacion",
     "memoria_virtual": 64, "memoria_fisica": 32, "tamano_pagina": 8,
     "tabla_paginas": {"0": 3, "1": 1},
     "direcciones": [10, 20, 63]
   }
   - Segmentación:
   {
     "tipo": "segmentacion",
     "memoria_fisica": 1000,
     "segmentos": [{"numero": 0, "nombre": "codigo", "base": 100, "limite": 200}],
     "accesos": [{"segmento": 0, "desplazamiento": 50}]
   }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Union

from .memoria import AdministradorMemoria, Proceso, obtener_estrategia
from .traduccion import Paginacion, Segmentacion, Segmento


def cargar_json(ruta: Union[str, Path]) -> dict:
    """Carga y valida que un archivo JSON exista y tenga la clave 'tipo'."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    with ruta.open("r", encoding="utf-8") as f:
        datos = json.load(f)
    if "tipo" not in datos:
        raise ValueError("El archivo de entrada debe incluir la clave 'tipo'.")
    return datos


# ---------------------------------------------------------------------- #
# Ejecución de escenarios
# ---------------------------------------------------------------------- #
def ejecutar_memoria(datos: dict) -> Dict:
    """Ejecuta un escenario de asignación de memoria y devuelve la traza."""
    admin = AdministradorMemoria(
        tamano_total=int(datos["tamano_total"]),
        estrategia=obtener_estrategia(datos.get("estrategia", "first_fit")),
        alineacion=int(datos.get("alineacion", 1)),
    )

    traza: List[str] = []
    for op in datos.get("operaciones", []):
        accion = op.get("accion")
        if accion == "asignar":
            proceso = Proceso(pid=op["pid"], tamano=int(op["tamano"]))
            resultado = admin.asignar(proceso)
        elif accion == "liberar":
            resultado = admin.liberar(op["pid"])
        else:
            traza.append(f"[IGNORADA] acción desconocida: {accion}")
            continue
        marca = "OK " if resultado.exito else "ERR"
        traza.append(f"[{marca}] {resultado.mensaje}")

    return {"tipo": "memoria", "traza": traza, "resumen": admin.resumen()}


def ejecutar_paginacion(datos: dict) -> Dict:
    """Ejecuta un escenario de paginación y traduce cada dirección."""
    tabla = {int(k): int(v) for k, v in datos.get("tabla_paginas", {}).items()}
    sim = Paginacion(
        tamano_memoria_virtual=int(datos["memoria_virtual"]),
        tamano_memoria_fisica=int(datos["memoria_fisica"]),
        tamano_pagina=int(datos["tamano_pagina"]),
        tabla_paginas=tabla,
    )
    resultados = [sim.traducir(int(d)).a_dict() for d in datos.get("direcciones", [])]
    return {"tipo": "paginacion", "resultados": resultados, "resumen": sim.resumen()}


def ejecutar_segmentacion(datos: dict) -> Dict:
    """Ejecuta un escenario de segmentación y traduce cada acceso."""
    segmentos = [
        Segmento(
            numero=int(s["numero"]),
            base=int(s["base"]),
            limite=int(s["limite"]),
            nombre=s.get("nombre", ""),
        )
        for s in datos.get("segmentos", [])
    ]
    sim = Segmentacion(
        tamano_memoria_fisica=int(datos["memoria_fisica"]), segmentos=segmentos
    )
    resultados = [
        sim.traducir(int(a["segmento"]), int(a["desplazamiento"])).a_dict()
        for a in datos.get("accesos", [])
    ]
    return {"tipo": "segmentacion", "resultados": resultados, "resumen": sim.resumen()}


def ejecutar_escenario(datos: dict) -> Dict:
    """Despacha la ejecución según el 'tipo' del escenario."""
    tipo = datos["tipo"]
    despachador = {
        "memoria": ejecutar_memoria,
        "paginacion": ejecutar_paginacion,
        "segmentacion": ejecutar_segmentacion,
    }
    if tipo not in despachador:
        raise ValueError(f"Tipo de escenario no soportado: {tipo}")
    return despachador[tipo](datos)


def guardar_salida(resultado: Dict, ruta: Union[str, Path]) -> None:
    """Guarda el resultado de un escenario como archivo JSON."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
