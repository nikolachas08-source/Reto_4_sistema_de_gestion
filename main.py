# -*- coding: utf-8 -*-
"""Punto de entrada de Software FJ: ejecuta la simulación y abre la interfaz gráfica. (Rol 1)

Responsable: Nicolas David Ramirez Sanchez (@usuario3).

Uso:
    python main.py                 -> simulación en consola y luego la interfaz gráfica
    python main.py --solo-consola  -> solo la simulación (sin interfaz)
    python main.py --solo-gui      -> solo la interfaz gráfica
"""

# argparse: lectura de opciones de la línea de comandos.
import argparse
# sys: código de salida del programa.
import sys

# Logger compartido.
from modelo.registro import obtener_logger
# Simulación de operaciones.
from simulaciones import ejecutar_simulaciones

# Logger de este módulo.
logger = obtener_logger()

# Identificación mostrada al ejecutar: solo el número del grupo.
INTEGRANTES = [
    "Grupo 599",
]


# Abre la interfaz gráfica sin dejar que un fallo detenga el programa.
def abrir_interfaz() -> None:
    """Lanza la ventana Tkinter; si no hay pantalla o falta Tkinter, lo informa y sigue."""
    # Intenta importar y abrir la interfaz.
    try:
        # Se importa aquí para que la simulación funcione aunque Tkinter no exista.
        from gui import iniciar_aplicacion
        # Abre la ventana (bloquea hasta que se cierre).
        iniciar_aplicacion()
    # Falta Tkinter, o no hay entorno gráfico disponible.
    except Exception as error:
        # Registra el problema.
        logger.error("No fue posible abrir la interfaz gráfica: %s", error)
        # Informa al usuario sin cerrar el programa de forma abrupta.
        print(f"[AVISO] No se pudo abrir la interfaz gráfica ({error}). "
              "La simulación de consola sí se ejecutó.")


# Función principal.
def main() -> int:
    """Interpreta las opciones y ejecuta lo pedido; devuelve el código de salida."""
    # Define las opciones permitidas.
    parser = argparse.ArgumentParser(description="Sistema de gestión de Software FJ")
    # Opción: solo consola.
    parser.add_argument("--solo-consola", action="store_true", help="solo ejecuta la simulación")
    # Opción: solo interfaz.
    parser.add_argument("--solo-gui", action="store_true", help="solo abre la interfaz gráfica")
    # Lee los argumentos.
    args = parser.parse_args()
    # Registra el arranque.
    logger.info("Aplicación iniciada por: %s", "; ".join(INTEGRANTES))
    # Ejecuta la simulación salvo que se pida solo la interfaz.
    if not args.solo_gui:
        # Imprime los integrantes.
        print("Integrantes: " + " | ".join(INTEGRANTES))
        # Corre las operaciones.
        ejecutar_simulaciones()
    # Abre la interfaz salvo que se pida solo consola.
    if not args.solo_consola:
        # Lanza la ventana.
        abrir_interfaz()
    # Registra el cierre.
    logger.info("Aplicación finalizada.")
    # Código de salida correcto.
    return 0


# Solo se ejecuta si el archivo se corre directamente.
if __name__ == "__main__":
    # Termina con el código que devuelva main().
    sys.exit(main())
