# -*- coding: utf-8 -*-
"""Gestor con las listas internas de clientes, servicios y reservas (sin base de datos). (Roles 1 y 5)

Responsable: Nicolas David Ramirez Sanchez (@usuario3).
"""

# Clase de cliente.
from modelo.cliente import Cliente
# Excepciones propias del sistema.
from modelo.excepciones import (ClienteInvalidoError, DatoInvalidoError,
                                ReservaInvalidaError, ServicioNoDisponibleError)
# Logger compartido.
from modelo.registro import obtener_logger
# Clase de reserva.
from modelo.reserva import Reserva
# Clase base de servicios.
from modelo.servicios import Servicio

# Logger de este módulo.
logger = obtener_logger()


# Administra las colecciones en memoria y evita duplicados.
class GestorFJ:
    """Punto único de acceso a los datos del sistema; la interfaz solo usa esta clase."""

    # Constructor: crea las tres listas internas vacías.
    def __init__(self):
        # Lista privada de clientes.
        self.__clientes = []
        # Lista privada de servicios.
        self.__servicios = []
        # Lista privada de reservas.
        self.__reservas = []

    # Copia de solo lectura de los clientes.
    @property
    def clientes(self) -> tuple:
        """Clientes registrados."""
        # Se devuelve una tupla para impedir modificar la lista desde fuera.
        return tuple(self.__clientes)

    # Copia de solo lectura de los servicios.
    @property
    def servicios(self) -> tuple:
        """Servicios registrados."""
        # Se devuelve una tupla para impedir modificar la lista desde fuera.
        return tuple(self.__servicios)

    # Copia de solo lectura de las reservas.
    @property
    def reservas(self) -> tuple:
        """Reservas creadas."""
        # Se devuelve una tupla para impedir modificar la lista desde fuera.
        return tuple(self.__reservas)

    # Registra un cliente ya validado.
    def registrar_cliente(self, cliente: Cliente) -> None:
        """Agrega el cliente si el identificador y el documento no están repetidos."""
        # Solo se aceptan objetos Cliente.
        if not isinstance(cliente, Cliente):
            # Tipo incorrecto.
            raise ClienteInvalidoError("Solo se pueden registrar objetos Cliente.")
        # Recorre los clientes existentes buscando duplicados.
        for existente in self.__clientes:
            # Identificador repetido.
            if existente.identificador == cliente.identificador:
                # Registra y lanza.
                logger.error("Cliente duplicado (identificador %s).", cliente.identificador)
                raise ClienteInvalidoError(f"Ya existe un cliente con el identificador {cliente.identificador}.")
            # Documento repetido.
            if existente.documento == cliente.documento:
                # Registra y lanza.
                logger.error("Cliente duplicado (documento %s).", cliente.documento)
                raise ClienteInvalidoError(f"Ya existe un cliente con el documento {cliente.documento}.")
        # Agrega el cliente a la lista.
        self.__clientes.append(cliente)
        # Registra el evento.
        logger.info("Cliente %s registrado en el sistema.", cliente.identificador)

    # Registra un servicio ya validado.
    def registrar_servicio(self, servicio: Servicio) -> None:
        """Agrega el servicio si el identificador no está repetido."""
        # Solo se aceptan objetos Servicio.
        if not isinstance(servicio, Servicio):
            # Tipo incorrecto.
            raise ServicioNoDisponibleError("Solo se pueden registrar objetos Servicio.")
        # Busca un servicio con el mismo identificador.
        if any(s.identificador == servicio.identificador for s in self.__servicios):
            # Registra y lanza.
            logger.error("Servicio duplicado (%s).", servicio.identificador)
            raise DatoInvalidoError(f"Ya existe un servicio con el identificador {servicio.identificador}.")
        # Agrega el servicio a la lista.
        self.__servicios.append(servicio)
        # Registra el evento.
        logger.info("Servicio %s registrado en el sistema.", servicio.identificador)

    # Busca un cliente por identificador.
    def buscar_cliente(self, identificador: str) -> Cliente:
        """Devuelve el cliente o lanza ClienteInvalidoError si no existe."""
        # Recorre la lista.
        for cliente in self.__clientes:
            # Coincidencia exacta.
            if cliente.identificador == identificador:
                # Devuelve el cliente encontrado.
                return cliente
        # No se encontró.
        raise ClienteInvalidoError(f"No existe el cliente '{identificador}'.")

    # Busca un servicio por identificador.
    def buscar_servicio(self, identificador: str) -> Servicio:
        """Devuelve el servicio o lanza ServicioNoDisponibleError si no existe."""
        # Recorre la lista.
        for servicio in self.__servicios:
            # Coincidencia exacta.
            if servicio.identificador == identificador:
                # Devuelve el servicio encontrado.
                return servicio
        # No se encontró.
        raise ServicioNoDisponibleError(f"No existe el servicio '{identificador}'.")

    # Busca una reserva por identificador.
    def buscar_reserva(self, identificador: str) -> Reserva:
        """Devuelve la reserva o lanza ReservaInvalidaError si no existe."""
        # Recorre la lista.
        for reserva in self.__reservas:
            # Coincidencia exacta.
            if reserva.identificador == identificador:
                # Devuelve la reserva encontrada.
                return reserva
        # No se encontró.
        raise ReservaInvalidaError(f"No existe la reserva '{identificador}'.")

    # Crea una reserva a partir de identificadores.
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion, opciones: dict = None) -> Reserva:
        """Busca cliente y servicio, crea la reserva y la guarda (queda Pendiente)."""
        # Busca el cliente (lanza error si no existe).
        cliente = self.buscar_cliente(id_cliente)
        # Busca el servicio (lanza error si no existe).
        servicio = self.buscar_servicio(id_servicio)
        # Crea la reserva (valida duración y opciones).
        reserva = Reserva(cliente, servicio, duracion, opciones)
        # La guarda en la lista interna.
        self.__reservas.append(reserva)
        # Devuelve la reserva creada.
        return reserva

    # Cuenta las reservas por estado.
    def resumen_reservas(self) -> dict:
        """Devuelve un diccionario estado -> cantidad."""
        # Diccionario de conteo.
        conteo = {}
        # Recorre las reservas.
        for reserva in self.__reservas:
            # Suma uno al estado correspondiente.
            conteo[reserva.estado.value] = conteo.get(reserva.estado.value, 0) + 1
        # Devuelve el conteo.
        return conteo
