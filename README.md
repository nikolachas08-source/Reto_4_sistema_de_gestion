# Software FJ – Sistema integral de gestión de clientes, servicios y reservas

**Grupo colaborativo: 599**

**Repositorio:** https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion

Curso **Programación 213023** · UNAD · Fase 4 – Prácticas simuladas · Tutor: Frank Rodríguez Achury

Aplicación orientada a objetos en Python, **sin base de datos**, que gestiona clientes, servicios
(salas, equipos, asesorías) y reservas de la empresa *Software FJ*. Aplica abstracción, herencia,
polimorfismo, encapsulación y manejo avanzado de excepciones: **ningún error detiene el programa**
y todo queda registrado en `logs/sistema.log`.

## Integrantes y roles

El plan de trabajo prevé 5 roles. Como el grupo tiene **3 integrantes activos**, se aplicó la
redistribución prevista en el plan (el rol 1 absorbe el rol 5 y el rol 2 absorbe el rol 3):

| Integrante | Usuario GitHub | Roles | Rama | Módulos | Revisa el PR de |
|---|---|---|---|---|---|
| Andrés Ovidio Tobar Ladino | `@por-confirmar` | 2 + 3: Excepciones, log, entidad y clientes | `feature/excepciones-clientes-andres` | `excepciones.py`, `registro.py`, `validaciones.py`, `entidad.py`, `cliente.py` | Integrador (roles 1 + 5) |
| Livan Jussete Vargas Perdomo | `@por-confirmar` | 4: Servicios | `feature/servicios-livan` | `servicios.py` | Roles 2 + 3 |
| Nicolas David Ramirez Sanchez | `@nikolachas08-source` | 1 + 5: Integración, interfaz, reservas y simulaciones | `feature/integracion-reservas-nicolas` | `main.py`, `gui.py`, `gestor.py`, `reserva.py`, `simulaciones.py`, `README.md` | Rol 4 |

> Los usuarios `@por-confirmar` deben reemplazarse por las cuentas reales de esos dos integrantes
> cuando se confirmen en el foro. La redistribución de roles (3 integrantes activos para 5 roles)
> quedó registrada en el README y en la guía de GitHub.

## Cómo ejecutar

Requisitos: Python 3.10 o superior (con Tkinter; viene incluido en Windows y macOS, en Linux:
`sudo apt install python3-tk`). No hay dependencias externas.

```bash
python main.py                  # simulación en consola + interfaz gráfica
python main.py --solo-consola   # solo las 24 operaciones simuladas
python main.py --solo-gui       # solo la interfaz Tkinter
```

Si no hay entorno gráfico, `main.py` lo informa y termina sin errores después de la simulación.

## Estructura del repositorio

```
Reto_4_sistema_de_gestion/
├── README.md
├── .gitignore
├── main.py              # punto de entrada
├── gui.py               # interfaz Tkinter en inglés (solo llama a las clases, sin reglas de negocio)
├── simulaciones.py      # 24 operaciones válidas e inválidas
├── modelo/
│   ├── excepciones.py   # jerarquía ErrorSistema y sus hijas
│   ├── registro.py      # configuración del log
│   ├── validaciones.py  # funciones de validación reutilizables
│   ├── entidad.py       # clase abstracta Entidad
│   ├── cliente.py       # Cliente (atributos privados, validaciones)
│   ├── servicios.py     # Servicio (abstracta) + ReservaSala, AlquilerEquipo, Asesoria
│   ├── reserva.py       # Reserva y EstadoReserva
│   └── gestor.py        # listas internas en memoria (clientes, servicios, reservas)
├── logs/sistema.log     # se genera al ejecutar
└── docs/                # guía de GitHub, evidencia de la simulación y capturas
```

Respecto a la estructura sugerida en el plan se agregaron `modelo/validaciones.py` y
`modelo/gestor.py` para no repetir validaciones y para que la interfaz y las simulaciones compartan
las listas internas sin poner reglas de negocio en `gui.py`.

## Acuerdo de interfaces

| Clase | Dueño | Qué pueden usar los demás |
|---|---|---|
| `ErrorSistema` y sus hijas | Rol 2 | `DatoInvalidoError`, `ClienteInvalidoError`, `ParametroFaltanteError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`, `CalculoInconsistenteError` |
| `Entidad` (abstracta) | Rol 3 | `identificador` y el método abstracto `describir()` |
| `Cliente` | Rol 3 | Constructor que valida; propiedades de solo lectura; `actualizar_contacto()` |
| `Servicio` + 3 hijas | Rol 4 | `calcular_costo(...)`, `describir()`, `validar_parametros(...)`, `habilitar()/deshabilitar()` |
| `Reserva` | Rol 5 | `procesar()`, `confirmar()`, `cancelar()` y `estado` |
| `GestorFJ` | Roles 1 y 5 | `registrar_cliente/servicio`, `crear_reserva`, búsquedas y listas de solo lectura |
| `SoftwareFJApp` (Tkinter) | Rol 1 | Solo llama a las clases anteriores |

## Cómo se cumple cada requisito

| Requisito del anexo | Dónde está |
|---|---|
| Clase abstracta de entidades | `Entidad` (`modelo/entidad.py`) |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados (`__nombre`…), propiedades de solo lectura, validación de nombre, documento, correo y teléfono |
| Servicio abstracto + 3 servicios, polimorfismo y métodos sobrescritos | `Servicio`, `ReservaSala`, `AlquilerEquipo`, `Asesoria`: cada una sobrescribe `calcular_costo`, `describir` y `validar_parametros` |
| Reserva con cliente, servicio, duración y estado | `Reserva` con `procesar()`, `confirmar()`, `cancelar()` y `EstadoReserva` |
| Métodos sobrecargados | Python no tiene sobrecarga nativa; se emula con parámetros opcionales y variantes: `calcular_costo(duración, descuento=0, impuesto=0, **opciones)`, `calcular_costo_con_impuesto`, `calcular_costo_con_descuento`, `calcular_costo_completo` |
| Excepciones personalizadas | `modelo/excepciones.py` |
| `try/except`, `try/except/else`, `try/except/finally` | `Reserva.procesar()` (try/except/else/finally) y el ejecutor de `simulaciones.py` |
| Encadenamiento `raise … from …` | `Cliente`, `Servicio`, `Reserva`, `Entidad`, `gui.to_number` |
| Archivo de log con errores y eventos | `logs/sistema.log` (`modelo/registro.py`) |
| Sin base de datos | Solo listas en memoria (`GestorFJ`); el único archivo es el log |
| Mínimo 10 operaciones válidas e inválidas | 24 en `simulaciones.py` (10 exitosas y 14 con error controlado) |
| El sistema sigue funcionando ante errores graves | Operación 21: un `ZeroDivisionError` inesperado se encadena a `ReservaInvalidaError`, queda en el log y la ejecución continúa |

## Operaciones simuladas

Clientes válidos (3) e inválidos (documento con letras, correo sin dominio, documento duplicado);
servicios válidos (sala, equipo, asesoría) e inválidos (costo negativo, capacidad cero); reservas
exitosas con descuento, IVA, seguro y alta complejidad; reservas fallidas (duración cero,
capacidad excedida, servicio no disponible, parámetro no soportado, cliente inexistente, descuento
mayor a 100 %); error grave inesperado; confirmar sin procesar; cancelación válida y repetida.
La salida completa de una ejecución está en `docs/evidencia_simulacion.txt`.

## Declaración de uso de inteligencia artificial

Se usó **Claude (Anthropic)** para revisar el código inicial del grupo (`Untitled-1.py`),
reorganizarlo en los módulos del plan de trabajo, completar la interfaz gráfica, las simulaciones y
la documentación. El grupo revisó, ejecutó y probó el resultado y es responsable de poder explicarlo
en una sustentación. *(Ajusten esta sección a lo que realmente haya hecho cada integrante.)*

## Flujo de trabajo en GitHub

El repositorio del grupo es https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion

```bash
git clone https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion.git
cd Reto_4_sistema_de_gestion
python main.py --solo-consola
```

Ver `docs/GUIA_GITHUB.md`: ramas por integrante, commits pequeños, pull requests revisados por un
compañero, issues asignados y metas mínimas de la rúbrica.

## Evidencias

Las capturas con fecha y hora de la consola, la interfaz y el archivo de log están en
`docs/capturas/`. La salida completa de la simulación está en `docs/evidencia_simulacion.txt`.
