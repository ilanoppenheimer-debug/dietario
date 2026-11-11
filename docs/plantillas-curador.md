# Dietario · Plantillas y lógica de armado de fichas

Documento de conocimiento para el proyecto "Curador de Dietario". Contiene **estructura y reglas, no contenido clínico**. Toda cifra o recomendación se obtiene de los documentos primarios del conocimiento.

Versión 3.0 · noviembre 2026 · Novedades v3: búsqueda con Drive primero, núcleo de fuentes y ventanas de años (sección 13). v2: condición para el paciente (9), tema clínico (10), calculadora (11), bloques (12), nombres de sección para el selector.

---

## 1. Links

| Recurso | URL | Uso |
|---|---|---|
| App (prototipo) | https://dietario.vercel.app/ | Ver cómo se presenta cada tipo de contenido |
| Condición paciente ejemplo | https://dietario.vercel.app/salud/diabetes.html | Formato "Mi salud" |
| Tema clínico ejemplo | https://dietario.vercel.app/clinica/diabetes.html | Formato tema profesional (requiere código) |
| Calculadoras | https://dietario.vercel.app/clinica/calculadoras.html | Formato de calculadora (requiere código) |
| Ficha ejemplo DASH | https://dietario.vercel.app/dietas/dash.html | Referencia **visual y de formato**, no de evidencia |
| Ficha ejemplo FODMAP | https://dietario.vercel.app/dietas/fodmap.html | Ejemplo de dieta por etapas |
| Trípticos ejemplo | https://dietario.vercel.app/tripticos/dash.pdf · /fodmap.pdf | Capacidad real de cada panel |
| Repositorio | https://github.com/ilanoppenheimer-debug/dietario | Código del sitio |

> Las fichas publicadas están **en revisión**. No usar sus cifras como fuente.

---

## 2. Lógica general

**Una fuente, tres formatos.** Cada dieta se redacta una sola vez y de ahí salen:

| Formato | Lector | Momento | Dónde vive |
|---|---|---|---|
| Ficha web · vista profesional | Médico, nutricionista | Antes de indicar | `dietas/<dieta>.html#medico` |
| Ficha web · vista paciente (imprimible A4) | Paciente, familia | En la casa | `dietas/<dieta>.html#paciente` |
| Tríptico (PDF A4 apaisado, doble faz) | Médico y paciente juntos | En la consulta | `tripticos/<dieta>.pdf` |

Regla: el tríptico y la vista paciente **no pueden contradecirse**. El tríptico es un subconjunto de la vista paciente, más los campos para completar en la consulta.

### Flujo de trabajo

1. **Alcance:** dieta, indicación principal y población (adulto ambulatorio salvo que se indique otra).
2. **Fuentes:** Drive primero, luego web para lo que falta; núcleo de máximo 8 documentos (sección 13).
3. **Reanálisis:** extraer cada dato con su ubicación exacta y clasificar la evidencia.
4. **Tipo de dieta:** elegir los módulos (sección 3).
5. **Redacción:** profesional → paciente → tríptico, en ese orden.
6. **Trazabilidad:** cada afirmación queda con su fila (sección 7).
7. **Puntos a validar:** dudas y decisiones, con quién debe revisarlas.
8. **Validación externa:** especialista y nutricionista, con registro de cambios.
9. **Publicación:** se lleva al repositorio; estado y fecha de revisión visibles.

### Estados

`Borrador` → `En revisión` → `Validada` → `Publicada` · revisión anual obligatoria.

---

## 3. Tipos de dieta y módulos

El "contenido central" de la vista paciente cambia según el tipo de dieta. Elegir **un tipo principal** (puede sumar módulos de otro).

| Tipo | Ejemplos | Módulos centrales (paciente) | Módulo del tríptico (contratapa/interior) |
|---|---|---|---|
| **A. Patrón alimentario** | DASH, mediterránea, diabetes, gota | Plato o proporciones · porciones por grupo con marcadores · semáforo · día ejemplo | Metas marcables + registro de control (PA, glicemia, peso) |
| **B. Eliminación y reintroducción** | Baja en FODMAP | Qué se elimina y por qué · etapas con plazos · tabla de reemplazos · protocolo de reintroducción | Calendario de etapas + registro de síntomas 0–10 |
| **C. Exclusión estricta** | Sin gluten (celiaquía) | Permitido / prohibido / revisar etiqueta · contaminación cruzada · lectura de etiquetas · comer fuera | Lista de verificación de la cocina + contactos de organizaciones |
| **D. Límite de un nutriente** | Hiposódica, renal, sin lactosa | Meta numérica en medidas caseras · fuentes ocultas · tabla de contenido por alimento · reemplazos | Meta indicada por el médico + registro |
| **E. Constancia** | Vitamina K con anticoagulantes | Qué alimentos aportan · por qué importa la constancia · qué avisar | Registro de INR + cambios de dieta |
| **F. Textura o consistencia** | Disfagia (IDDSI) | Nivel indicado · cómo reconocerlo y prepararlo · pruebas caseras · señales de alarma | Nivel marcado por el profesional + ejemplos por nivel |
| **G. Preparación de procedimiento** | Baja en residuos pre-colonoscopía | Línea de tiempo por día · permitido / evitar · qué hacer si… | Calendario con fechas a completar |

---

## 4. Plantilla · vista profesional

| # | Sección | Contenido | Límite |
|---|---|---|---|
| P1 | Encabezado | Nombre de la dieta · fecha de revisión | — |
| P2 | Definición | Qué es, componentes principales | 2–4 líneas |
| P3 | Etiquetas | Indicación principal · lugar en el manejo (1ª línea, 2ª línea, adyuvante) | 2 etiquetas |
| P4 | Indicaciones | Con quién usarla | 3–5 viñetas |
| P5 | Antes de indicarla | Prerrequisitos, descartes, exámenes (si aplica) | 2–4 viñetas |
| P6 | Precauciones / contraindicaciones | Absolutas y relativas, interacciones con fármacos | 3–5 viñetas |
| P7 | Mecanismo | Fisiopatología breve | 2–3 líneas |
| P8 | Magnitud del efecto | 2–4 barras: etiqueta · valor · unidad · fuente · nota del diseño del estudio | 1 gráfico |
| P9 | Tabla de evidencia | Estudio (autor, revista, año) · Diseño (tipo, n, duración) · Resultado principal (con cifras) · Nivel | 3–6 filas |
| P10 | Limitaciones de la evidencia | Sesgos, vacíos, aplicabilidad | 1–3 líneas |
| P11 | Prescribirla en consulta | Pasos en orden | 4–5 pasos |
| P12 | Parámetros prácticos | Porciones, metas numéricas o niveles | 1 recuadro |
| P13 | Derivar si | A nutricionista o especialista | 4–5 viñetas |
| P14 | Referencias | Vancouver, con PMID/DOI | 5–10 |

**Niveles permitidos (P9):** `ECA` · `Metaanálisis` · `Observacional` · `Consenso` · fuerza de guía tal como la publica la guía (p. ej., "Clase I", "Condicional, muy baja calidad").

---

## 5. Plantilla · vista paciente

Lenguaje de 6º a 8º básico, tuteo, frases de menos de 20 palabras, sin siglas sin explicar.

| # | Sección | Contenido | Límite |
|---|---|---|---|
| V1 | Etiqueta superior | "Ficha educativa · <problema de salud>" | — |
| V2 | Título | Nombre + para qué sirve ("Dieta DASH: comer para bajar la presión") | ≤ 60 caracteres |
| V3 | Bajada | Qué es y qué no es | 2–3 frases |
| V4 | Etiquetas | 3 ideas fuerza ("Es temporal", "Menos sal") | 3 × ≤ 25 caracteres |
| V5 | Cifra motivadora | Número grande + explicación simple + plazo en que se nota | 1 cifra, 2–3 frases |
| V6 | Contenido central | Módulos según el tipo de dieta (sección 3) | 2–4 bloques |
| V7 | Día ejemplo | Desayuno, colación, almuerzo, once, cena, colación, con alimentos chilenos | 4–6 comidas, ≤ 30 palabras c/u |
| V8 | Trucos | Acciones concretas | 6–8 viñetas |
| V9 | Errores frecuentes | Si la dieta los tiene | 4–6 viñetas |
| V10 | Consulta antes si… | Situaciones de riesgo o que requieren adaptación | 3–4 viñetas |
| V11 | Pie | Descargo breve · fuentes en una línea · fecha de revisión | — |

### Bloques reutilizables (V6)

- **Porciones por grupo:** grupo · cantidad por día o semana · equivalencia casera · n.º de marcadores (máx. 8 grupos).
- **Semáforo:** Todos los días / Con moderación / Evitar · 5–9 alimentos por color.
- **Reemplazos:** alto → bajo, 6–8 filas.
- **Etapas:** n.º · nombre · plazo · qué se hace · criterio para avanzar o suspender.
- **Protocolo de prueba:** grupo · alimento · cantidad día 1, 2 y 3.
- **Fuentes ocultas:** chips de alimentos + sello "ALTO EN" si aplica.
- **Línea de tiempo:** día −n … día 0, con qué se come cada día.
- **Niveles:** n.º y nombre del nivel · cómo se ve · ejemplo · prueba casera.

### Medidas caseras

taza (≈ 200–240 ml), ½ taza, cucharada, cucharadita, unidad, rebanada, puñado, palma de la mano. Gramos solo entre paréntesis cuando importan.

---

## 6. Plantilla · tríptico

A4 apaisado, plegado en rollo, doble faz con volteo por el borde corto. **Cada panel tiene capacidad fija**: si el texto no cabe, se recorta, no se achica la letra.

| Cara | Panel | Contenido | Capacidad aprox. |
|---|---|---|---|
| Exterior | Portada (derecha) | Etiqueta · título · subtítulo · ilustración · Nombre / Fecha | Título ≤ 25 car.; subtítulo ≤ 45 car. |
| Exterior | Solapa (izquierda; se ve al abrir) | El porqué: cifra + 3 ideas con ícono + mensaje clave | 120 palabras |
| Exterior | Contratapa (centro) | Ejemplo práctico (día tipo o etapas) + **QR a la ficha** + recuadro "Indicaciones de tu médico" (2 líneas, 1 dato específico, próximo control) | 6 ítems cortos |
| Interior | Panel 1 | Contenido central parte 1 (p. ej., porciones o reemplazos) | 8 filas cortas |
| Interior | Panel 2 | Contenido central parte 2 (p. ej., sal + semáforo, o protocolo) | 150 palabras o 1 tabla de 8 filas |
| Interior | Panel 3 | Contenido central parte 3 (p. ej., semáforo ampliado o protocolo) + "Consulta antes si…" | 150 palabras; 3 alertas |

Reglas del tríptico:
- **Prioridad: informar.** El paciente debe poder entender qué comer y qué evitar sin volver a preguntar. Lo que se completa a mano se limita al recuadro "Indicaciones de tu médico".
- El "qué comer / qué evitar" va en listas concretas de alimentos chilenos, no en principios generales.
- El QR lleva a `dietario.vercel.app/<dieta>` (redirección a la vista paciente de la ficha).
- Si un examen previo es obligatorio (p. ej., serología celíaca), va destacado en la solapa o en el recuadro del médico.
- Se imprime en color y en blanco y negro: nada puede depender solo del color (usar ✓, !, ✕, ⚠ y palabras).
- Ninguna cifra que no esté en la vista paciente.

---

## 7. Trazabilidad, cambios y validación

### Tabla de trazabilidad (obligatoria por ficha)

| # | Afirmación o cifra | Dónde aparece (P#/V#/T#) | Fuente exacta (cita + tabla/figura/página) | Tipo de evidencia | Comentario (subgrupo, redondeo, extrapolación) |
|---|---|---|---|---|---|

Reglas: una fila por cifra; si se redondea, indicarlo; si es análisis secundario o de subgrupo, indicarlo; si no hay fuente, **no va en la ficha**.

### Registro de cambios

| Fecha | Sección | Antes | Después | Solicitado por | Fuente |
|---|---|---|---|---|---|

### Puntos a validar

| # | Punto | Tipo (cifra, adaptación local, decisión entre guías, redacción) | Revisa (especialista / nutricionista / médico autor) | Estado |
|---|---|---|---|---|

### Checklist antes de pasar a "Validada"

- [ ] Todas las cifras tienen fila de trazabilidad verificada contra la fuente primaria
- [ ] Guías vigentes a la fecha (año indicado)
- [ ] Vista profesional revisada por especialista del área
- [ ] Vista paciente y tríptico revisados por nutricionista
- [ ] Tríptico y vista paciente sin contradicciones
- [ ] Fecha de revisión y próxima revisión definidas

---

## 8. Formato de entrega para el sitio

Para llevar una ficha al sitio, entregarla en Markdown con los códigos de sección como encabezados, en este orden:

```
# <Dieta> · Tipo <A–G> · Estado: <estado> · Revisión: <mes año>

## Profesional
### P2 Definición
...
### P14 Referencias
...

## Paciente
### V1 Etiqueta
...
### V11 Pie
...

## Tríptico
### T-Portada
### T-Solapa
### T-Contratapa
### T-Panel1
### T-Panel2
### T-Panel3

## Trazabilidad
## Puntos a validar
## Registro de cambios
```

Datos de gráficos (P8) y tablas en tablas Markdown, no en prosa.

**Nombres para el selector.** En la app cada vista se lee por secciones en un menú desplegable. Agrupa las secciones y dales un nombre corto (≤ 25 caracteres). Referencia DASH:
- Paciente: ¿Cuánto ayuda? · Porciones · La sal · Qué elegir · Un día de ejemplo · Trucos · Antes de empezar
- Profesional: Resumen · Magnitud del efecto · Evidencia · Prescribir · Referencias

---

## 9. Plantilla · condición para el paciente (Mi salud)

Siempre 4 secciones, en este orden. Lenguaje paciente (sección 5).

| Sección | Contenido | Bloques típicos |
|---|---|---|
| Qué es | Definición simple, por qué importa, cifra diagnóstica si es útil | [CIFRA] + 1–2 párrafos + [TARJETA] |
| Mi alimentación | Qué comer más y menos, enlaces a las dietas de Dietario que aplican | [TARJETA] "Más de" / "Menos de" con ✓ y ✕ · enlace a ficha |
| Mi control | Qué medir y cada cuánto, metas ("las fija tu médico" + referencia general con fuente), remedios | [TARJETA] + [BOTÓN] al registro si aplica |
| Cuándo consultar | Urgencia vs. pedir hora | [ALERTA] urgencia · [TARJETA] pedir hora |

Reglas: sin dosis de fármacos; umbrales de alarma solo si están en una guía (si no, a "Puntos a validar").

---

## 10. Plantilla · tema clínico profesional

Para médicos de medicina interna y de hospital. Entre 6 y 12 secciones con nombre corto (≤ 30 caracteres) y una sección final **Fuentes**.

Orden sugerido (adaptar al tema):
1. Definición y metas
2. Evaluación inicial o al ingreso
3. Manejo, una sección por escenario (p. ej., basal, corrección, corticoides)
4. Situaciones especiales (ayuno, nutrición enteral/parenteral, ERC, adulto mayor)
5. Complicaciones y alertas
6. Ambulatorio y alta (incluye "si hay acceso" y alternativa de menor costo)
7. Fuentes (y discordancias resueltas)

Cada sección contiene solo bloques (sección 12). Todo bloque con cifras termina en `Fuente:`.

---

## 11. Especificación · calculadora

| Campo | Contenido |
|---|---|
| Nombre y para qué sirve | 1 línea |
| Entradas | nombre · unidad · rango válido · valor por defecto · opciones (si son botones) |
| Cálculo | fórmula o tabla exacta, con fuente (guía, tabla, página) |
| Redondeo | hacia abajo, al entero, a 0,5… (como lo hace la guía) |
| Salidas | qué se muestra en grande y qué como detalle |
| Avisos | condiciones que disparan alerta y su texto |
| Casos de prueba | ≥ 3 con entradas y resultado esperado; usar los ejemplos de la guía si existen |
| Zonas grises | valores entre tramos, datos faltantes: qué decisión se tomó (va a "Puntos a validar") |

---

## 12. Bloques

| Bloque | Uso | Límite |
|---|---|---|
| `[TARJETA] Título` | Contenido general | 2–6 líneas de ≤ 25 palabras + `Fuente:` |
| `[ALERTA] Título` | Urgencias, riesgos, errores peligrosos | 1–4 líneas + `Fuente:` |
| `[TABLA] Título` | Umbrales, dosis, comparaciones | ≤ 4 columnas (6 si son números cortos), ≤ 8 filas + `Fuente:` |
| `[NOTA]` | Discordancia entre guías o aclaración | 1–2 líneas |
| `[PENDIENTE] Qué falta` | Lo que no está en las fuentes entregadas | 1–2 líneas con el documento que lo resolvería |
| `[CIFRA] Valor` | Solo paciente: un número que motive o defina | 1 cifra + 1–2 frases |
| `[BOTÓN] Texto → destino` | Enlace a calculadora, registro o ficha | — |

Si algo no cabe, se divide en dos bloques: no se comprime.

---

## 13. Búsqueda de fuentes (Fase 1)

### 13.1 Drive primero

Las fuentes viven en Google Drive, no en el conocimiento del proyecto. Hay dos carpetas dentro de "Beca MMII", con roles distintos:

| Carpeta | Rol | Qué se hace ahí |
|---|---|---|
| **Dietario** | Carpeta de trabajo: una subcarpeta por tema | Aquí va el material de cada contenido. La Fase 2 lee de aquí |
| **Especialidades** | Biblioteca general por especialidad | Se revisa para no descargar lo que ya existe. No se duplica: si un documento de aquí es núcleo, Ilan crea un acceso directo en la subcarpeta del tema en Dietario |

Antes de buscar en la web:
1. Lista la subcarpeta del tema en Dietario y la carpeta de la especialidad en Especialidades, con sus subcarpetas, **recorriendo todas las páginas** de resultados. No basta con buscar por título: da falsos negativos.
2. Para cada documento útil anota: nombre · año · ruta · vigencia (vigente / hay versión más nueva / retirada).
3. Busca en la web solo lo que falta, las ediciones más nuevas y las fuentes chilenas.

**Dietario** (Beca MMII › Dietario):

| Subcarpeta | Contenido |
|---|---|
| 00_Transversal_Chile_y_OMS | Guías Alimentarias MINSAL, Reglamento Sanitario de los Alimentos (Ley 20.606), ENS, OMS. Sirve para todos los temas |
| 01_DASH, 02_Diabetes, 03_Renal… | Una por tema, numeradas. Para un tema nuevo, propone la siguiente numeración (p. ej., 04_Hiposodica) |
| 80_Referencia_general_no_es_fuente | Manuales y libros de texto. Punto de partida, **nunca se citan** |
| 90_Nutricion_clinica_hospitalaria | Guías ESPEN/ASPEN, vademécum de fórmulas enterales. Para temas clínicos y calculadoras |

**Especialidades** (Beca MMII › Especialidades):

| Tema de Dietario | Carpeta principal | Ver también |
|---|---|---|
| Diabetes, hiperglicemia hospitalaria | Endocrinología › 01_Diabetes | Endocrinología › 08_Nutricion |
| Obesidad, hígado graso, síndrome metabólico | Endocrinología › 06_Obesidad_y_Sindrome_Metabolico | 01_Diabetes |
| Nutrición clínica, NE/NP, realimentación, UCI | Endocrinología › 08_Nutricion | Cuidados Críticos |
| HTA, dislipidemia, riesgo cardiovascular | Cardiología | Endocrinología › 01_Diabetes (dislipidemia MINSAL) |
| ERC, dieta renal, hiposódica | Nefrología | Cardiología |
| Celiaquía, FODMAP, cirrosis, pancreatitis, baja en residuos | Gastroenterología | — |
| Disfagia, sarcopenia, desnutrición del adulto mayor | Geriatría › 07_Fragilidad_Sarcopenia_y_Desnutricion | Neurología (ACV) |
| Paciente oncológico | Oncología › 07_Dolor_y_Sintomas_en_Cancer_Avanzado | Endocrinología › 08_Nutricion |

Si una carpeta no aparece con este nombre, lista la carpeta que la contiene y búscala por su contenido.

**Documentos nuevos:** se guardan en la subcarpeta del tema en Dietario, con nombre según la convención: `Guía <Sociedad> <Año> - <Tema>.pdf` · `Review <Año> - <Tema> (Autores).pdf` · `Metaanálisis <Año> - <Tema> (Autor).pdf` · `ECA <Año> - <Nombre del estudio>.pdf`. Antes de proponer uno, verifica que no esté ya en Dietario ni en Especialidades.

### 13.2 Ventanas de años

| Tipo | Ventana | Regla |
|---|---|---|
| Guía de sociedad | Última edición vigente | Si tiene > 5 años: buscar actualización y verificar que no esté retirada o archivada. Retirada = no se usa |
| Metaanálisis / RS | Últimos 5 años | Uno anterior solo si no hay uno más nuevo, y se dice |
| ECA fundacional | Sin límite | Marcado "fundacional"; sirve para magnitud del efecto (P8–P9), no para fijar recomendaciones |
| Otros ECA | Últimos 10 años | — |
| Cohortes | Últimos 10 años | Solo si no hay ECA |
| Documento chileno (MINSAL, sociedades) | Última versión | Año visible. Si tiene > 5 años o contradice una guía vigente: capa local, marcado "desactualizado" |
| Tablas de composición / intercambio | La vigente | Indicar edición |

No se usan: StatPearls, Merck, libros de texto como fuente citada, blogs ni guías retiradas.

### 13.3 Lo más relevante: núcleo primero

La lista no es un inventario exhaustivo. Se ordena así:

| Prioridad | Máximo | Qué entra |
|---|---|---|
| 1 · Núcleo | 8 | Sin estos documentos no se puede armar el contenido |
| 2 · Complementario | 6 | Mejoran una sección concreta (magnitud del efecto, adaptación local) |
| 3 · Opcional | 4 | Solo si hay tiempo o acceso |

Un documento entra al núcleo si cumple al menos dos de estos criterios, y se dice cuáles:
1. Es la guía vigente de la sociedad de referencia del tema.
2. De él salen cifras o recomendaciones que irán en la ficha.
3. Aplica a adultos y a la práctica en Chile (medicina interna u hospital).
4. Es el más reciente entre los que dicen lo mismo.
5. No es redundante con otro documento del núcleo.

Si dos guías dicen lo mismo, entra la más reciente y la otra baja a Prioridad 3 o sale. Si propones más documentos que el máximo, justifícalo.

### 13.4 Formato de entrega de la Fase 1

```
# <Tema> · Fase 1 · Búsqueda <fecha>

## Alcance
## Ya en Drive
| Documento | Año | Ruta | Vigencia |
## Lista de fuentes
| Prioridad | Documento (cita completa) | Año | Tipo | Estado (En Drive / Descargar) | Link | Acceso | Qué aporta | Destino + nombre sugerido |
## Fuentes chilenas
## Discordancias previsibles
## Preguntas que la evidencia debe responder
```
