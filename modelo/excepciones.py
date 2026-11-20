# -*- coding: utf-8 -*-
"""Jerarquía de excepciones personalizadas de Software FJ. (Rol 2)"""


# Excepción base: todas las fallas controladas del sistema heredan de ella.
class ErrorSistema(Exception):
    """Falla controlada del sistema; permite capturar cualquier error propio con un solo except."""

    # Mensaje por defecto cuando no se entrega uno específico.
    mensaje_defecto = "Se produjo un error en el sistema."

    # Constructor: recibe un mensaje opcional.
    def __init__(self, mensaje=None):
        # Usa el mensaje recibido o, si no hay, el mensaje por defecto de la clase.
        super().__init__(mensaje or self.mensaje_defecto)


# Falla por datos con formato o valor incorrecto.
class DatoInvalidoError(ErrorSistema):
    """Un dato no cumple las validaciones (texto vacío, número negativo, etc.)."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "El dato recibido no es válido."


# Falla específica de los datos personales de un cliente.
class ClienteInvalidoError(DatoInvalidoError):
    """Los datos de un cliente (documento, nombre, correo, teléfono) son incorrectos."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "Los datos del cliente no son válidos."


# Falla cuando falta un parámetro obligatorio o llega uno desconocido.
class ParametroFaltanteError(DatoInvalidoError):
    """Falta un parámetro requerido o se envió uno que el servicio no soporta."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "Faltan parámetros o hay parámetros no soportados."


# Falla cuando un servicio no se puede crear o usar.
class ServicioNoDisponibleError(ErrorSistema):
    """El servicio está mal configurado, deshabilitado o no existe."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "El servicio no está disponible."


# Falla cuando una reserva no se puede crear o procesar.
class ReservaInvalidaError(ErrorSistema):
    """Intento de reserva incorrecto (cliente o servicio inválido, duración errónea)."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "La reserva no es válida."


# Falla cuando se pide una acción que el estado actual no permite.
class OperacionNoPermitidaError(ReservaInvalidaError):
    """Operación fuera de orden (confirmar sin procesar, cancelar dos veces, etc.)."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "La operación no está permitida en el estado actual."


# Falla cuando un cálculo de costos produce o recibe valores inconsistentes.
class CalculoInconsistenteError(ErrorSistema):
    """El cálculo de costos no se pudo completar de forma coherente."""

    # Mensaje por defecto de esta falla.
    mensaje_defecto = "El cálculo de costos es inconsistente."
