# Dietario (prototipo)

App web (instalable, funciona sin conexión) con pautas de alimentación con evidencia, en dos perfiles:

- **Paciente:** fichas de dietas en lenguaje simple, Mi salud por condición (presión alta, diabetes), Mis dietas y registro de presión y glicemia para llevar al control (impreso, archivo o QR).
- **Profesional** (con código): vista profesional de cada ficha, trípticos, evaluar un paciente, calculadoras (requerimientos, gasto energético, realimentación, enteral, insulina, sodio corregido y osmolaridad) y temas clínicos (diabetes, realimentación, renal, UCI, pancreatitis).

> **Prototipo en revisión.** El contenido aún no está validado por el equipo clínico.

## Estructura

```
site/                         ← lo que se publica
  index.html                  ← elegir perfil → introducción (solo la primera vez) → inicio
  salud/  registro/  dietas/  clinica/  nosotros.html  codigo.html
  dietas/<dieta>.html         ← ficha: #paciente y #medico (solo perfil profesional); ?imprimir abre la impresión
  tripticos/<dieta>(-bn).pdf  ← color y blanco y negro
  assets/app.css, app.js      ← estructura común: navegación, perfiles, selector de secciones, Mis dietas
  assets/nutricalc.js         ← cálculos (funciones puras, con pruebas)
  assets/registro.js          ← registro del paciente (solo en el dispositivo)
  manifest.webmanifest, sw.js ← app instalable y sin conexión
middleware.ts, api/acceso.ts  ← acceso profesional (Vercel)
src/tripticos/                ← fuente HTML de cada tríptico
tools/build_app.py            ← genera las páginas de la app (el contenido se edita ahí y en tools/contenido/)
tools/adaptar_fichas.py       ← integra una ficha nueva a la app (barra, secciones, Mis dietas)
```

## Reglas de contenido

Solo cifras de guías vigentes, con la guía al lado. Ante discordancia, gana la más reciente. Términos: "insulina cristalina".

## Privacidad

Sin cuentas ni base de datos. Perfil, Mis dietas y registro de presión y glicemia quedan en el dispositivo (localStorage). El QR del registro lleva los datos dentro de la URL (después de `#`, que no llega al servidor). Las calculadoras no guardan nada.

## Acceso profesional

`/clinica/*` solo se sirve con la cookie que entrega `/api/acceso` al ingresar el código. El código es la variable de entorno **`PRO_CODE`** del proyecto en Vercel (Production y Preview). Si no está definida, nadie entra. Cambiarla deja fuera todas las sesiones anteriores.

## Antes de publicar

```
node tools/test_nutricalc.js      # todas las pruebas deben pasar
python3 tools/build_app.py        # regenera las páginas
python3 -m http.server 8000 -d site   # ver en local (sin el acceso profesional, que es de Vercel)
```

## Agregar una dieta

1. Ficha en `site/dietas/<dieta>.html` siguiendo la estructura de `dash.html`; agregarla a `GRUPOS` en `tools/adaptar_fichas.py` y correrlo.
2. Agregarla a `CATS` en `tools/build_app.py`.
3. Tríptico en `src/tripticos/<dieta>.html` → `python3 tools/build_tripticos.py <dieta>`.
