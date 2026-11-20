# Guía de GitHub para el grupo (3 integrantes)

El código ya está terminado y probado, pero **la rúbrica (criterio 4, 30 puntos) evalúa el trabajo
colaborativo en GitHub**: ramas por integrante, commits frecuentes en días distintos, pull requests
revisados e issues. Esa evidencia solo la pueden generar ustedes con sus propias cuentas. Cada
integrante debe subir **sus** archivos desde **su** cuenta; no suban todo desde una sola.

## 1. Arranque (responsable del repositorio, rol 1)
1. Repositorio del grupo: `Reto_4_sistema_de_gestion` → https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion (público, con README y `.gitignore` de Python).
2. Settings → Collaborators: invitar a los otros dos integrantes (la invitación vence en 7 días).
3. Settings → Branches: proteger `main` (exigir pull request antes de fusionar).
4. Projects: crear el tablero con las columnas *Por hacer, En curso, En revisión, Hecho*.
5. Subir `.gitignore`, `.github/pull_request_template.md` y la carpeta `docs/` en un primer commit.
6. Cada integrante publica en el foro su usuario de GitHub, su rol y su disponibilidad.

## 2. Ramas, archivos y revisiones

| Integrante | Rama | Sube estos archivos | Revisa el PR de |
|---|---|---|---|
| Roles 2 + 3 (Andrés) | `feature/excepciones-clientes-andres` | `modelo/__init__.py`, `excepciones.py`, `registro.py`, `validaciones.py`, `entidad.py`, `cliente.py` | Roles 1 + 5 |
| Rol 4 (Livan) | `feature/servicios-livan` | `modelo/servicios.py` | Roles 2 + 3 |
| Roles 1 + 5 (Nicolas David Ramirez Sanchez) | `feature/integracion-reservas-nicolas` | `modelo/reserva.py`, `modelo/gestor.py`, `simulaciones.py`, `gui.py`, `main.py`, `README.md`, `logs/sistema.log` | Rol 4 |

Orden recomendado de fusión en `main` (cada módulo depende del anterior): primero excepciones/log/entidad/cliente,
luego servicios, y al final reservas, simulaciones, interfaz y `main.py`.

## 3. Ciclo de trabajo (repetirlo varias veces)
```bash
git clone https://github.com/nikolachas08-source/Reto_4_sistema_de_gestion.git
cd Reto_4_sistema_de_gestion
git checkout -b feature/tu-rama            # una sola vez
# ... trabaja un archivo o una función ...
python main.py --solo-consola              # prueba antes de subir
git add modelo/cliente.py
git commit -m "feat(clientes): valida formato de correo"
git push origin feature/tu-rama
# En GitHub: Create Pull Request -> "Closes #N" -> pedir revisión al compañero asignado
```
Prefijos de commit: `feat`, `fix`, `docs`, `test`, `refactor`. **Nadie fusiona su propio PR ni hace commit directo a `main`.**

Metas mínimas por integrante (plan de trabajo): 5 o más commits en 3 o más días distintos, 1 rama,
1 o más PR fusionados, 1 o más revisiones con comentario, 2 o más issues asignados y cerrados,
2 reportes de avance en el foro. Para llegar a 5 commits con sentido, hagan commits pequeños
(por ejemplo: la jerarquía de excepciones, el log, la validación de correo, la de teléfono, etc.).

## 4. Issues sugeridos (crear y asignar)
**Andrés (roles 2 + 3):** #1 Jerarquía de excepciones personalizadas · #2 Configurar `logs/sistema.log` ·
#3 Clase abstracta `Entidad` · #4 Clase `Cliente` con validaciones · #5 Redistribución del grupo a 3 integrantes (constancia).
**Livan (rol 4):** #6 Clase abstracta `Servicio` · #7 `ReservaSala` · #8 `AlquilerEquipo` y `Asesoria` ·
#9 Variantes de cálculo con impuesto y descuento.
**Nicolas David Ramirez Sanchez (roles 1 + 5):** #10 Clase `Reserva` (procesar, confirmar, cancelar) · #11 `GestorFJ` · #12 Simulaciones (10 o más) ·
#13 Interfaz Tkinter · #14 `main.py`, README e informe PDF.

## 5. Entrega
1. Las capturas con fecha y hora de la consola, las cuatro pestañas de la interfaz y el `sistema.log` ya están en
   `docs/capturas/`. Cada integrante debe agregar además capturas del historial de commits, sus pull requests y el
   tablero desde su propia cuenta.
2. Los datos del grupo (nombre del tercer integrante, número 599 y enlace del repositorio) ya están completos en
   `README.md`, `main.py` y `docs/generar_informe.py`. Si cambia el enlace, ejecute
   `python docs/generar_informe.py` para regenerar el PDF.
3. Subir **un solo PDF** al foro/entorno de entrega (portada, introducción, enlace del repositorio, conclusiones y
   referencias APA), aprobado por todos en el foro antes del cierre (22 de noviembre).
