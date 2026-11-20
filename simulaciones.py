# -*- coding: utf-8 -*-
"""Simulación de 24 operaciones completas (válidas e inválidas) sobre el sistema. (Rol 5)

Responsable: Nicolas David Ramirez Sanchez (@usuario3).
"""

# datetime: fecha y hora de la ejecución.
import datetime

# Clases del modelo.
from modelo.cliente import Cliente
from modelo.excepciones import ErrorSistema
from modelo.gestor import GestorFJ
from modelo.registro import ARCHIVO_LOG, obtener_logger
from modelo.servicios import Asesoria, AlquilerEquipo, ReservaSala, Servicio

# Logger compartido.
logger = obtener_logger()

# Resultados esperados de cada operación.
OK = "ok"                # debe terminar bien
CONTROLADO = "controlado"  # debe fallar con una excepción propia, sin detener el programa


# Servicio de prueba con un bug a propósito, para demostrar el manejo de errores graves.
class ServicioDefectuoso(Servicio):
    """Servicio cuyo cálculo falla con ZeroDivisionError (error inesperado)."""

    # Sobrescribe el cálculo con un error intencional.
    def calcular_costo(self, duracion, descuento=0.0, impuesto=0.0, **opciones):
        # División por cero: simula un bug grave que no es un ErrorSistema.
        return self.costo_base / (duracion - duracion)

    # Sin parámetros propios que validar.
    def validar_parametros(self, **opciones):
        # No hace nada.
        return None

    # Descripción del servicio de prueba.
    def describir(self):
        # Texto descriptivo.
        return f"Servicio defectuoso '{self.nombre}' (solo para pruebas)"


# Agrupa las operaciones para compartir el mismo gestor.
class Simulacion:
    """Cada método op_XX es una operación completa; devuelve un mensaje si salió bien."""

    # Constructor: recibe el gestor con las listas internas.
    def __init__(self, gestor: GestorFJ):
        # Guarda el gestor.
        self.g = gestor
        # Identificador de la reserva de la operación 12 (se usa luego para cancelarla).
        self.id_reserva_sala = None

    # ----- Clientes ---------------------------------------------------------------------
    def op_01(self):
        # Cliente válido 1.
        c = Cliente("CLI-01", "Andrés Tobar", "1012345678", "andres.tobar@unad.edu.co", "3101234567")
        # Lo registra.
        self.g.registrar_cliente(c)
        # Mensaje de éxito.
        return c.describir()

    def op_02(self):
        # Cliente válido 2.
        c = Cliente("CLI-02", "Livan Vargas", "1098765432", "livan.vargas@unad.edu.co", "3159876543")
        # Lo registra.
        self.g.registrar_cliente(c)
        # Mensaje de éxito.
        return c.describir()

    def op_03(self):
        # Cliente válido 3.
        c = Cliente("CLI-03", "Carlos Gómez", "80123456", "carlos.gomez@gmail.com", "3201112233")
        # Lo registra.
        self.g.registrar_cliente(c)
        # Mensaje de éxito.
        return c.describir()

    def op_04(self):
        # Documento con letras: debe fallar.
        Cliente("CLI-04", "María Pérez", "ABC12345", "maria@gmail.com", "3209876543")

    def op_05(self):
        # Correo sin dominio: debe fallar.
        Cliente("CLI-05", "Pedro Díaz", "1023456789", "pedro@correo", "3001234567")

    def op_06(self):
        # Documento repetido con otro identificador: lo rechaza el gestor.
        c = Cliente("CLI-06", "Andrés Duplicado", "1012345678", "otro@gmail.com", "3101112233")
        # Intenta registrarlo.
        self.g.registrar_cliente(c)

    # ----- Servicios --------------------------------------------------------------------
    def op_07(self):
        # Sala válida.
        s = ReservaSala("SRV-01", "Sala de Juntas Principal", 60000.0, 20)
        # La registra.
        self.g.registrar_servicio(s)
        # Mensaje de éxito.
        return s.describir()

    def op_08(self):
        # Costo negativo: debe fallar.
        ReservaSala("SRV-02", "Sala Beta", -5000.0, 10)

    def op_09(self):
        # Equipo válido.
        s = AlquilerEquipo("SRV-03", "Servidor de Alto Rendimiento", 150000.0, "SRV-DELL-9922")
        # Lo registra.
        self.g.registrar_servicio(s)
        # Mensaje de éxito.
        return s.describir()

    def op_10(self):
        # Asesoría válida.
        s = Asesoria("SRV-04", "Asesoría en Arquitectura de Software", 100000.0, "Ingeniería de Software")
        # La registra.
        self.g.registrar_servicio(s)
        # Mensaje de éxito.
        return s.describir()

    def op_11(self):
        # Capacidad cero: debe fallar.
        ReservaSala("SRV-05", "Sala Gamma", 40000.0, 0)

    # ----- Reservas exitosas ------------------------------------------------------------
    def op_12(self):
        # Reserva de sala con descuento, IVA y número de personas.
        r = self.g.crear_reserva("CLI-01", "SRV-01", 3,
                                 {"descuento": 15.0, "impuesto": 19.0, "personas": 12})
        # Procesa (calcula el costo).
        r.procesar()
        # Confirma.
        r.confirmar()
        # Guarda su identificador para las operaciones de cancelación.
        self.id_reserva_sala = r.identificador
        # Mensaje de éxito.
        return r.describir()

    def op_13(self):
        # Reserva de equipo con seguro adicional.
        r = self.g.crear_reserva("CLI-02", "SRV-03", 4, {"seguro_adicional": 30000.0})
        # Procesa.
        r.procesar()
        # Confirma.
        r.confirmar()
        # Mensaje de éxito.
        return r.describir()

    def op_14(self):
        # Reserva de asesoría de alta complejidad.
        r = self.g.crear_reserva("CLI-03", "SRV-04", 2, {"alta_complejidad": True})
        # Procesa.
        r.procesar()
        # Confirma.
        r.confirmar()
        # Muestra además las variantes "sobrecargadas" del cálculo.
        s = r.servicio
        # Variante con impuesto.
        con_iva = s.calcular_costo_con_impuesto(2, alta_complejidad=True)
        # Variante con descuento.
        con_desc = s.calcular_costo_con_descuento(2, 10, alta_complejidad=True)
        # Variante completa.
        completo = s.calcular_costo_completo(2, 10, alta_complejidad=True)
        # Mensaje de éxito con las variantes.
        return (f"{r.describir()}\n        Variantes: con IVA ${con_iva:,.2f} | con 10% desc. "
                f"${con_desc:,.2f} | desc.+IVA ${completo:,.2f}")

    # ----- Reservas fallidas ------------------------------------------------------------
    def op_15(self):
        # Duración cero: falla al crear la reserva.
        self.g.crear_reserva("CLI-01", "SRV-04", 0, {"alta_complejidad": True})

    def op_16(self):
        # 50 personas en una sala de 20: falla al procesar.
        r = self.g.crear_reserva("CLI-01", "SRV-01", 2, {"personas": 50})
        # Procesa (lanza el error).
        r.procesar()

    def op_17(self):
        # Deshabilita el equipo y luego intenta reservarlo.
        self.g.buscar_servicio("SRV-03").deshabilitar()
        # Crea la reserva (se permite crear, falla al procesar).
        r = self.g.crear_reserva("CLI-02", "SRV-03", 1)
        # Procesa (lanza el error).
        r.procesar()

    def op_18(self):
        # Parámetro que el servicio no soporta.
        r = self.g.crear_reserva("CLI-03", "SRV-04", 1, {"color": "azul"})
        # Procesa (lanza el error).
        r.procesar()

    def op_19(self):
        # Cliente que no existe.
        self.g.crear_reserva("CLI-99", "SRV-01", 1)

    def op_20(self):
        # Descuento de 150%: cálculo inconsistente.
        r = self.g.crear_reserva("CLI-01", "SRV-01", 1, {"descuento": 150.0})
        # Procesa (lanza el error).
        r.procesar()

    def op_21(self):
        # Registra un servicio defectuoso y lo reserva: error grave inesperado.
        self.g.registrar_servicio(ServicioDefectuoso("SRV-99", "Servicio de Prueba", 1000.0))
        # Crea la reserva.
        r = self.g.crear_reserva("CLI-01", "SRV-99", 2)
        # Procesa: ZeroDivisionError -> ReservaInvalidaError (encadenado).
        r.procesar()

    # ----- Confirmar y cancelar ---------------------------------------------------------
    def op_22(self):
        # Confirmar una reserva que nunca se procesó.
        r = self.g.crear_reserva("CLI-02", "SRV-01", 1)
        # Lanza OperacionNoPermitidaError.
        r.confirmar()

    def op_23(self):
        # Cancela la primera reserva confirmada.
        r = self.g.buscar_reserva(self.id_reserva_sala)
        # Cancela.
        r.cancelar()
        # Mensaje de éxito.
        return r.describir()

    def op_24(self):
        # Cancelar de nuevo la misma reserva.
        self.g.buscar_reserva(self.id_reserva_sala).cancelar()


# Lista de operaciones: (método, título, resultado esperado).
OPERACIONES = [
    ("op_01", "Registro válido de cliente 1", OK),
    ("op_02", "Registro válido de cliente 2", OK),
    ("op_03", "Registro válido de cliente 3", OK),
    ("op_04", "Cliente inválido: documento con letras", CONTROLADO),
    ("op_05", "Cliente inválido: correo sin dominio", CONTROLADO),
    ("op_06", "Cliente inválido: documento duplicado", CONTROLADO),
    ("op_07", "Servicio válido: sala de juntas", OK),
    ("op_08", "Servicio inválido: costo negativo", CONTROLADO),
    ("op_09", "Servicio válido: alquiler de servidor", OK),
    ("op_10", "Servicio válido: asesoría especializada", OK),
    ("op_11", "Servicio inválido: capacidad cero", CONTROLADO),
    ("op_12", "Reserva exitosa de sala (descuento + IVA)", OK),
    ("op_13", "Reserva exitosa de equipo (seguro adicional)", OK),
    ("op_14", "Reserva exitosa de asesoría (+ variantes de cálculo)", OK),
    ("op_15", "Reserva fallida: duración cero", CONTROLADO),
    ("op_16", "Reserva fallida: capacidad de sala excedida", CONTROLADO),
    ("op_17", "Reserva fallida: servicio no disponible", CONTROLADO),
    ("op_18", "Reserva fallida: parámetro no soportado", CONTROLADO),
    ("op_19", "Reserva fallida: cliente inexistente", CONTROLADO),
    ("op_20", "Reserva fallida: descuento de 150%", CONTROLADO),
    ("op_21", "Error grave inesperado (ZeroDivisionError encadenado)", CONTROLADO),
    ("op_22", "Confirmar una reserva sin procesar", CONTROLADO),
    ("op_23", "Cancelación válida de reserva", OK),
    ("op_24", "Cancelación repetida (no permitida)", CONTROLADO),
]


# Ejecuta todas las operaciones sin que ninguna detenga el programa.
def ejecutar_simulaciones(gestor: GestorFJ = None, imprimir: bool = True) -> dict:
    """Corre las 24 operaciones y devuelve un resumen (también escribe en el log)."""
    # Usa el gestor recibido o crea uno nuevo.
    gestor = gestor or GestorFJ()
    # Objeto que contiene las operaciones.
    simulacion = Simulacion(gestor)
    # Lista de resultados.
    resultados = []

    # Función de salida: imprime solo si se pidió.
    def mostrar(texto=""):
        # Imprime en consola cuando corresponde.
        if imprimir:
            print(texto)

    # Encabezado de la simulación.
    mostrar("=" * 72)
    mostrar("  SIMULACIÓN DEL SISTEMA - SOFTWARE FJ (FASE 4)")
    mostrar("  Fecha y hora: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    mostrar("=" * 72)
    # Marca el inicio en el log.
    logger.info("===== INICIO DE LA SIMULACIÓN (%d operaciones) =====", len(OPERACIONES))

    # Recorre cada operación con su número.
    for numero, (nombre_metodo, titulo, esperado) in enumerate(OPERACIONES, start=1):
        # Imprime el título.
        mostrar(f"\n--- Operación {numero:02d}: {titulo} ---")
        # Registra el inicio de la operación.
        logger.info("Operación %02d iniciada: %s", numero, titulo)
        # Resultado por defecto.
        obtenido = "error inesperado"
        # Ejecuta la operación dentro de un bloque try/except/else/finally.
        try:
            # Llama al método de la operación.
            mensaje = getattr(simulacion, nombre_metodo)()
        # Errores propios del sistema: son los fallos controlados.
        except ErrorSistema as error:
            # Resultado: error controlado.
            obtenido = CONTROLADO
            # Registra la advertencia.
            logger.warning("Operación %02d: error controlado (%s): %s", numero,
                           type(error).__name__, error)
            # Muestra el error.
            mostrar(f"  [CONTROLADO] {type(error).__name__}: {error}")
            # Si hay una causa encadenada (raise ... from ...), también se muestra.
            if error.__cause__ is not None:
                # Muestra la causa original.
                mostrar(f"  Causa original: {type(error.__cause__).__name__}: {error.__cause__}")
        # Cualquier otro error: se registra y el programa continúa.
        except Exception as error:
            # Resultado: error inesperado.
            obtenido = "error inesperado"
            # Registra con la traza completa.
            logger.exception("Operación %02d: error inesperado.", numero)
            # Muestra el error.
            mostrar(f"  [INESPERADO] {type(error).__name__}: {error}")
        # Solo si no hubo errores.
        else:
            # Resultado: éxito.
            obtenido = OK
            # Muestra el mensaje de éxito.
            mostrar(f"  [OK] {mensaje}")
        # Siempre se ejecuta.
        finally:
            # Registra el fin de la operación.
            logger.info("Operación %02d finalizada con resultado: %s.", numero, obtenido)
            # Guarda el resultado.
            resultados.append((numero, titulo, esperado, obtenido))

    # Cuenta las operaciones que dieron lo esperado.
    cumplidas = sum(1 for _, _, esperado, obtenido in resultados if esperado == obtenido)
    # Cuenta las exitosas.
    exitosas = sum(1 for r in resultados if r[3] == OK)
    # Cuenta los errores controlados.
    controlados = sum(1 for r in resultados if r[3] == CONTROLADO)
    # Arma el resumen.
    resumen = {
        "operaciones": len(resultados),
        "exitosas": exitosas,
        "errores_controlados": controlados,
        "segun_lo_esperado": cumplidas,
        "clientes": len(gestor.clientes),
        "servicios": len(gestor.servicios),
        "reservas": gestor.resumen_reservas(),
    }
    # Imprime el resumen.
    mostrar("\n" + "=" * 72)
    mostrar("  RESUMEN DE LA SIMULACIÓN")
    mostrar("=" * 72)
    mostrar(f"  Operaciones ejecutadas : {resumen['operaciones']}")
    mostrar(f"  Exitosas               : {exitosas}")
    mostrar(f"  Errores controlados    : {controlados}")
    mostrar(f"  Resultado esperado     : {cumplidas} de {resumen['operaciones']}")
    mostrar(f"  Clientes / Servicios   : {resumen['clientes']} / {resumen['servicios']}")
    mostrar(f"  Reservas por estado    : {resumen['reservas']}")
    mostrar(f"  Log generado en        : {ARCHIVO_LOG}")
    mostrar("=" * 72)
    # Marca el fin en el log.
    logger.info("===== FIN DE LA SIMULACIÓN: %d de %d según lo esperado =====", cumplidas, len(resultados))
    # Devuelve el resumen.
    return resumen
