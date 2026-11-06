# Dietario · Plantillas y lógica de armado de fichas

Documento de conocimiento para el Project "Curador de Dietas". Contiene **estructura y reglas, no contenido clínico**. Toda cifra o recomendación se obtiene de los documentos primarios del conocimiento.

Versión 1.0 · noviembre 2026

---

## 1. Links

| Recurso | URL | Uso |
|---|---|---|
| Sitio (prototipo) | https://dietario.vercel.app/ | Ver cómo se presentan las fichas |
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
2. **Fuentes:** inventario de guías y estudios disponibles en el conocimiento y de los que faltan.
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
| Exterior | Contratapa (centro) | Registro/seguimiento según tipo (sección 3) + próximo control, médico/a, centro o nutricionista | Tabla de 6–8 filas |
| Interior | Panel 1 | Contenido central parte 1 (p. ej., porciones o reemplazos) | 8 filas cortas |
| Interior | Panel 2 | Contenido central parte 2 (p. ej., sal + semáforo, o protocolo) | 150 palabras o 1 tabla de 8 filas |
| Interior | Panel 3 | **Metas o indicaciones marcables por el médico** + "Consulta antes si…" | 8–9 metas × ≤ 50 car.; 3 alertas |

Reglas del tríptico:
- Las metas son **acciones concretas y verificables** ("Sacar el salero de la mesa", no "Comer más sano").
- Incluir siempre 1 meta con blanco para completar ("Bajar el pan a ___ al día") y 1 línea "Otra: ____".
- Si un examen previo es obligatorio (p. ej., serología celíaca), va como **primera meta**.
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
