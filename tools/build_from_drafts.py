"""Convierte los borradores de fichas (HTML autónomos) en páginas del sitio.

Uso: python3 tools/build_from_drafts.py <carpeta_borradores>
Genera: site/assets/ficha.css, site/dietas/*.html
"""
import re, sys, os

SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
os.makedirs(os.path.join(SITE, "dietas"), exist_ok=True)

dash = open(os.path.join(SRC, "dieta-dash.html")).read()
fod = open(os.path.join(SRC, "dieta-fodmap.html")).read()

# ---------- CSS compartido ----------
css = re.search(r"<style>(.*?)</style>", dash, re.S).group(1)
css = re.sub(r"@media \(prefers-color-scheme: dark\)\{.*?color-scheme:dark\}\}\n", "", css, flags=re.S)
css = re.sub(r':root\[data-theme="dark"\]\{.*?color-scheme:dark\}\n', "", css, flags=re.S)
css = css.replace(':root,:root[data-theme="dark"]{', ":root{")
css = css.replace("--f-mono:\"IBM Plex Mono\", ui-monospace, Menlo, monospace;\n}",
                  "--f-mono:\"IBM Plex Mono\", ui-monospace, Menlo, monospace;\n  color-scheme:light;\n}")
fod_css = re.search(r"<style>(.*?)</style>", fod, re.S).group(1)
fod_extra = fod_css[fod_css.index(".letters{"):]
css = css.replace("body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:16px;line-height:1.55;\n  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}",
                  "body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:16px;line-height:1.55}\n.page{padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}")

css += fod_extra + r"""
/* ===== Sitio: barra superior, aviso de prototipo, impresión ===== */
.proto{background:#FFF6DD;color:#6B4E00;border-bottom:1px solid #EED9A0;font-size:.84rem;text-align:center;padding:7px max(16px, env(safe-area-inset-right,0px)) 7px max(16px, env(safe-area-inset-left,0px))}
.proto b{font-weight:800}
.sitebar{position:sticky;top:env(safe-area-inset-top,0px);z-index:9;background:var(--surface);border-bottom:1px solid var(--line)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--surface)}
.sitebar .in{max-width:780px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;padding:10px max(16px, env(safe-area-inset-right,0px)) 10px max(16px, env(safe-area-inset-left,0px))}
.home{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-family:var(--f-display);font-weight:800;font-size:1rem;min-width:0}
.home .mark{width:32px;height:32px;border-radius:9px;background:var(--leaf);display:grid;place-items:center;flex:none}
.home .mark svg{width:20px;height:20px;color:#fff}
.sitebar .tabs{margin-left:auto}
.printbtn{font:inherit;font-weight:800;font-size:.9rem;display:flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:7px 14px;cursor:pointer}
.printbtn svg{width:17px;height:17px}
.printbtn:hover{border-color:var(--leaf);color:var(--leaf)}
.crumb{font-size:.88rem;font-weight:700;color:var(--leaf);text-decoration:none;align-self:flex-start}
.crumb:hover{text-decoration:underline}

/* ===== Gráficos de barras en HTML (se adaptan al ancho) ===== */
.bars{display:flex;flex-direction:column;gap:12px}
.bar{display:grid;grid-template-columns:minmax(150px,210px) 1fr;gap:6px 14px;align-items:center}
.bar .bl{font-size:.9rem;font-weight:600;min-width:0}
.bar .bt{display:flex;align-items:center;gap:8px;min-width:0;height:28px;
  background:linear-gradient(to right,var(--line) 1px,transparent 1px) 0 0/var(--tick) 100% repeat-x}
.bar .bt i{display:block;height:24px;border-radius:5px;flex:none}
.bar .bt b{font-family:var(--f-mono);font-weight:500;font-size:.85rem;font-variant-numeric:tabular-nums;flex:none}
.axis{display:grid;grid-template-columns:minmax(150px,210px) 1fr;gap:14px}
.axis .ax{position:relative;height:18px;font-size:.78rem;color:var(--muted)}
.axis .ax span{position:absolute;top:0;transform:translateX(-50%);white-space:nowrap}
.axis .ax span:first-child{transform:none}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.84rem;color:var(--muted)}
.legend span{display:flex;align-items:center;gap:6px}
.legend i{width:12px;height:12px;border-radius:3px;display:block}

/* ===== Celular ===== */
@media (max-width:640px){
  .sitebar .tabs{order:3;margin-left:0;width:100%;display:flex}
  .sitebar .tabs a{flex:1;text-align:center}
  .printbtn{margin-left:auto}
  .printbtn span{display:none}
  .bar{grid-template-columns:1fr;gap:4px}
  .axis{grid-template-columns:1fr}
  .axis > :first-child{display:none}
  .kv{grid-template-columns:1fr}
  /* tablas apiladas como tarjetas */
  .tbl{overflow:visible;border:0;background:none}
  .tbl table{min-width:0;display:block}
  .tbl thead{display:none}
  .tbl tbody{display:flex;flex-direction:column;gap:10px}
  .tbl tr{display:block;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
  .tbl td{display:grid;grid-template-columns:7.5em 1fr;gap:10px;border:0;padding:5px 0;font-size:.9rem}
  .tbl td::before{content:attr(data-label);font-size:.7rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding-top:3px}
  .tbl td:first-child{display:block;font-size:1rem;padding-bottom:8px;margin-bottom:4px;border-bottom:1px solid var(--line)}
  .tbl td:first-child::before{display:none}
  .tbl.compact td{grid-template-columns:6em 1fr}
  .tbl td[data-label^="Día"]{display:inline-grid;grid-template-columns:1fr;gap:2px;width:33.33%;vertical-align:top;padding-top:8px}
}
@media print{
  .sitebar,.crumb,.printbtn{display:none!important}
  .proto{font-size:8pt;padding:3px;background:none;border:0;border-bottom:1px solid #ccc}
  .page{padding:0}
  .bar{grid-template-columns:200px 1fr}
}
"""
open(os.path.join(SITE, "assets", "ficha.css"), "w").write(css.strip() + "\n")

# ---------- Utilidades ----------
def label_tables(html):
    def fix(tbl):
        heads = re.findall(r"<th>(.*?)</th>", tbl)
        def row(m):
            cells = re.findall(r"<td>(.*?)</td>", m.group(0), re.S)
            return "<tr>" + "".join('<td data-label="%s"><div class="c">%s</div></td>' % (heads[i] if i < len(heads) else "", c) for i, c in enumerate(cells)) + "</tr>"
        return re.sub(r"<tr><td>.*?</tr>", row, tbl, flags=re.S)
    return re.sub(r'<div class="tbl"><table>.*?</table></div>', lambda m: fix(m.group(0)), html, flags=re.S)

def bars(rows, ticks, unit_max, legend=None, aria=""):
    tick_pct = 100.0 * ticks[1][0] / unit_max
    out = ['<div class="bars" role="img" aria-label="%s" style="--tick:%.3f%%">' % (aria, tick_pct)]
    for label, val, txt, color, op in rows:
        out.append('<div class="bar"><span class="bl">%s</span><span class="bt"><i style="width:%.2f%%;background:%s;opacity:%s"></i><b>%s</b></span></div>'
                   % (label, 100.0 * val / unit_max, color, op, txt))
    out.append('<div class="axis"><span></span><div class="ax">' + "".join(
        '<span style="left:%.3f%%">%s</span>' % (100.0 * v / unit_max, t) for v, t in ticks) + "</div></div>")
    out.append("</div>")
    if legend:
        out.append('<div class="legend">' + "".join('<span><i style="background:%s"></i>%s</span>' % (c, t) for c, t in legend) + "</div>")
    return "\n".join(out)

ICONS = '''<symbol id="i-print" viewBox="0 0 24 24"><path d="M7 8V3h10v5" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/><rect x="3" y="8" width="18" height="9" rx="2" fill="currentColor"/><rect x="7" y="14" width="10" height="7" rx="1" fill="#fff" stroke="currentColor" stroke-width="2"/></symbol>'''

def page(src, title, desc, slug, accent_css, chart_html):
    sprite = re.search(r'<svg width="0".*?</svg>', src, re.S).group(0).replace("</defs>", ICONS + "</defs>")
    body = src[src.index("<!-- ===================== VISTA PACIENTE"):src.index('<p class="printnote">')]
    # cerrar el wrap original: body termina antes de printnote; dentro hay </main>s
    body = re.sub(r'<svg class="chart".*?</svg>', chart_html, body, flags=re.S)
    body = label_tables(body)
    body = body.replace('<main id="v-paciente" data-v="paciente" class="wrap" style="padding:0">', '<main data-v="paciente" class="wrap" style="padding:0">')
    body = body.replace('<main id="v-medico" data-v="medico" class="wrap" style="padding:0" hidden>', '<main data-v="medico" class="wrap" style="padding:0" hidden>')
    scripts = re.findall(r"<script>(.*?)</script>", src, re.S)[0]
    scripts = scripts.replace('document.querySelectorAll(".tabs a")', 'document.querySelectorAll(".sitebar .tabs a")')
    scripts = scripts.replace("})();", r'''
  var pb=document.getElementById("printbtn");
  var framed=false; try{framed=window.self!==window.top}catch(e){framed=true}
  if(framed){pb.hidden=true}
  pb.addEventListener("click",function(){window.print()});
  if(/[?&]imprimir/.test(location.search)&&!framed){
    (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){setTimeout(function(){window.print()},300)});
  }
})();''')
    html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Guías de Alimentación</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="../assets/ficha.css">
{accent_css}
</head>
<body>
{sprite}
<div class="proto"><b>Prototipo en revisión.</b> Contenido aún no validado por el equipo clínico; no usar para indicar tratamiento.</div>
<header class="sitebar">
  <div class="in">
    <a class="home" href="../index.html"><span class="mark"><svg><use href="#i-leaf"/></svg></span>Guías de Alimentación</a>
    <nav class="tabs" aria-label="Versión de la ficha">
      <a href="#paciente" data-view="paciente">Paciente</a>
      <a href="#medico" data-view="medico">Profesional</a>
    </nav>
    <button class="printbtn" id="printbtn" type="button"><svg aria-hidden="true"><use href="#i-print"/></svg><span>Imprimir</span></button>
  </div>
</header>
<div class="page">
<div class="wrap">
  <a class="crumb" href="../index.html#dietas">← Todas las dietas</a>
{body}
</div>
</div>
<script>{scripts}</script>
</body>
</html>
'''
    open(os.path.join(SITE, "dietas", slug + ".html"), "w").write(html)

dash_chart = bars(
    [("DASH · todos", 5.5, "−5,5", "var(--leaf)", ".55"),
     ("DASH · hipertensos", 11.4, "−11,4", "var(--leaf)", "1"),
     ("DASH + Na bajo · todos", 8.9, "−8,9", "var(--beet)", ".55"),
     ("DASH + Na bajo · hipertensos", 11.5, "−11,5", "var(--beet)", "1")],
    [(0, "0"), (5, "−5"), (10, "−10 mmHg")], 14,
    aria="Reducción de PA sistólica: DASH global −5,5 mmHg; DASH en hipertensos −11,4; DASH más sodio bajo global −8,9; en hipertensos −11,5")
fod_chart = bars(
    [("Basal", 36.0, "36,0", "var(--muted)", ".45"),
     ("Baja en FODMAP", 22.8, "22,8", "var(--leaf)", "1"),
     ("Dieta habitual", 44.9, "44,9", "var(--beet)", "1")],
    [(0, "0"), (20, "20"), (40, "40 mm")], 60,
    aria="Halmos 2014: puntaje basal 36,0 mm; baja en FODMAP 22,8 mm; dieta habitual 44,9 mm")

page(dash, "Dieta DASH", "Dieta DASH para la presión arterial: ficha para pacientes y pauta para profesionales.", "dash", "", dash_chart)
page(fod, "Dieta baja en FODMAP", "Dieta baja en FODMAP para el colon irritable: ficha para pacientes y pauta para profesionales.", "fodmap",
     "<style>:root{--beet:#3D4FA3;--beet-soft:#E7EAF8}</style>", fod_chart)
print("ok")
