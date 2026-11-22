# Diario del equipo --- EGC 2026/2027

**Asignatura:** Evolución y Gestión de la Configuración (EGC)  
**Curso académico:** 2026/2027  
**Tutor asignado:** Jesús Moreno

> NOTA: Tener en cuenta que las enmiendas que se vayan realizando a lo largo de la vida del proyecto aplican SIN RETROACTIVIDAD, de modo que el proceder que haya sido anterior a una enmienda no se considera incorrecto. Cada enmienda cita la parte que deja de ser válida y desarrolla la nueva forma de proceder. Por tanto, el equipo debe estar atento a las enmiendas y aplicarlas a partir de su fecha de publicación.


# Actas de reuniones


# Registro de decisiones importantes

## [19/11/2026]

### Despliegue continuo (CD) y protección de `main`

El equipo mantiene dos entornos desplegados en Render y utiliza Enzonic como servicio de base de datos.

- **Preproducción (PRE)**. Se despliega desde `trunk`. [Abrir preproducción](https://pre-classical-hub.onrender.com)
- **Producción (PROD)**. Se despliega desde `main`. [Abrir producción](https://prod-classical-hub.onrender.com)

El repositorio tiene un *ruleset* que reserva a @mouady la posibilidad de actualizar `main`.

### Enmiendas al acta fundacional

| Enmienda | Texto del acta | Acuerdo vigente |
| --- | --- | --- |
| **Integración continua (CI)** | **Texto sustituido** ([acta fundacional, apartado 5, p. 3](ACTA_EGC_definitiva.pdf#page=3))<br><br>«Configuraremos un flujo de integración continua (CI) que ejecute automáticamente las pruebas al abrir o actualizar una pull request hacia trunk o main. Solo podremos integrar los cambios en estas ramas si todas las pruebas se superan.» | El repositorio tiene un *ruleset* que exige superar tres comprobaciones de CI para integrar cambios en `trunk`. Las comprobaciones obligatorias son `Commits Syntax Checker`, `Pytest` y `Python Lint`. |
| **Formato de rama** | **Texto anterior** ([acta fundacional, apartado 5, p. 2](ACTA_EGC_definitiva.pdf#page=2))<br><br>«El trabajo se organizará mediante ramas de tarea, cada una asociada a un propósito concreto, como una funcionalidad, corrección, mejora de documentación o refactorización. Se evitarán las ramas personales: el nombre de cada rama deberá describir el cambio que contiene.» | La enmienda concreta el formato del nombre de las ramas de tarea.<br><br>Las ramas tienen el formato `tipo/nombre`, donde `tipo` es `feat`, `docs`, `style`, `refactor`, `test` o `fix`. El nombre debe ser descriptivo y en minúsculas, con palabras separadas por guiones. Un ejemplo es `feat/gestor-de-usuarios`. |
| **Flujo de trabajo en GitHub Projects** | **Texto sustituido** ([acta fundacional, apartado 4, p. 2](ACTA_EGC_definitiva.pdf#page=2))<br><br>«Vamos a tener 3 columnas en un Project (Todo, In Progress, In Review, Done). Cuando una issue pasa a In Review necesita ser revisada por un miembro del equipo antes de darla por cerrada. Cuando una issue in review no resulta aprobada se pasa esa issue de nuevo a in progress.» | El tablero del proyecto se organiza en cinco columnas.<br><br>1. **Backlog**. Aquí se añaden las tareas nuevas.<br>2. **In Progress**. Aquí se sitúan las tareas en curso y las que vuelven de revisión para incorporar correcciones.<br>3. **In Review**. La tarea queda pendiente de revisión. Quien la revisa deja un comentario en la issue con el resultado. Si la revisión es favorable, se añade la etiqueta `revisado`. Si requiere cambios, la issue vuelve a **In Progress**. Los autores de la issue son responsables de fusionar sus ramas aprobadas en `trunk` y mover la issue a **PRE (trunk)**.<br>4. **PRE (trunk)**. @mouady valida los cambios en preproducción. Si superan la validación, añade la etiqueta `READY FOR PRO`. Si encuentra algo que corregir, se abre una issue vinculada a la original para resolverlo, y la original permanece en **PRE (trunk)**.<br>5. **Done**. Cuando los cambios de la tarea se integran en `main`, la issue pasa a **Done** y se cierra. |
| **Uso de etiquetas** | **Texto sustituido** ([acta fundacional, apartado 4, p. 2](ACTA_EGC_definitiva.pdf#page=2))<br><br>«Vamos a evitar el uso de las etiquetas ya que en nuestra opinión dan una falsa sensación de seguridad y terminan perdiendo su sentido semántico.» | Las etiquetas complementan el estado del tablero y permiten identificar qué validaciones ha superado una tarea. `revisado` indica que la revisión fue favorable y `READY FOR PRO` indica que los cambios se validaron en preproducción y están listos para pasar a producción. El resultado de la revisión queda documentado en el comentario de la issue. `EPIC` hace referencia a una tarea que agrupa otras tareas relacionadas. |
| **Plantillas para issues de GitHub** | **Acuerdo que se amplía** ([acta fundacional, apartado 4, p. 2](ACTA_EGC_definitiva.pdf#page=2))<br><br>«Gestión de tareas e incidencias: GitHub Issues.» | El equipo adopta dos plantillas para que las tareas nuevas lleguen a **Backlog** con la información necesaria para planificar su resolución y revisarlas. La unica excepción son las issues marcadas como `EPIC`, que pueden ser más generales y no requieren criterios de aceptación verificables.<br><br>- [Tarea de desarrollo](../.github/ISSUE_TEMPLATE/desarrollo.md). Recoge la necesidad, el alcance y los criterios de aceptación verificables que servirán para revisar el cambio.<br>- [Incidencia o arreglo](../.github/ISSUE_TEMPLATE/incidencia.md). Recoge el entorno, los pasos de reproducción, el comportamiento observado y el esperado.<br><br>La distinción entre tareas de desarrollo e incidencias sigue el material docente y facilita la trazabilidad desde el informe hasta la validación. [Gestión de tareas e incidencias](https://egc.us.es/static/uploads/EGC_2026-27_T5_gestiondetareaseincidencias_light.pdf) · [Reto de gestión y depuración de una incidencia](https://egc.us.es/cursos/egc-20262027/documento/reto-de-gestion-y-depuracion-de-una-incidencia) |

## [22/11/2026]

### Tipo de dato del hub: partituras MusicXML

El equipo adapta uvlhub para que, además de modelos UVL, admita partituras de música clásica en formato MusicXML. Esta decisión concreta el tipo de dato que exige el WI-newdataset recogido en el [acta fundacional, apartado 2, p. 1](ACTA_EGC_definitiva.pdf#page=1).

- **Formato aceptado**. Ficheros `.musicxml` sin comprimir. El formato comprimido `.mxl` queda como posible ampliación posterior.
- **Validación**. Los ficheros se validan contra el XSD oficial de MusicXML con `lxml`. Se descarta `music21` como dependencia inicial por su peso en el despliegue de Render.
- **Metadatos y métricas**. Se extraen del propio fichero el título de la obra, el compositor, la tonalidad, el compás, el número de partes y el número de compases.
- **Previsualización**. La página del dataset muestra la partitura renderizada con OpenSheetMusicDisplay.
- **UVL se mantiene**. UVL sigue funcionando como uno de los tipos de dataset, sin regresiones.

El equipo descartó otros formatos por estos motivos:

- **MIDI**. Es binario, describe la interpretación y no la notación, y apenas tiene metadatos.
- **ABC**. Está orientado a música folk y se queda corto para obras orquestales.
- **MEI**. Es más complejo y tiene menos herramientas disponibles.
