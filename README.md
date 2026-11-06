# Guías de Alimentación (prototipo)

Sitio estático con pautas de alimentación con evidencia: una ficha web por dieta (vista paciente y vista profesional, imprimible en A4) y un tríptico PDF para entregar en la consulta.

> **Prototipo en revisión.** El contenido aún no está validado por el equipo clínico.

## Estructura

```
site/                  ← lo que se publica
  index.html           ← portal: buscador, filtros y catálogo
  dietas/<dieta>.html  ← ficha: #paciente y #medico; ?imprimir abre el diálogo de impresión
  tripticos/<dieta>.pdf      ← color
  tripticos/<dieta>-bn.pdf   ← blanco y negro
  assets/              ← ficha.css, portal.css, favicon
src/tripticos/         ← fuente HTML de cada tríptico (A4 apaisado, doble faz)
tools/                 ← scripts que generan site/ desde los borradores
```

## Herramientas profesionales

- `site/herramientas/calculadora.html` usa `site/assets/nutricalc.js` (funciones puras). Antes de publicar un cambio: `node tools/test_nutricalc.js` (todas las pruebas deben pasar).
- `site/herramientas/nutricion-hospitalaria.html` se genera con `python3 tools/build_torpedo.py`; el contenido se edita en ese script.
- Regla: solo cifras de guías vigentes, con la guía al lado. Las fórmulas del manual 2014 van marcadas como tales.

## Ver en local

```
python3 -m http.server 8000 -d site
```

## Publicar en Vercel

Proyecto estático, sin build: `vercel deploy site --prod` (o directorio de salida `site` en el panel).

## Agregar una dieta

1. Ficha en `site/dietas/<dieta>.html` siguiendo la estructura de `dash.html`.
2. Tríptico en `src/tripticos/<dieta>.html` → `python3 tools/build_tripticos.py <dieta>` genera `<dieta>.pdf` (color) y `<dieta>-bn.pdf` (blanco y negro, reglas en `src/tripticos/bn.css`).
3. En `site/index.html`, en la lista `D`, marcar la dieta con `on:1, slug:"<dieta>"`.

## Checklist de revisión por ficha

- [ ] Cifras verificadas contra la fuente primaria (abstract o texto completo)
- [ ] Guías vigentes a la fecha de revisión
- [ ] Vista paciente revisada por nutricionista
- [ ] Vista profesional revisada por especialista del área
- [ ] Fecha de revisión actualizada
