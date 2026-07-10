"""Simulador de Administracion de Memoria - Aplicacion de consola.

Ejecucion:
    python main.py                     -> menu interactivo
    python main.py archivo.json        -> ejecuta un escenario desde archivo JSON

El menu interactivo permite:
    1) Simulador de asignacion de memoria (First/Best/Worst Fit)
    2) Simulador de traduccion de direcciones (paginacion / segmentacion)
    3) Ejecutar los escenarios de ejemplo incluidos en la carpeta 'ejemplos/'
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from src.entrada_salida import cargar_json, ejecutar_escenario
from src.memoria import AdministradorMemoria, Proceso, obtener_estrategia
from src.traduccion import Paginacion, Segmentacion, Segmento

LINEA = "=" * 70
SUBLINEA = "-" * 70


# --------------------------------------------------------------------- #
# Utilidades de entrada por consola
# --------------------------------------------------------------------- #
def leer_entero(mensaje: str, minimo: int | None = None) -> int:
    """Pide un entero por consola validando el rango."""
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                print(f"  ! Debe ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  ! Ingrese un numero entero valido.")


def leer_texto(mensaje: str) -> str:
    """Pide texto no vacio por consola."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  ! El valor no puede estar vacio.")


def pausar() -> None:
    input("\nPresione ENTER para continuar...")


# --------------------------------------------------------------------- #
# Impresion de resultados
# --------------------------------------------------------------------- #
def imprimir_mapa_memoria(admin: AdministradorMemoria) -> None:
    """Dibuja el estado de la memoria en consola."""
    r = admin.resumen()
    print(SUBLINEA)
    print(f"Estrategia            : {r['estrategia']}")
    print(f"Memoria total         : {r['tamano_total']} KB")
    print(f"Ocupada / Libre       : {r['memoria_ocupada']} / {r['memoria_libre']} KB")
    print(f"Mayor hueco libre     : {r['mayor_hueco_libre']} KB")
    print(f"Fragmentacion externa : {r['fragmentacion_externa']} KB")
    print(f"Fragmentacion interna : {r['fragmentacion_interna']} KB")
    print(SUBLINEA)
    print(f"{'INICIO':>7} {'FIN':>7} {'TAMANO':>7}  {'ESTADO':<8} PROCESO")
    for b in r["bloques"]:
        barra = "#" * max(1, round(b["tamano"] / r["tamano_total"] * 40))
        print(
            f"{b['inicio']:>7} {b['fin']:>7} {b['tamano']:>7}  "
            f"{b['estado']:<8} {b['proceso'] or '-':<6} {barra}"
        )
    print(SUBLINEA)


# --------------------------------------------------------------------- #
# Simulador 1: asignacion de memoria (interactivo)
# --------------------------------------------------------------------- #
def menu_memoria() -> None:
    print("\n" + LINEA)
    print("SIMULADOR 1: ASIGNACION DE MEMORIA (particiones dinamicas)")
    print(LINEA)

    total = leer_entero("Tamano total de memoria (KB): ", minimo=1)
    print("\nEstrategias disponibles: first_fit | best_fit | worst_fit")
    estrategia = leer_texto("Estrategia: ").lower()
    alineacion = leer_entero("Alineacion (1 = sin fragmentacion interna): ", minimo=1)

    admin = AdministradorMemoria(
        tamano_total=total,
        estrategia=obtener_estrategia(estrategia),
        alineacion=alineacion,
    )

    while True:
        imprimir_mapa_memoria(admin)
        print("\nOpciones:")
        print("  1) Asignar proceso")
        print("  2) Liberar proceso")
        print("  3) Cambiar estrategia")
        print("  4) Reiniciar memoria")
        print("  0) Volver al menu principal")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            pid = leer_texto("  PID del proceso (ej. P1): ")
            tamano = leer_entero("  Tamano solicitado (KB): ", minimo=1)
            res = admin.asignar(Proceso(pid=pid, tamano=tamano))
            print(("  [OK] " if res.exito else "  [ERROR] ") + res.mensaje)
        elif opcion == "2":
            pid = leer_texto("  PID a liberar: ")
            res = admin.liberar(pid)
            print(("  [OK] " if res.exito else "  [ERROR] ") + res.mensaje)
        elif opcion == "3":
            nueva = leer_texto("  Nueva estrategia: ").lower()
            admin.cambiar_estrategia(obtener_estrategia(nueva))
            print("  [OK] Estrategia actualizada.")
        elif opcion == "4":
            admin.reiniciar()
            print("  [OK] Memoria reiniciada.")
        elif opcion == "0":
            return
        else:
            print("  ! Opcion no valida.")


# --------------------------------------------------------------------- #
# Simulador 2: traduccion de direcciones (interactivo)
# --------------------------------------------------------------------- #
def menu_paginacion() -> None:
    print("\n" + LINEA)
    print("SIMULADOR 2A: TRADUCCION POR PAGINACION")
    print(LINEA)

    mem_virtual = leer_entero("Tamano memoria virtual (bytes): ", minimo=1)
    mem_fisica = leer_entero("Tamano memoria fisica (bytes): ", minimo=1)
    tam_pagina = leer_entero("Tamano de pagina (bytes): ", minimo=1)

    num_paginas = mem_virtual // tam_pagina
    tabla: dict[int, int] = {}
    print(f"\nDefina la tabla de paginas ({num_paginas} paginas: 0..{num_paginas - 1}).")
    print("Deje el marco vacio para marcar la pagina como NO presente.")
    for pagina in range(num_paginas):
        entrada = input(f"  Pagina {pagina} -> marco: ").strip()
        if entrada:
            tabla[pagina] = int(entrada)

    try:
        sim = Paginacion(mem_virtual, mem_fisica, tam_pagina, tabla)
    except ValueError as exc:
        print(f"\n[ERROR] Configuracion invalida: {exc}")
        return

    print("\n" + json.dumps(sim.resumen(), indent=2, ensure_ascii=False))

    while True:
        entrada = input("\nDireccion virtual a traducir (o 'q' para salir): ").strip()
        if entrada.lower() == "q":
            return
        try:
            direccion = int(entrada)
        except ValueError:
            print("  ! Ingrese un numero o 'q'.")
            continue
        res = sim.traducir(direccion).a_dict()
        print(f"  {res['estado']}: {res['detalle']}")
        if res["estado"] == "OK":
            print(
                f"     pagina={res['pagina']} offset={res['desplazamiento']} "
                f"marco={res['marco']} -> dir_fisica={res['dir_fisica']}"
            )


def menu_segmentacion() -> None:
    print("\n" + LINEA)
    print("SIMULADOR 2B: TRADUCCION POR SEGMENTACION")
    print(LINEA)

    mem_fisica = leer_entero("Tamano memoria fisica (bytes): ", minimo=1)
    num_seg = leer_entero("Numero de segmentos: ", minimo=1)

    segmentos: list[Segmento] = []
    for i in range(num_seg):
        print(f"\n  Segmento {i}:")
        nombre = input("    Nombre (opcional): ").strip()
        base = leer_entero("    Base (direccion fisica de inicio): ", minimo=0)
        limite = leer_entero("    Limite (tamano del segmento): ", minimo=1)
        segmentos.append(Segmento(numero=i, base=base, limite=limite, nombre=nombre))

    try:
        sim = Segmentacion(mem_fisica, segmentos)
    except ValueError as exc:
        print(f"\n[ERROR] Configuracion invalida: {exc}")
        return

    print("\n" + json.dumps(sim.resumen(), indent=2, ensure_ascii=False))

    while True:
        entrada = input("\nAcceso 'segmento desplazamiento' (o 'q' para salir): ").strip()
        if entrada.lower() == "q":
            return
        partes = entrada.split()
        if len(partes) != 2:
            print("  ! Formato: numero_segmento desplazamiento (ej. 0 50)")
            continue
        try:
            seg, desp = int(partes[0]), int(partes[1])
        except ValueError:
            print("  ! Ambos valores deben ser enteros.")
            continue
        res = sim.traducir(seg, desp).a_dict()
        print(f"  {res['estado']}: {res['detalle']}")
        if res["estado"] == "OK":
            print(f"     base={res['base']} + offset={desp} -> dir_fisica={res['dir_fisica']}")


def menu_traduccion() -> None:
    while True:
        print("\n" + LINEA)
        print("SIMULADOR 2: TRADUCCION DE DIRECCIONES")
        print(LINEA)
        print("  1) Paginacion")
        print("  2) Segmentacion")
        print("  0) Volver al menu principal")
        opcion = input("Opcion: ").strip()
        if opcion == "1":
            menu_paginacion()
        elif opcion == "2":
            menu_segmentacion()
        elif opcion == "0":
            return
        else:
            print("  ! Opcion no valida.")


# --------------------------------------------------------------------- #
# Ejecucion de escenarios de ejemplo desde archivos JSON
# --------------------------------------------------------------------- #
def imprimir_resultado_archivo(resultado: dict, origen: str) -> None:
    print("\n" + LINEA)
    print(f"Escenario: {origen}  (tipo: {resultado['tipo']})")
    print(LINEA)

    if resultado["tipo"] == "memoria":
        for linea in resultado["traza"]:
            print(linea)
        r = resultado["resumen"]
        print(SUBLINEA)
        print(f"Estrategia            : {r['estrategia']}")
        print(f"Ocupada / Libre       : {r['memoria_ocupada']} / {r['memoria_libre']} KB")
        print(f"Fragmentacion externa : {r['fragmentacion_externa']} KB")
        print(f"Fragmentacion interna : {r['fragmentacion_interna']} KB")
        print(SUBLINEA)
        for b in r["bloques"]:
            print(
                f"[{b['inicio']:>5}-{b['fin']:<5}] {b['tamano']:>5} KB  "
                f"{b['estado']:<8} {b['proceso'] or ''}"
            )
    else:
        print(json.dumps(resultado["resumen"], indent=2, ensure_ascii=False))
        print(SUBLINEA)
        for fila in resultado["resultados"]:
            print(fila)


def menu_ejemplos() -> None:
    carpeta = Path(__file__).parent / "ejemplos"
    archivos = sorted(carpeta.glob("*.json"))
    if not archivos:
        print("  ! No hay archivos de ejemplo en la carpeta 'ejemplos/'.")
        return

    print("\n" + LINEA)
    print("EJECUTAR ESCENARIO DE EJEMPLO")
    print(LINEA)
    for i, archivo in enumerate(archivos, start=1):
        print(f"  {i}) {archivo.name}")
    print("  0) Volver")

    opcion = input("Seleccione un archivo: ").strip()
    if opcion == "0":
        return
    try:
        indice = int(opcion) - 1
        archivo = archivos[indice]
    except (ValueError, IndexError):
        print("  ! Seleccion no valida.")
        return

    datos = cargar_json(archivo)
    resultado = ejecutar_escenario(datos)
    imprimir_resultado_archivo(resultado, archivo.name)


# --------------------------------------------------------------------- #
# Menu principal
# --------------------------------------------------------------------- #
def menu_principal() -> None:
    while True:
        print("\n" + LINEA)
        print("  SIMULADOR DE ADMINISTRACION DE MEMORIA - Sistemas Operativos")
        print(LINEA)
        print("  1) Simulador de asignacion de memoria")
        print("  2) Simulador de traduccion de direcciones")
        print("  3) Ejecutar escenario de ejemplo (archivo JSON)")
        print("  0) Salir")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            menu_memoria()
        elif opcion == "2":
            menu_traduccion()
        elif opcion == "3":
            menu_ejemplos()
            pausar()
        elif opcion == "0":
            print("\nHasta luego.\n")
            return
        else:
            print("  ! Opcion no valida.")


def ejecutar_desde_archivo(ruta: str) -> None:
    """Modo no interactivo: ejecuta un archivo JSON y muestra el resultado."""
    datos = cargar_json(ruta)
    resultado = ejecutar_escenario(datos)
    imprimir_resultado_archivo(resultado, ruta)


def main() -> None:
    if len(sys.argv) > 1:
        ejecutar_desde_archivo(sys.argv[1])
    else:
        try:
            menu_principal()
        except (KeyboardInterrupt, EOFError):
            print("\n\nInterrumpido por el usuario.\n")


if __name__ == "__main__":
    main()
