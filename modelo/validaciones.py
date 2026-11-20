# -*- coding: utf-8 -*-
"""Funciones auxiliares de validación reutilizadas por todas las clases. (Roles 2 y 3)"""

# math: permite comprobar que un número es finito (no inf ni nan).
import math
# re: expresiones regulares para validar formatos.
import re

# Nombres: letras (con tildes y ñ), espacios, apóstrofes, puntos y guiones.
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]*$")
# Correo: texto@dominio.ext sin espacios.
PATRON_CORREO = re.compile(r"^[\w.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


# Valida que un valor sea texto con una longitud mínima.
def validar_texto(valor, campo, longitud_minima=1):
    """Devuelve el texto sin espacios sobrantes o lanza ValueError."""
    # Rechaza lo que no sea str o quede demasiado corto tras quitar espacios.
    if not isinstance(valor, str) or len(valor.strip()) < longitud_minima:
        # Lanza el error con el nombre del campo para dar un mensaje claro.
        raise ValueError(f"El campo '{campo}' debe tener al menos {longitud_minima} carácter(es).")
    # Devuelve el texto limpio.
    return valor.strip()


# Valida que un valor sea un número real finito y, opcionalmente, positivo.
def validar_numero(valor, campo, permitir_cero=False):
    """Devuelve el número validado o lanza ValueError."""
    # Los booleanos son subclase de int en Python; se rechazan explícitamente.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        # El valor no es numérico.
        raise ValueError(f"El campo '{campo}' debe ser un número.")
    # Rechaza infinito y NaN.
    if not math.isfinite(valor):
        # Valor no finito.
        raise ValueError(f"El campo '{campo}' debe ser un número finito.")
    # Caso en que el cero está permitido: solo se rechazan negativos.
    if permitir_cero:
        # Valida que no sea negativo.
        if valor < 0:
            # Número negativo.
            raise ValueError(f"El campo '{campo}' no puede ser negativo.")
    # Caso en que el cero no está permitido: debe ser estrictamente positivo.
    elif valor <= 0:
        # Número cero o negativo.
        raise ValueError(f"El campo '{campo}' debe ser mayor que cero.")
    # Devuelve el valor ya validado.
    return valor


# Valida que un valor sea un entero (no bool) mayor que cero.
def validar_entero_positivo(valor, campo):
    """Devuelve el entero validado o lanza ValueError."""
    # Rechaza bool y todo lo que no sea int.
    if isinstance(valor, bool) or not isinstance(valor, int):
        # No es entero.
        raise ValueError(f"El campo '{campo}' debe ser un número entero.")
    # Debe ser mayor que cero.
    if valor <= 0:
        # Entero no positivo.
        raise ValueError(f"El campo '{campo}' debe ser mayor que cero.")
    # Devuelve el entero.
    return valor
