# -*- coding: utf-8 -*-
"""Clase abstracta Servicio y los tres servicios especializados. (Rol 4)"""

# abstractmethod: marca los métodos que cada servicio debe implementar.
from abc import abstractmethod

# Clase base de las entidades.
from modelo.entidad import Entidad
# Excepciones propias del sistema.
from modelo.excepciones import (CalculoInconsistenteError, DatoInvalidoError,
                                ParametroFaltanteError, ServicioNoDisponibleError)
# Logger compartido.
from modelo.registro import obtener_logger
# Validaciones reutilizables.
from modelo.validaciones import validar_entero_positivo, validar_numero, validar_texto

# Logger de este módulo.
logger = obtener_logger()


# Clase abstracta que define lo que todo servicio de Software FJ debe ofrecer.
class Servicio(Entidad):
    """Servicio con costo base. Las hijas sobrescriben cálculo, descripción y validación."""

    # Porcentaje de IVA usado en la variante "con impuesto".
    TASA_IVA = 19.0
    # Unidad en la que se mide la duración (las hijas la sobrescriben).
    unidad_duracion = "unidades"
    # Opciones extra que acepta cada servicio al calcular el costo (las hijas la sobrescriben).
    OPCIONES_VALIDAS = ()

    # Constructor: valida nombre y costo base.
    def __init__(self, identificador: str, nombre: str, costo_base: float):
        # Inicializa el identificador heredado.
        super().__init__(identificador)
        # Intenta validar los datos comunes a todos los servicios.
        try:
            # Guarda el nombre validado (atributo privado).
            self.__nombre = validar_texto(nombre, "nombre del servicio", 3)
            # Guarda el costo base validado (debe ser mayor que cero).
            self.__costo_base = float(validar_numero(costo_base, "costo base"))
        # Captura el error de validación.
        except ValueError as error:
            # Registra el rechazo del servicio.
            logger.error("Servicio %r rechazado: %s", identificador, error)
            # Encadenamiento hacia la excepción propia.
            raise ServicioNoDisponibleError(str(error)) from error
        # Todo servicio nuevo nace disponible.
        self.__disponible = True

    # Propiedad de solo lectura: nombre.
    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        # Devuelve el atributo privado.
        return self.__nombre

    # Propiedad de solo lectura: costo base.
    @property
    def costo_base(self) -> float:
        """Costo por unidad de duración (hora, día o sesión)."""
        # Devuelve el atributo privado.
        return self.__costo_base

    # Propiedad de solo lectura: disponibilidad.
    @property
    def disponible(self) -> bool:
        """Indica si el servicio puede reservarse."""
        # Devuelve el atributo privado.
        return self.__disponible

    # Marca el servicio como no disponible.
    def deshabilitar(self) -> None:
        """Impide nuevas reservas del servicio."""
        # Cambia el estado interno.
        self.__disponible = False
        # Registra el evento.
        logger.info("Servicio %s deshabilitado.", self.identificador)

    # Marca el servicio como disponible.
    def habilitar(self) -> None:
        """Permite de nuevo reservar el servicio."""
        # Cambia el estado interno.
        self.__disponible = True
        # Registra el evento.
        logger.info("Servicio %s habilitado.", self.identificador)

    # Lanza error si el servicio está deshabilitado.
    def _verificar_disponible(self) -> None:
        """Comprueba la disponibilidad antes de calcular o reservar."""
        # Si no está disponible, no se puede usar.
        if not self.__disponible:
            # Registra el intento y lanza la excepción.
            logger.warning("Intento de usar el servicio deshabilitado %s.", self.identificador)
            raise ServicioNoDisponibleError(f"El servicio '{self.__nombre}' no está disponible.")

    # Rechaza opciones que el servicio no conoce (parámetros no soportados).
    def _rechazar_opciones_desconocidas(self, opciones: dict) -> None:
        """Lanza ParametroFaltanteError si llega una opción no soportada."""
        # Busca las claves que no están en la lista de opciones válidas.
        desconocidas = [clave for clave in opciones if clave not in self.OPCIONES_VALIDAS]
        # Si hay alguna, se rechaza el cálculo.
        if desconocidas:
            # Lanza el error indicando cuáles opciones sobran.
            raise ParametroFaltanteError(
                f"Opciones no soportadas por {self.nombre}: {', '.join(desconocidas)}. "
                f"Opciones válidas: {', '.join(self.OPCIONES_VALIDAS) or 'ninguna'}."
            )

    # Aplica descuento e impuesto a un subtotal (lógica común a todas las hijas).
    def _aplicar_ajustes(self, subtotal: float, descuento: float, impuesto: float) -> float:
        """Resta el descuento (%), suma el impuesto (%) y redondea a dos decimales."""
        # Intenta validar los porcentajes.
        try:
            # El descuento debe ser un número entre 0 y 100.
            validar_numero(descuento, "descuento", permitir_cero=True)
            # El impuesto debe ser un número no negativo.
            validar_numero(impuesto, "impuesto", permitir_cero=True)
        # Captura el error de validación.
        except ValueError as error:
            # Encadenamiento hacia la excepción de cálculo.
            raise CalculoInconsistenteError(str(error)) from error
        # Un descuento mayor a 100% produciría costos negativos.
        if descuento > 100:
            # Cálculo incoherente.
            raise CalculoInconsistenteError("El descuento no puede superar el 100%.")
        # Un impuesto mayor a 100% se considera un error de digitación.
        if impuesto > 100:
            # Cálculo incoherente.
            raise CalculoInconsistenteError("El impuesto no puede superar el 100%.")
        # Subtotal después del descuento.
        con_descuento = subtotal * (1 - descuento / 100)
        # Total después del impuesto, redondeado a dos decimales.
        total = round(con_descuento * (1 + impuesto / 100), 2)
        # Verifica que el resultado sea coherente.
        if total < 0:
            # Un costo negativo nunca es válido.
            raise CalculoInconsistenteError("El cálculo produjo un costo negativo.")
        # Devuelve el total.
        return total

    # Método abstracto: cálculo base (sin impuesto ni descuento) = variante principal.
    @abstractmethod
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0, **opciones) -> float:
        """Cada servicio calcula su costo a su manera (polimorfismo)."""
        # Lo implementan las clases hijas.
        raise NotImplementedError

    # Método abstracto: validación de los parámetros propios del servicio.
    @abstractmethod
    def validar_parametros(self, **opciones) -> None:
        """Valida la configuración del servicio y las opciones de una reserva."""
        # Lo implementan las clases hijas.
        raise NotImplementedError

    # --- Variantes del cálculo (sobrecarga emulada en Python) ---------------------------
    # Python no tiene sobrecarga nativa; se emula con parámetros opcionales y con
    # variantes de nombre explícito que delegan en calcular_costo.

    # Variante 1: solo con impuesto (por defecto el IVA).
    def calcular_costo_con_impuesto(self, duracion, impuesto=None, **opciones) -> float:
        """Calcula el costo aplicando impuesto (IVA si no se indica otro porcentaje)."""
        # Si no se indicó impuesto se usa el IVA.
        tasa = self.TASA_IVA if impuesto is None else impuesto
        # Delegar en el cálculo principal sin descuento.
        return self.calcular_costo(duracion, 0.0, tasa, **opciones)

    # Variante 2: solo con descuento.
    def calcular_costo_con_descuento(self, duracion, descuento, **opciones) -> float:
        """Calcula el costo aplicando un descuento porcentual."""
        # Delegar en el cálculo principal sin impuesto.
        return self.calcular_costo(duracion, descuento, 0.0, **opciones)

    # Variante 3: descuento e impuesto juntos.
    def calcular_costo_completo(self, duracion, descuento, impuesto=None, **opciones) -> float:
        """Calcula el costo con descuento y con impuesto (IVA por defecto)."""
        # Si no se indicó impuesto se usa el IVA.
        tasa = self.TASA_IVA if impuesto is None else impuesto
        # Delegar en el cálculo principal.
        return self.calcular_costo(duracion, descuento, tasa, **opciones)


# ---------------------------------------------------------------------------------------
# Servicio 1: reserva de salas
# ---------------------------------------------------------------------------------------
class ReservaSala(Servicio):
    """Sala de reuniones o conferencias cobrada por hora."""

    # Unidad de duración de este servicio.
    unidad_duracion = "horas"
    # Opción extra permitida: número de personas que usarán la sala.
    OPCIONES_VALIDAS = ("personas",)

    # Constructor: costo por hora y capacidad máxima.
    def __init__(self, identificador: str, nombre: str, costo_base: float, capacidad: int):
        # Inicializa los datos comunes del servicio.
        super().__init__(identificador, nombre, costo_base)
        # Guarda la capacidad (atributo privado).
        self.__capacidad = capacidad
        # Valida la configuración propia de la sala.
        self.validar_parametros()

    # Propiedad de solo lectura: capacidad.
    @property
    def capacidad(self) -> int:
        """Número máximo de personas de la sala."""
        # Devuelve el atributo privado.
        return self.__capacidad

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, **opciones) -> None:
        """Verifica capacidad válida y, si se envía, que 'personas' quepa en la sala."""
        # Rechaza opciones desconocidas.
        self._rechazar_opciones_desconocidas(opciones)
        # Intenta validar la capacidad de la sala.
        try:
            # La capacidad debe ser un entero mayor que cero.
            validar_entero_positivo(self.__capacidad, "capacidad")
        # Captura el error de validación.
        except ValueError as error:
            # Registra y encadena hacia la excepción de servicio.
            logger.error("Sala %s con capacidad inválida: %s", self.identificador, error)
            raise ServicioNoDisponibleError(str(error)) from error
        # Si no se indicaron personas no hay más que validar.
        if "personas" not in opciones:
            # Fin de la validación.
            return
        # Intenta validar el número de personas.
        try:
            # Debe ser un entero mayor que cero.
            validar_entero_positivo(opciones["personas"], "personas")
        # Captura el error de validación.
        except ValueError as error:
            # Encadena hacia la excepción de dato inválido.
            raise DatoInvalidoError(str(error)) from error
        # Compara con la capacidad de la sala.
        if opciones["personas"] > self.__capacidad:
            # Registra y lanza: la sala no tiene espacio.
            logger.warning("Capacidad excedida en %s: %s > %s", self.identificador,
                           opciones["personas"], self.__capacidad)
            raise ServicioNoDisponibleError(
                f"La sala '{self.nombre}' admite {self.__capacidad} personas y se pidieron "
                f"{opciones['personas']}."
            )

    # Sobrescribe el cálculo del costo.
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0, **opciones) -> float:
        """Costo = tarifa por hora x horas, con descuento e impuesto opcionales."""
        # La sala debe estar habilitada.
        self._verificar_disponible()
        # Valida configuración y opciones.
        self.validar_parametros(**opciones)
        # Intenta validar la duración.
        try:
            # Las horas deben ser un número mayor que cero.
            validar_numero(duracion, "horas")
        # Captura el error de validación.
        except ValueError as error:
            # Encadenamiento hacia la excepción de cálculo.
            raise CalculoInconsistenteError(str(error)) from error
        # Subtotal = tarifa x horas.
        subtotal = self.costo_base * duracion
        # Aplica descuento e impuesto.
        return self._aplicar_ajustes(subtotal, descuento, impuesto)

    # Sobrescribe la descripción.
    def describir(self) -> str:
        """Describe la sala y su capacidad."""
        # Devuelve el texto descriptivo.
        return (f"Reserva de sala '{self.nombre}' (capacidad {self.__capacidad} personas, "
                f"${self.costo_base:,.2f} por hora)")


# ---------------------------------------------------------------------------------------
# Servicio 2: alquiler de equipos
# ---------------------------------------------------------------------------------------
class AlquilerEquipo(Servicio):
    """Equipo tecnológico alquilado por día."""

    # Unidad de duración de este servicio.
    unidad_duracion = "días"
    # Opción extra permitida: valor de un seguro adicional.
    OPCIONES_VALIDAS = ("seguro_adicional",)

    # Constructor: costo por día y serial del equipo.
    def __init__(self, identificador: str, nombre: str, costo_base: float, serial: str):
        # Inicializa los datos comunes del servicio.
        super().__init__(identificador, nombre, costo_base)
        # Guarda el serial (atributo privado).
        self.__serial = serial
        # Valida la configuración propia del equipo.
        self.validar_parametros()

    # Propiedad de solo lectura: serial.
    @property
    def serial(self) -> str:
        """Serial del equipo alquilado."""
        # Devuelve el atributo privado.
        return self.__serial

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, **opciones) -> None:
        """Verifica el serial y, si se envía, que el seguro adicional sea válido."""
        # Rechaza opciones desconocidas.
        self._rechazar_opciones_desconocidas(opciones)
        # Intenta validar el serial.
        try:
            # El serial debe tener al menos 3 caracteres.
            self.__serial = validar_texto(self.__serial, "serial del equipo", 3)
        # Captura el error de validación.
        except ValueError as error:
            # Registra y encadena hacia la excepción de servicio.
            logger.error("Equipo %s con serial inválido: %s", self.identificador, error)
            raise ServicioNoDisponibleError(str(error)) from error
        # Si se envió un seguro, se valida.
        if "seguro_adicional" in opciones:
            # Intenta validar el valor del seguro.
            try:
                # Debe ser un número mayor o igual que cero.
                validar_numero(opciones["seguro_adicional"], "seguro adicional", permitir_cero=True)
            # Captura el error de validación.
            except ValueError as error:
                # Encadena hacia la excepción de dato inválido.
                raise DatoInvalidoError(str(error)) from error

    # Sobrescribe el cálculo del costo.
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0, **opciones) -> float:
        """Costo = tarifa por día x días + seguro adicional, con ajustes opcionales."""
        # El equipo debe estar habilitado.
        self._verificar_disponible()
        # Valida configuración y opciones.
        self.validar_parametros(**opciones)
        # Intenta validar la duración.
        try:
            # Los días deben ser un número mayor que cero.
            validar_numero(duracion, "días")
        # Captura el error de validación.
        except ValueError as error:
            # Encadenamiento hacia la excepción de cálculo.
            raise CalculoInconsistenteError(str(error)) from error
        # Subtotal = tarifa x días + seguro (0 si no se indicó).
        subtotal = self.costo_base * duracion + opciones.get("seguro_adicional", 0.0)
        # Aplica descuento e impuesto.
        return self._aplicar_ajustes(subtotal, descuento, impuesto)

    # Sobrescribe la descripción.
    def describir(self) -> str:
        """Describe el equipo y su serial."""
        # Devuelve el texto descriptivo.
        return (f"Alquiler de equipo '{self.nombre}' (serial {self.__serial}, "
                f"${self.costo_base:,.2f} por día)")


# ---------------------------------------------------------------------------------------
# Servicio 3: asesorías especializadas
# ---------------------------------------------------------------------------------------
class Asesoria(Servicio):
    """Asesoría profesional cobrada por sesión."""

    # Unidad de duración de este servicio.
    unidad_duracion = "sesiones"
    # Opción extra permitida: marcar la asesoría como de alta complejidad (+25%).
    OPCIONES_VALIDAS = ("alta_complejidad",)
    # Recargo por alta complejidad.
    RECARGO_COMPLEJIDAD = 1.25

    # Constructor: costo por sesión y especialidad.
    def __init__(self, identificador: str, nombre: str, costo_base: float, especialidad: str):
        # Inicializa los datos comunes del servicio.
        super().__init__(identificador, nombre, costo_base)
        # Guarda la especialidad (atributo privado).
        self.__especialidad = especialidad
        # Valida la configuración propia de la asesoría.
        self.validar_parametros()

    # Propiedad de solo lectura: especialidad.
    @property
    def especialidad(self) -> str:
        """Área de la asesoría."""
        # Devuelve el atributo privado.
        return self.__especialidad

    # Sobrescribe la validación de parámetros.
    def validar_parametros(self, **opciones) -> None:
        """Verifica la especialidad y, si se envía, que 'alta_complejidad' sea booleano."""
        # Rechaza opciones desconocidas.
        self._rechazar_opciones_desconocidas(opciones)
        # Intenta validar la especialidad.
        try:
            # La especialidad debe tener al menos 3 caracteres.
            self.__especialidad = validar_texto(self.__especialidad, "especialidad", 3)
        # Captura el error de validación.
        except ValueError as error:
            # Registra y encadena hacia la excepción de servicio.
            logger.error("Asesoría %s con especialidad inválida: %s", self.identificador, error)
            raise ServicioNoDisponibleError(str(error)) from error
        # Si se envió la opción de complejidad, debe ser True o False.
        if "alta_complejidad" in opciones and not isinstance(opciones["alta_complejidad"], bool):
            # Dato inválido.
            raise DatoInvalidoError("La alta complejidad debe indicarse con True o False.")

    # Sobrescribe el cálculo del costo.
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0, **opciones) -> float:
        """Costo = tarifa por sesión x sesiones (+25% si es de alta complejidad)."""
        # La asesoría debe estar habilitada.
        self._verificar_disponible()
        # Valida configuración y opciones.
        self.validar_parametros(**opciones)
        # Intenta validar la duración.
        try:
            # Las sesiones deben ser un número mayor que cero.
            validar_numero(duracion, "sesiones")
        # Captura el error de validación.
        except ValueError as error:
            # Encadenamiento hacia la excepción de cálculo.
            raise CalculoInconsistenteError(str(error)) from error
        # Multiplicador según la complejidad.
        multiplicador = self.RECARGO_COMPLEJIDAD if opciones.get("alta_complejidad", False) else 1.0
        # Subtotal = tarifa x sesiones x multiplicador.
        subtotal = self.costo_base * duracion * multiplicador
        # Aplica descuento e impuesto.
        return self._aplicar_ajustes(subtotal, descuento, impuesto)

    # Sobrescribe la descripción.
    def describir(self) -> str:
        """Describe la asesoría y su especialidad."""
        # Devuelve el texto descriptivo.
        return (f"Asesoría en '{self.__especialidad}' - {self.nombre} "
                f"(${self.costo_base:,.2f} por sesión)")
