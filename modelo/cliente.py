# -*- coding: utf-8 -*-
"""Clase Cliente con atributos privados y validaciones robustas. (Rol 3)"""

# Clase base abstracta.
from modelo.entidad import Entidad
# Excepción específica de clientes.
from modelo.excepciones import ClienteInvalidoError
# Logger compartido.
from modelo.registro import obtener_logger
# Validaciones reutilizables.
from modelo.validaciones import PATRON_CORREO, PATRON_NOMBRE, validar_texto

# Logger de este módulo.
logger = obtener_logger()


# Función interna: valida el nombre y devuelve el valor limpio.
def _validar_nombre(valor):
    # Primero exige texto de al menos 3 caracteres.
    texto = validar_texto(valor, "nombre", 3)
    # Luego exige que solo tenga letras y signos de nombre.
    if not PATRON_NOMBRE.match(texto):
        # Nombre con números o símbolos.
        raise ValueError("El campo 'nombre' solo admite letras, espacios, apóstrofes y guiones.")
    # Devuelve el nombre limpio.
    return texto


# Función interna: valida el documento (solo dígitos, 7 a 12).
def _validar_documento(valor):
    # Debe ser texto formado solo por dígitos y con longitud permitida.
    if not isinstance(valor, str) or not valor.strip().isdigit() or not 7 <= len(valor.strip()) <= 12:
        # Documento incorrecto.
        raise ValueError("El documento debe tener entre 7 y 12 dígitos numéricos.")
    # Devuelve el documento sin espacios.
    return valor.strip()


# Función interna: valida el correo electrónico.
def _validar_correo(valor):
    # Debe ser texto con formato usuario@dominio.ext.
    if not isinstance(valor, str) or not PATRON_CORREO.match(valor.strip()):
        # Correo incorrecto.
        raise ValueError("El correo electrónico no tiene un formato válido.")
    # Devuelve el correo en minúsculas y sin espacios.
    return valor.strip().lower()


# Función interna: valida el teléfono (solo dígitos, 7 a 15).
def _validar_telefono(valor):
    # Debe ser texto formado solo por dígitos y con longitud permitida.
    if not isinstance(valor, str) or not valor.strip().isdigit() or not 7 <= len(valor.strip()) <= 15:
        # Teléfono incorrecto.
        raise ValueError("El teléfono debe tener entre 7 y 15 dígitos numéricos.")
    # Devuelve el teléfono sin espacios.
    return valor.strip()


# Cliente registrado en Software FJ.
class Cliente(Entidad):
    """Cliente con datos personales encapsulados: se validan al crear y se leen por propiedades."""

    # Constructor: valida todos los datos antes de guardarlos.
    def __init__(self, identificador: str, nombre: str, documento: str,
                 correo: str, telefono: str):
        # Inicializa el identificador heredado (puede lanzar DatoInvalidoError).
        super().__init__(identificador)
        # Valida los cuatro datos personales dentro de un solo bloque try.
        try:
            # Guarda el nombre validado en un atributo privado.
            self.__nombre = _validar_nombre(nombre)
            # Guarda el documento validado.
            self.__documento = _validar_documento(documento)
            # Guarda el correo validado.
            self.__correo = _validar_correo(correo)
            # Guarda el teléfono validado.
            self.__telefono = _validar_telefono(telefono)
        # Captura cualquier ValueError de las validaciones.
        except ValueError as error:
            # Registra el rechazo del cliente.
            logger.error("Cliente %r rechazado: %s", identificador, error)
            # Encadenamiento: lanza la excepción de cliente conservando la causa.
            raise ClienteInvalidoError(str(error)) from error
        # Registra la creación exitosa.
        logger.info("Cliente %s creado correctamente.", self.identificador)

    # Propiedad de solo lectura: nombre.
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        # Devuelve el atributo privado.
        return self.__nombre

    # Propiedad de solo lectura: documento.
    @property
    def documento(self) -> str:
        """Número de documento del cliente."""
        # Devuelve el atributo privado.
        return self.__documento

    # Propiedad de solo lectura: correo.
    @property
    def correo(self) -> str:
        """Correo electrónico del cliente."""
        # Devuelve el atributo privado.
        return self.__correo

    # Propiedad de solo lectura: teléfono.
    @property
    def telefono(self) -> str:
        """Teléfono del cliente."""
        # Devuelve el atributo privado.
        return self.__telefono

    # Actualiza correo y teléfono de forma atómica (o cambian ambos o ninguno).
    def actualizar_contacto(self, correo: str, telefono: str) -> None:
        """Cambia los datos de contacto solo si ambos son válidos."""
        # Intenta validar ambos valores antes de modificar nada.
        try:
            # Valida el nuevo correo.
            nuevo_correo = _validar_correo(correo)
            # Valida el nuevo teléfono.
            nuevo_telefono = _validar_telefono(telefono)
        # Captura el error de validación.
        except ValueError as error:
            # Registra el rechazo.
            logger.error("Actualización de contacto rechazada para %s: %s", self.identificador, error)
            # Encadenamiento hacia la excepción propia.
            raise ClienteInvalidoError(str(error)) from error
        # Solo si todo fue válido se reemplazan los datos.
        self.__correo = nuevo_correo
        # Reemplaza el teléfono.
        self.__telefono = nuevo_telefono
        # Registra el evento.
        logger.info("Contacto del cliente %s actualizado.", self.identificador)

    # Implementación del método abstracto de Entidad.
    def describir(self) -> str:
        """Resume los datos principales del cliente."""
        # Devuelve una línea con identificador, nombre, documento y correo.
        return (f"Cliente [{self.identificador}] {self.__nombre} - "
                f"Doc: {self.__documento} - {self.__correo}")
