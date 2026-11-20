# -*- coding: utf-8 -*-
"""Clase abstracta que representa las entidades generales del sistema. (Rol 3)"""

# ABC y abstractmethod: permiten definir clases y métodos abstractos.
from abc import ABC, abstractmethod

# Excepciones propias del sistema.
from modelo.excepciones import DatoInvalidoError
# Logger compartido.
from modelo.registro import obtener_logger
# Validación de texto.
from modelo.validaciones import validar_texto

# Logger de este módulo.
logger = obtener_logger()


# Clase abstracta: no se puede instanciar directamente.
class Entidad(ABC):
    """Base común de Cliente, Servicio y Reserva: todas tienen identificador y se describen."""

    # Constructor: valida y guarda el identificador.
    def __init__(self, identificador: str):
        # Intenta validar el identificador (mínimo 3 caracteres).
        try:
            # Guarda el identificador en un atributo privado (encapsulación).
            self.__identificador = validar_texto(identificador, "identificador", 3)
        # Captura el ValueError de la validación.
        except ValueError as error:
            # Registra el fallo en el log.
            logger.error("Identificador inválido %r: %s", identificador, error)
            # Encadenamiento: lanza la excepción propia conservando la causa original.
            raise DatoInvalidoError("No fue posible crear la entidad: " + str(error)) from error

    # Propiedad de solo lectura para consultar el identificador.
    @property
    def identificador(self) -> str:
        """Permite leer el identificador sin poder modificarlo."""
        # Devuelve el valor privado.
        return self.__identificador

    # Método abstracto: cada subclase debe describirse a sí misma.
    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        # El cuerpo vacío es intencional: lo implementan las clases hijas.
        raise NotImplementedError
