"""Genera site/index.html y site/assets/portal.css desde la plantilla del portal."""
import re, sys, os
SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
t = open(os.path.join(SRC, "hub-template.html")).read()

css = re.search(r"<style>(.*?)</style>", t, re.S).group(1)
css = css.replace("body{background:var(--bg)", "body{margin:0;background:var(--bg)")
css += """
.proto{background:#FFF6DD;color:#6B4E00;border-bottom:1px solid #EED9A0;font-size:.84rem;text-align:center;padding:7px max(16px, env(safe-area-inset-right,0px)) 7px max(16px, env(safe-area-inset-left,0px))}
.proto b{font-weight:800}
"""
open(os.path.join(SITE, "assets", "portal.css"), "w").write(css.strip() + "\n")

body = t[t.index("</style>") + len("</style>"):]
mark = '<span class="mark"><svg><use href="#i-leaf"/></svg></span>'
body = body.replace("{{BRAND}}", '<a class="brand" href="index.html">' + mark + '<span class="nm"><b>Guías de Alimentación</b><span>Material educativo con evidencia</span></span></a>')
body = body.replace("{{FOOTBRAND}}", '<div class="brand">' + mark + '<span class="nm"><b>Guías de Alimentación</b><span>Prototipo · noviembre 2026</span></span></div>')
body = body.replace('<header class="hdr">', '<div class="proto"><b>Prototipo en revisión.</b> Contenido aún no validado por el equipo clínico; no usar para indicar tratamiento.</div>\n<header class="hdr">', 1)
body = body.replace('var DASH="{{DASH}}", FOD="{{FOD}}";', '')
body = body.replace('url:DASH}', 'slug:"dash"}').replace('url:FOD}', 'slug:"fodmap"}')
old = re.search(r'acts = aud==="pac"\n.*?;\n', body, re.S).group(0)
new = '''acts = aud==="pac"
          ? '<a class="p" href="dietas/'+x.slug+'.html#paciente">Ver ficha</a><a class="s" href="dietas/'+x.slug+'.html?imprimir#paciente">Imprimir</a>'
          : '<a class="p" href="dietas/'+x.slug+'.html#medico">Pauta profesional</a><a class="s" href="tripticos/'+x.slug+'.pdf" target="_blank" rel="noopener">Tríptico PDF</a><a class="s" href="dietas/'+x.slug+'.html#paciente">Ficha paciente</a>';
'''
body = body.replace(old, new)
body = body.replace("<b>Hoja</b>Para imprimir y pegar en el refri", "<b>Hoja</b>Para imprimir y pegar en el refri")
assert "{{" not in body

html = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Guías de Alimentación</title>
<meta name="description" content="Pautas de alimentación con evidencia para explicar en la consulta y llevar a la casa.">
<meta name="robots" content="noindex">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="assets/portal.css">
</head>
<body>
''' + body.strip() + '''
</body>
</html>
'''
open(os.path.join(SITE, "index.html"), "w").write(html)
open(os.path.join(SITE, "assets", "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#2A7A4B"/><path d="M8 25C8 14 14 8 25 8c0 11-6 17-17 17z" fill="#fff"/><path d="M8 25L19 14" stroke="#2A7A4B" stroke-width="2" stroke-linecap="round"/></svg>')
print("ok")
