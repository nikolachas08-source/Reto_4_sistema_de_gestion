# -*- coding: utf-8 -*-
"""Configuración del archivo de log logs/sistema.log. (Rol 2)"""

# logging: biblioteca estándar para registrar eventos y errores.
import logging
# sys: detecta si el código se ejecuta desde el ejecutable compilado.
import sys
# Path: manejo de rutas independiente del sistema operativo.
from pathlib import Path

# Carpeta raíz del proyecto (un nivel arriba de "modelo"); en el .exe, la carpeta del ejecutable.
RAIZ_PROYECTO = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
                 else Path(__file__).resolve().parent.parent)
# Carpeta donde se guarda el log.
CARPETA_LOGS = RAIZ_PROYECTO / "logs"
# Ruta completa del archivo de log exigido por la rúbrica.
ARCHIVO_LOG = CARPETA_LOGS / "sistema.log"
# Nombre del logger compartido por todos los módulos.
NOMBRE_LOGGER = "software_fj"


# Devuelve el logger del sistema, configurándolo solo la primera vez.
def obtener_logger() -> logging.Logger:
    """Entrega el logger único; evita duplicar manejadores si se llama varias veces."""
    # Obtiene (o crea) el logger por su nombre.
    logger = logging.getLogger(NOMBRE_LOGGER)
    # Si ya tiene manejadores, ya fue configurado: se devuelve tal cual.
    if logger.handlers:
        return logger
    # Se registran eventos desde nivel INFO hacia arriba.
    logger.setLevel(logging.INFO)
    # Evita que los mensajes suban al logger raíz y se impriman dos veces.
    logger.propagate = False
    try:
        # Crea la carpeta logs/ si no existe.
        CARPETA_LOGS.mkdir(parents=True, exist_ok=True)
        # Manejador que escribe en el archivo (modo agregar, UTF-8 para las tildes).
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    except OSError:
        # Si no se puede escribir el archivo, se usa la consola para no detener el programa.
        manejador = logging.StreamHandler()
    # Formato: fecha, nivel, archivo:línea y mensaje.
    formato = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    # Aplica el formato al manejador.
    manejador.setFormatter(formato)
    # Conecta el manejador al logger.
    logger.addHandler(manejador)
    # Devuelve el logger listo para usar.
    return logger
