# -*- coding: utf-8 -*-
"""Clase Reserva: integra cliente, servicio, duración y estado. (Rol 5)

Responsable: Nicolas David Ramirez Sanchez (@usuario3).
"""

# Enum: estados cerrados de una reserva.
from enum import Enum
# count: generador de números consecutivos para los identificadores.
from itertools import count

# Clase base de las entidades.
from modelo.entidad import Entidad
# Cliente de la reserva.
from modelo.cliente import Cliente
# Excepciones propias del sistema.
from modelo.excepciones import (ErrorSistema, OperacionNoPermitidaError,
                                ParametroFaltanteError, ReservaInvalidaError,
                                ServicioNoDisponibleError)
# Logger compartido.
from modelo.registro import obtener_logger
# Servicio de la reserva.
from modelo.servicios import Servicio
# Validación numérica.
from modelo.validaciones import validar_numero

# Logger de este módulo.
logger = obtener_logger()


# Estados posibles de una reserva.
class EstadoReserva(Enum):
    """Ciclo de vida: Pendiente -> Procesada -> Confirmada (o Cancelada / Fallida)."""

    # La reserva se creó pero aún no se calcula su costo.
    PENDIENTE = "Pendiente"
    # El costo se calculó correctamente; falta confirmarla.
    PROCESADA = "Procesada"
    # El cliente confirmó la reserva.
    CONFIRMADA = "Confirmada"
    # La reserva fue cancelada.
    CANCELADA = "Cancelada"
    # El procesamiento falló por un error controlado.
    FALLIDA = "Fallida"
    # El procesamiento falló por un error inesperado.
    ERROR_CRITICO = "Error crítico"


# Reserva de un servicio por parte de un cliente.
class Reserva(Entidad):
    """Reserva con confirmar(), cancelar() y procesar(), todas con manejo de excepciones."""

    # Generador de consecutivos (compartido por todas las reservas).
    _consecutivo = count(2001)

    # Constructor: valida todo antes de crear el objeto.
    def __init__(self, cliente: Cliente, servicio: Servicio, duracion, opciones: dict = None):
        # El cliente debe ser un objeto Cliente.
        if not isinstance(cliente, Cliente):
            # Registra y lanza el error de reserva.
            logger.error("Reserva rechazada: cliente inválido (%r).", cliente)
            raise ReservaInvalidaError("La reserva requiere un cliente válido.")
        # El servicio debe ser un objeto Servicio.
        if not isinstance(servicio, Servicio):
            # Registra y lanza el error de reserva.
            logger.error("Reserva rechazada: servicio inválido (%r).", servicio)
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")
        # Intenta validar la duración.
        try:
            # La duración debe ser un número mayor que cero.
            validar_numero(duracion, "duración")
        # Captura el error de validación.
        except ValueError as error:
            # Registra el rechazo.
            logger.error("Reserva rechazada por duración inválida: %s", error)
            # Encadenamiento hacia la excepción de reserva.
            raise ReservaInvalidaError(f"Duración inválida: {error}") from error
        # Las opciones deben ser un diccionario (o None).
        if opciones is not None and not isinstance(opciones, dict):
            # Registra y lanza el error de reserva.
            logger.error("Reserva rechazada: opciones con tipo incorrecto.")
            raise ReservaInvalidaError("Las opciones de costo deben enviarse en un diccionario.")
        # Solo si todo es válido se consume un consecutivo y se crea la entidad.
        super().__init__(f"RES-{next(Reserva._consecutivo)}")
        # Guarda el cliente (privado).
        self.__cliente = cliente
        # Guarda el servicio (privado).
        self.__servicio = servicio
        # Guarda la duración (privado).
        self.__duracion = duracion
        # Guarda una copia de las opciones para que nadie las modifique desde fuera.
        self.__opciones = dict(opciones or {})
        # Estado inicial.
        self.__estado = EstadoReserva.PENDIENTE
        # Costo pendiente de calcular.
        self.__costo_total = 0.0
        # Registra la creación.
        logger.info("Reserva %s creada (cliente %s, servicio %s).", self.identificador,
                    cliente.identificador, servicio.identificador)

    # Propiedad de solo lectura: cliente.
    @property
    def cliente(self) -> Cliente:
        """Cliente que reserva."""
        # Devuelve el atributo privado.
        return self.__cliente

    # Propiedad de solo lectura: servicio.
    @property
    def servicio(self) -> Servicio:
        """Servicio reservado."""
        # Devuelve el atributo privado.
        return self.__servicio

    # Propiedad de solo lectura: duración.
    @property
    def duracion(self):
        """Duración reservada (horas, días o sesiones según el servicio)."""
        # Devuelve el atributo privado.
        return self.__duracion

    # Propiedad de solo lectura: estado.
    @property
    def estado(self) -> EstadoReserva:
        """Estado actual de la reserva."""
        # Devuelve el atributo privado.
        return self.__estado

    # Propiedad de solo lectura: costo total.
    @property
    def costo_total(self) -> float:
        """Costo calculado (0 mientras no se procese)."""
        # Devuelve el atributo privado.
        return self.__costo_total

    # Procesa la reserva: valida y calcula el costo.
    def procesar(self) -> float:
        """Calcula el costo con try/except/else/finally. Relanza los errores ya registrados."""
        # Registra el inicio del procesamiento.
        logger.info("Procesando la reserva %s.", self.identificador)
        # Bloque principal: puede fallar de varias formas.
        try:
            # Solo se procesa una reserva pendiente.
            if self.__estado is not EstadoReserva.PENDIENTE:
                # Operación fuera de orden.
                raise OperacionNoPermitidaError(
                    f"No se puede procesar una reserva en estado {self.__estado.value}.")
            # El servicio debe seguir disponible.
            if not self.__servicio.disponible:
                # Servicio deshabilitado.
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.__servicio.nombre}' no está disponible.")
            # Cálculo polimórfico: cada servicio aplica su propia fórmula.
            costo = self.__servicio.calcular_costo(self.__duracion, **self.__opciones)
        # Error de orden: no cambia el estado de la reserva.
        except OperacionNoPermitidaError as error:
            # Registra la advertencia.
            logger.warning("Reserva %s: %s", self.identificador, error)
            # Relanza la misma excepción.
            raise
        # Error de parámetros mal enviados a la función de cálculo.
        except TypeError as error:
            # La reserva queda fallida.
            self.__estado = EstadoReserva.FALLIDA
            # Registra el error con su traza.
            logger.error("Reserva %s con parámetros incorrectos: %s", self.identificador, error)
            # Encadenamiento: se conserva el TypeError original como causa.
            raise ParametroFaltanteError("Parámetros incorrectos para el servicio.") from error
        # Cualquier otro error controlado del sistema.
        except ErrorSistema as error:
            # La reserva queda fallida.
            self.__estado = EstadoReserva.FALLIDA
            # Registra la advertencia.
            logger.warning("Reserva %s fallida: %s", self.identificador, error)
            # Relanza la excepción propia.
            raise
        # Error inesperado (un bug o una falla grave).
        except Exception as error:
            # La reserva queda en error crítico.
            self.__estado = EstadoReserva.ERROR_CRITICO
            # Registra el error con la traza completa.
            logger.exception("Error crítico procesando la reserva %s.", self.identificador)
            # Encadenamiento: se conserva el error original como causa.
            raise ReservaInvalidaError(
                f"Falla grave al procesar la reserva {self.identificador}.") from error
        # Se ejecuta solo si el bloque try terminó sin errores.
        else:
            # Guarda el costo calculado.
            self.__costo_total = costo
            # La reserva pasa a procesada.
            self.__estado = EstadoReserva.PROCESADA
            # Registra el éxito.
            logger.info("Reserva %s procesada. Total: $%.2f", self.identificador, costo)
            # Devuelve el costo.
            return costo
        # Se ejecuta siempre, con o sin error.
        finally:
            # Registra el cierre del ciclo con el estado final.
            logger.info("Cierre del procesamiento de %s. Estado: %s.",
                        self.identificador, self.__estado.value)

    # Confirma una reserva ya procesada.
    def confirmar(self) -> None:
        """Pasa la reserva de Procesada a Confirmada."""
        # Solo se confirma lo que ya se procesó.
        if self.__estado is not EstadoReserva.PROCESADA:
            # Registra el intento inválido.
            logger.warning("Confirmación rechazada en %s (estado %s).", self.identificador,
                           self.__estado.value)
            # Lanza el error de operación no permitida.
            raise OperacionNoPermitidaError(
                f"Solo se puede confirmar una reserva procesada (estado actual: {self.__estado.value}).")
        # Cambia el estado.
        self.__estado = EstadoReserva.CONFIRMADA
        # Registra el evento.
        logger.info("Reserva %s confirmada.", self.identificador)

    # Cancela la reserva.
    def cancelar(self) -> None:
        """Cancela una reserva que aún no esté cancelada ni haya fallado."""
        # Estados desde los cuales no se puede cancelar.
        no_cancelables = (EstadoReserva.CANCELADA, EstadoReserva.FALLIDA,
                          EstadoReserva.ERROR_CRITICO)
        # Verifica el estado actual.
        if self.__estado in no_cancelables:
            # Registra el intento inválido.
            logger.warning("Cancelación rechazada en %s (estado %s).", self.identificador,
                           self.__estado.value)
            # Lanza el error de operación no permitida.
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado {self.__estado.value}.")
        # Cambia el estado.
        self.__estado = EstadoReserva.CANCELADA
        # Registra el evento.
        logger.info("Reserva %s cancelada.", self.identificador)

    # Implementación del método abstracto de Entidad.
    def describir(self) -> str:
        """Resume la reserva."""
        # Devuelve una línea con todos los datos relevantes.
        return (f"Reserva [{self.identificador}] {self.__cliente.nombre} -> "
                f"{self.__servicio.nombre} x {self.__duracion} {self.__servicio.unidad_duracion} "
                f"| {self.__estado.value} | ${self.__costo_total:,.2f}")
