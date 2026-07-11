# Simulador de Administración de Memoria

**Sistemas Operativos · Práctica / Parcial**

Proyecto en **Python (POO)** que funciona **por consola** y se despliega en **Docker**.
No usa dependencias externas: solo la biblioteca estándar de Python.

Incluye dos simuladores:

1. **Asignación de memoria** — estrategias *First Fit*, *Best Fit* y *Worst Fit*, con
   cálculo de fragmentación **interna** y **externa**, asignación y liberación de procesos.
2. **Traducción de direcciones** — de direcciones virtuales a físicas mediante
   **Paginación** de un nivel o **Segmentación** de un nivel.

---

## 1. Estructura del proyecto

```
.
├── main.py                    # Aplicación de consola (menú interactivo)
├── requirements.txt           # (Solo usa la librería estándar de Python)
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Despliegue con un comando
├── .dockerignore
├── src/
│   ├── memoria/               # Simulador 1
│   │   ├── modelos.py         #   Proceso, Bloque
│   │   ├── estrategias.py     #   First/Best/Worst Fit (patrón Strategy)
│   │   └── administrador.py   #   AdministradorMemoria (splitting + coalescing)
│   ├── traduccion/            # Simulador 2
│   │   ├── paginacion.py      #   Paginación de un nivel
│   │   └── segmentacion.py    #   Segmentación de un nivel
│   └── entrada_salida.py      # Lectura de archivos JSON y ejecución de escenarios
├── ejemplos/                  # Archivos de entrada de ejemplo (JSON)
│   ├── memoria_ejemplo1.json
│   ├── memoria_ejemplo2.json
│   ├── paginacion_ejemplo1.json
│   └── segmentacion_ejemplo1.json
├── tests/
│   └── test_simuladores.py    # Casos de prueba (unittest)
└── informe/
    └── informe.tex            # Informe en LaTeX (para Overleaf)
```

---

## 2. Requisitos previos

Instala en tu equipo (Windows/Mac/Linux):

- **Python 3.10+** — https://www.python.org/downloads/ (marca *"Add Python to PATH"* en Windows).
- **Docker Desktop** — https://www.docker.com/products/docker-desktop/
- **Git** — https://git-scm.com/downloads
- **Visual Studio Code** — https://code.visualstudio.com/ (recomendado: extensión *Python*).

Verifica en una terminal:

```bash
python --version
docker --version
git --version
```

---

## 3. Ejecutar en local desde VS Code (sin Docker)

No necesitas instalar nada aparte de Python (el proyecto usa solo la librería estándar).

```bash
# 1) Abre la carpeta del proyecto en VS Code (File > Open Folder).

# 2) Ejecuta el programa (menú interactivo por consola)
python main.py

# 3) (Opcional) Ejecuta un escenario de ejemplo directamente desde un archivo
python main.py ejemplos/memoria_ejemplo1.json
```

Al ejecutar `python main.py` verás un menú:

```
1) Simulador de asignacion de memoria
2) Simulador de traduccion de direcciones
3) Ejecutar escenario de ejemplo (archivo JSON)
0) Salir
```

### Ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

---

## 4. Despliegue con Docker (requerido por el curso)

Como la aplicación es interactiva por consola, hay que ejecutarla en modo interactivo
(`-it` o `docker compose run`).

### Opción A — Docker Compose (recomendada)

```bash
# 1) Construir la imagen
docker compose build

# 2) Ejecutar la aplicación de consola de forma interactiva
docker compose run --rm simulador-memoria
```

### Opción B — Docker "a mano"

```bash
# 1) Construir la imagen
docker build -t simulador-memoria-so .

# 2) Ejecutar en modo interactivo (IMPORTANTE: usar -it por ser consola)
docker run -it --rm simulador-memoria-so

# Ejecutar directamente un escenario de ejemplo:
docker run -it --rm simulador-memoria-so ejemplos/paginacion_ejemplo1.json
```

> **Evidencia para el informe:** toma una captura de `docker compose build`
> (o `docker build`) y otra del menú de la aplicación corriendo dentro del
> contenedor. Esto cubre el requisito de *"evidencia del despliegue en Docker"*.

---

## 5. Formato de los archivos de entrada

### Asignación de memoria
```json
{
  "tipo": "memoria",
  "tamano_total": 1000,
  "alineacion": 1,
  "estrategia": "best_fit",
  "operaciones": [
    { "accion": "asignar", "pid": "P1", "tamano": 200 },
    { "accion": "liberar", "pid": "P1" }
  ]
}
```
`estrategia`: `first_fit` | `best_fit` | `worst_fit`.
`alineacion` > 1 redondea cada solicitud y genera **fragmentación interna**.

### Paginación
```json
{
  "tipo": "paginacion",
  "memoria_virtual": 64,
  "memoria_fisica": 32,
  "tamano_pagina": 8,
  "tabla_paginas": { "0": 3, "1": 1, "2": 0, "5": 2 },
  "direcciones": [0, 5, 9, 20, 42, 63]
}
```

### Segmentación
```json
{
  "tipo": "segmentacion",
  "memoria_fisica": 2000,
  "segmentos": [
    { "numero": 0, "nombre": "codigo", "base": 100, "limite": 500 }
  ],
  "accesos": [ { "segmento": 0, "desplazamiento": 50 } ]
}
```