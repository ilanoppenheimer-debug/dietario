"""Adapta las fichas de dietas (site/dietas/*.html) a la estructura de la app: barra superior y navegación de Dietario,
selector de secciones, Mis dietas, tríptico, y vista profesional solo para el perfil profesional.
Idempotente: si la ficha ya está adaptada, no hace nada. Uso: python3 tools/adaptar_fichas.py"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRUPOS = {
    "dash": {
        "paciente": [["¿Cuánto ayuda?"], ["Porciones"], ["La sal"], ["Qué elegir"], ["Un día de ejemplo"], ["Trucos"], ["Antes de empezar"]],
        "medico": [["Resumen"], ["Magnitud del efecto"], ["Evidencia"], ["Prescribir", "+"], ["Referencias"]],
        "titulo": "Dieta DASH",
    },
    "fodmap": {
        "paciente": [["¿Funciona?"], ["Qué son"], ["Las 3 etapas"], ["Etapa 1: cambios"], ["Etapa 2: volver a probar"], ["Errores frecuentes"], ["Antes de empezar"]],
        "medico": [["Resumen"], ["Magnitud del efecto"], ["Evidencia"], ["Prescribir", "+"], ["Referencias"]],
        "titulo": "Dieta baja en FODMAP",
    },
}

TOP = '''<header class="a-top"><a class="a-back" href="index.html" aria-label="Volver a Dietas"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></a><span class="a-brand">Dietas</span><span class="a-proto" title="Contenido en revisión, aún no validado por el equipo clínico">Prototipo</span><a class="a-chip" data-perfil href="../index.html?perfil">Perfil</a></header>'''

def barra(k):
    return f'''<div class="a-banner" id="qr-nuevo" hidden><span style="flex:1"><b>¿Primera vez en Dietario?</b> Guarda esta dieta y conoce el resto de la app.</span><a class="a-chip" href="../index.html?intro" style="background:var(--a-green);color:#fff">Conocer</a><button class="a-x" type="button" aria-label="Cerrar aviso">✕</button></div>
  <div class="a-fbar a-noprint" style="display:flex;flex-direction:column;gap:10px">
   <div class="a-seg" data-pro hidden role="group" aria-label="Versión de la ficha"><a href="#paciente" data-view="paciente">Paciente</a><a href="#medico" data-view="medico">Profesional</a></div>
   <div style="display:flex;flex-wrap:wrap;gap:8px">
    <button class="a-btn pill line" type="button" data-mis="{k}" data-pac aria-pressed="false">+ Agregar a Mis dietas</button>
    <button class="a-btn pill line" type="button" id="printbtn"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M7 8V3h10v5M7 17H5a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="7" y="14" width="10" height="7"/></svg><span>Imprimir hoja</span></button>
    <a class="a-btn pill line" href="../tripticos/{k}.pdf" data-pro hidden>Tríptico color</a>
    <a class="a-btn pill line" href="../tripticos/{k}-bn.pdf" data-pro hidden>Tríptico B/N</a>
   </div>
  </div>'''

def agrupar(main_html, grupos):
    """main_html: contenido interior de <main>. Deja fuera el primer bloque (título) y el footer."""
    partes = re.split(r"\n(?=    <(?:section|div|footer)[ >])", main_html)
    cabeza, resto = partes[0], partes[1:]
    titulo = resto.pop(0)              # hero o encabezado del médico
    footer = resto.pop() if resto and resto[-1].lstrip().startswith("<footer") else ""
    out, i = [], 0
    for g in grupos:
        nombre, n = g[0], (2 if len(g) > 1 and g[1] == "+" else 1)
        bloque = "\n".join(resto[i:i + n]); i += n
        out.append(f'    <div data-sec="{nombre}">\n{bloque}\n    </div>')
    assert i == len(resto), (i, len(resto))
    return cabeza + "\n" + titulo + "\n    <div data-secs>\n" + "\n".join(out) + "\n    </div>\n" + footer

def adaptar(k):
    p = os.path.join(ROOT, f"site/dietas/{k}.html")
    s = open(p, encoding="utf-8").read()
    if 'class="a-app' in s:
        print("ya adaptada", k); return
    G = GRUPOS[k]
    s = s.replace('<link rel="stylesheet" href="../assets/ficha.css">',
                  '<link rel="stylesheet" href="../assets/ficha.css">\n<link rel="stylesheet" href="../assets/app.css">\n'
                  '<link rel="manifest" href="../manifest.webmanifest">\n<link rel="apple-touch-icon" href="../assets/icons/apple-touch-icon.png">\n<meta name="theme-color" content="#FFFFFF">')
    s = s.replace("<body>", '<body class="a-app" data-root="../" data-nav="dietas" data-qr>', 1)
    s = re.sub(r'<div class="proto">.*?</header>', TOP, s, count=1, flags=re.S)
    s = s.replace('<a class="crumb" href="../index.html#dietas">← Todas las dietas</a>', barra(k), 1)
    for v in ("paciente", "medico"):
        m = re.search(r'(<main data-v="%s"[^>]*>)(.*?)(\n  </main>)' % v, s, re.S)
        s = s[:m.start()] + m.group(1) + agrupar(m.group(2), G[v]) + m.group(3) + s[m.end():]
    # navegación + app.js antes del script de la ficha
    s = s.replace("<script>\n(function(){", '<nav class="a-nav"></nav>\n<script src="../assets/app.js"></script>\n<script>\n(function(){', 1)
    s = s.replace('links=document.querySelectorAll(".sitebar .tabs a")', 'links=document.querySelectorAll("[data-view]")')
    s = s.replace('var v=(location.hash||"#paciente").slice(1); if(v!=="medico") v="paciente";',
                  'var v=(location.hash||"#paciente").slice(1); if(v!=="medico"||!Dietario.isPro()) v="paciente";')
    s = s.replace('links.forEach(function(a){if(a.dataset.view===v)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});',
                  'links.forEach(function(a){if(a.dataset.view===v)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});\n'
                  '    document.querySelectorAll(\'main[data-v="\'+v+\'"] [data-secs]\').forEach(function(b){Dietario.secciones(b)});')
    # banner QR: se agrega dentro del IIFE existente, antes de su cierre final
    cierre = "\n})();\n</script>\n</body>"
    assert s.count(cierre) == 1
    s = s.replace(cierre, '''
  var qb=document.getElementById("qr-nuevo");
  if(Dietario.get("qrNuevo",false)&&!Dietario.get("intro.pac",false)&&!Dietario.isPro()){qb.hidden=false;qb.querySelector(".a-x").addEventListener("click",function(){Dietario.set("intro.pac",true);qb.hidden=true});}''' + cierre)
    for need in ('data-secs', 'a-nav', 'Dietario.isPro()', 'data-mis', 'a-top'):
        assert need in s, need
    open(p, "w", encoding="utf-8").write(s)
    print("ok", k)

for k in GRUPOS:
    adaptar(k)
