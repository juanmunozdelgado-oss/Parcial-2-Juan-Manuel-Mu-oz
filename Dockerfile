# Imagen base ligera y estable de Python.
FROM python:3.12-slim

# Evita archivos .pyc y fuerza salida sin buffer (logs en tiempo real).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar el codigo fuente de la aplicacion.
# El proyecto solo usa la biblioteca estandar, no hay dependencias que instalar.
COPY . .

# Aplicacion de consola interactiva.
# Se ejecuta con TTY (docker run -it ... o docker compose run).
ENTRYPOINT ["python", "main.py"]
