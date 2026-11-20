# -*- coding: utf-8 -*-
"""Genera el PDF de entrega de la Fase 4. Edite las constantes y ejecute: python docs/generar_informe.py

Grupo colaborativo: 599.
"""

# Path: rutas del archivo de salida.
from pathlib import Path
# Componentes de ReportLab para armar el documento.
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ======================= DATOS A COMPLETAR ANTES DE ENTREGAR =======================
GRUPO = "599"                                    # número del grupo colaborativo
URL_REPOSITORIO = "https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion"   # enlace real del repositorio
INTEGRANTES = [
    "Andrés Ovidio Tobar Ladino",
    "Livan Jussete Vargas Perdomo",
    "Nicolas David Ramirez Sanchez",
]
# ===================================================================================

# Archivo de salida junto a este script.
SALIDA = Path(__file__).resolve().parent / "Informe_Fase4_Software_FJ.pdf"

# Estilos de texto.
base = getSampleStyleSheet()
titulo = ParagraphStyle("t", parent=base["Title"], fontSize=18, leading=24, alignment=TA_CENTER)
centro = ParagraphStyle("c", parent=base["Normal"], fontSize=12, leading=18, alignment=TA_CENTER)
h1 = ParagraphStyle("h1", parent=base["Heading1"], fontSize=15, spaceAfter=10, textColor=colors.HexColor("#0B3C6F"))
cuerpo = ParagraphStyle("b", parent=base["Normal"], fontSize=11, leading=16, alignment=TA_JUSTIFY, spaceAfter=8)
ref = ParagraphStyle("r", parent=cuerpo, leftIndent=28, firstLineIndent=-28, alignment=0)


# Pie de página con el número de página.
def pie(canvas, doc):
    # Guarda el estado gráfico.
    canvas.saveState()
    # Fuente pequeña.
    canvas.setFont("Helvetica", 9)
    # Escribe el número de página (no en la portada).
    if doc.page > 1:
        canvas.drawCentredString(letter[0] / 2, 1.2 * cm, str(doc.page))
    # Restaura el estado.
    canvas.restoreState()


# Historia: lista de elementos del documento.
h = []
# ------------------------------- Portada -------------------------------
h += [Spacer(1, 2.5 * cm),
      Paragraph("Universidad Nacional Abierta y a Distancia - UNAD", centro),
      Paragraph("Escuela de Ciencias Básicas, Tecnología e Ingeniería - ECBTI", centro),
      Paragraph("Programa de Ingeniería de Sistemas", centro),
      Spacer(1, 2 * cm),
      Paragraph("Fase 4 - Prácticas simuladas", titulo),
      Paragraph("Sistema integral de gestión de clientes, servicios y reservas - Software FJ", titulo),
      Spacer(1, 1.5 * cm),
      Paragraph("Curso: Programación (213023)", centro),
      Paragraph(f"Grupo colaborativo: {GRUPO}", centro),
      Spacer(1, 1.2 * cm),
      Paragraph("<b>Integrantes</b>", centro)]
# Un párrafo por integrante.
h += [Paragraph(nombre, centro) for nombre in INTEGRANTES]
h += [Spacer(1, 1.2 * cm),
      Paragraph("<b>Tutor</b>", centro),
      Paragraph("Frank Rodríguez Achury", centro),
      Spacer(1, 1.5 * cm),
      Paragraph("22 de noviembre de 2026", centro),
      PageBreak()]

# ----------------------------- Introducción -----------------------------
h += [Paragraph("Introducción", h1),
      Paragraph("Este trabajo presenta el desarrollo de un sistema integral orientado a objetos para la empresa "
                "ficticia Software FJ, que ofrece reservas de salas, alquiler de equipos y asesorías "
                "especializadas. La aplicación gestiona clientes, servicios y reservas sin utilizar bases de "
                "datos: toda la información se maneja mediante objetos y listas en memoria, y los archivos se "
                "emplean únicamente para registrar eventos y errores.", cuerpo),
      Paragraph("El objetivo central de la fase es implementar el manejo de excepciones para lograr "
                "aplicaciones estables y robustas. Por ello el sistema define una jerarquía de excepciones "
                "personalizadas, usa bloques try/except, try/except/else y try/except/finally, encadena "
                "excepciones con la instrucción raise ... from ... y registra cada error en el archivo "
                "logs/sistema.log, de modo que el programa continúa funcionando aun ante datos inválidos, "
                "parámetros faltantes, servicios no disponibles, reservas incorrectas o cálculos inconsistentes.", cuerpo),
      Paragraph("La arquitectura aplica abstracción (clases abstractas Entidad y Servicio), herencia (tres "
                "servicios especializados), polimorfismo (cálculo de costos y descripción propios de cada "
                "servicio), encapsulación (atributos privados con propiedades de solo lectura) y variantes del "
                "cálculo de costos con impuesto, descuento y parámetros opcionales. Se incluye una interfaz "
                "gráfica en Tkinter y una simulación de 24 operaciones válidas e inválidas.", cuerpo),
      Paragraph("El trabajo se organizó de forma colaborativa en GitHub siguiendo el plan de trabajo de la fase: "
                "un responsable por módulo, una rama por integrante, issues asignados y pull requests revisados "
                "por un compañero. Como el grupo está conformado por tres integrantes activos, se aplicó la "
                "redistribución de roles prevista en dicho plan.", cuerpo),
      PageBreak()]

# ------------------------- Enlace del repositorio -------------------------
h += [Paragraph("Enlace del repositorio en GitHub", h1),
      Paragraph(f'<link href="{URL_REPOSITORIO}" color="blue">{URL_REPOSITORIO}</link>', cuerpo),
      Paragraph("El repositorio contiene el código fuente (main.py, gui.py, simulaciones.py y la carpeta modelo), "
                "el archivo logs/sistema.log generado al ejecutar, el README con la distribución de roles y la "
                "declaración de uso de inteligencia artificial, y el historial de commits, ramas, issues y pull "
                "requests que evidencia el aporte de cada integrante.", cuerpo),
      Spacer(1, 0.3 * cm)]
# Tabla de roles.
filas = [["Integrante", "Roles", "Módulos"],
         [INTEGRANTES[0], "2 + 3", "excepciones, registro, validaciones, entidad, cliente"],
         [INTEGRANTES[1], "4", "servicios"],
         [INTEGRANTES[2], "1 + 5", "main, gui, gestor, reserva, simulaciones, README"]]
# Estilo de la tabla.
tabla = Table([[Paragraph(str(c), ParagraphStyle("tc", parent=base["Normal"], fontSize=9.5, leading=12)) for c in f]
               for f in filas], colWidths=[5.5 * cm, 2 * cm, 9 * cm])
tabla.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E6F5")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
h += [tabla, PageBreak()]

# ------------------------------ Conclusiones ------------------------------
h += [Paragraph("Conclusiones", h1),
      Paragraph("Separar los errores en una jerarquía de excepciones propia (ErrorSistema y sus hijas) permitió "
                "distinguir con claridad un dato inválido, un servicio no disponible, una reserva incorrecta o un "
                "cálculo inconsistente, y capturar cualquier falla controlada con un solo except sin ocultar "
                "los errores inesperados.", cuerpo),
      Paragraph("El encadenamiento de excepciones conserva la causa original (por ejemplo, el ValueError de una "
                "validación o un ZeroDivisionError inesperado) dentro de la excepción propia, lo que facilita "
                "diagnosticar el problema en el log sin exponer detalles técnicos al usuario.", cuerpo),
      Paragraph("La simulación de 24 operaciones demostró que el sistema continúa funcionando después de cada "
                "falla: diez operaciones terminaron correctamente y catorce fueron rechazadas de forma "
                "controlada, todas con su registro en logs/sistema.log, incluyendo un error grave simulado.", cuerpo),
      Paragraph("Python no ofrece sobrecarga de métodos como otros lenguajes; se resolvió con parámetros "
                "opcionales y métodos de variante (con impuesto, con descuento y completo) que delegan en un "
                "único cálculo polimórfico, manteniendo el código sin duplicaciones.", cuerpo),
      Paragraph("Dividir el sistema en módulos con un responsable, una rama y revisiones cruzadas permitió "
                "trabajar en paralelo y dejar evidencia del aporte de cada integrante en el historial de GitHub, "
                "lo que reforzó la responsabilidad individual dentro del trabajo colaborativo.", cuerpo),
      PageBreak()]

# ------------------------------- Referencias -------------------------------
h += [Paragraph("Referencias", h1)]
referencias = [
    "Anthropic. (2026). <i>Claude</i> [Modelo de lenguaje de gran tamaño]. https://claude.ai",
    "Cuevas Álvarez, A. (2016). <i>Python 3: curso práctico</i>. RA-MA Editorial. "
    "https://elibro-net.bibliotecavirtual.unad.edu.co/es/ereader/unad/106404?page=373",
    "Romano, F., Baka, B., &amp; Phillips, D. (2019). <i>Getting started with Python: Understand key data "
    "structures and use Python in object-oriented programming</i>. Packt Publishing.",
    "Silva, F. D. (2025). <i>Basics of using GitHub</i> [Objeto virtual de información]. Repositorio "
    "Institucional UNAD. https://repository.unad.edu.co/handle/10596/75882",
    "Van Rossum, G., &amp; Drake Jr, F. L. (2024). <i>El tutorial de Python</i>. Python Software Foundation. "
    "https://docs.python.org/es/3.12/tutorial/errors.html",
    "Zambrano, J. P. (2025). <i>Introducción al uso de GitHub</i> [Objeto virtual de información]. Repositorio "
    "Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876",
]
h += [Paragraph(r, ref) for r in referencias]

# Construye el PDF.
SimpleDocTemplate(str(SALIDA), pagesize=letter, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                  topMargin=2.5 * cm, bottomMargin=2.2 * cm,
                  title="Fase 4 - Software FJ", author=", ".join(INTEGRANTES)).build(h, onFirstPage=pie, onLaterPages=pie)
# Informa dónde quedó.
print("PDF generado en", SALIDA)
