"""Genera las páginas de la app Dietario (site/) desde el contenido de este archivo y de tools/contenido/.
Las fichas de dietas (site/dietas/dash.html y fodmap.html) se editan a mano; este script no las toca.
Uso: python3 tools/build_app.py
Regla de contenido: solo cifras de guías vigentes, con la guía al lado. Si discrepan, gana la más reciente."""
import os, json, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DM = json.load(open(os.path.join(ROOT, "tools/contenido/diabetes.json"), encoding="utf-8"))

def esc(s):
    """Escapa texto y permite **negrita**."""
    s = html.escape(s, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800'
         '&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&display=swap">')
CHEV = '<svg class="a-chev" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'
LEAF = '<span class="a-mark"><svg width="20" height="20" viewBox="0 0 32 32" aria-hidden="true"><path d="M5 27C5 13 13 5 27 5c0 14-8 22-22 22z" fill="#FFFFFF"/></svg></span>'
BACK = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'

def page(path, title, body, nav="", back=None, top=None, desc="", scripts=(), head="", bodyattrs="", bare=False):
    depth = path.count("/")
    root = "../" * depth
    top_title = top if top is not None else title
    if bare:
        topbar, navbar = "", ""
    else:
        lead = f'<a class="a-back" href="{root}{back}" aria-label="Volver">{BACK}</a>' if back else LEAF
        topbar = (f'<header class="a-top">{lead}<span class="a-brand">{esc(top_title)}</span>'
                  f'<span class="a-proto" title="Contenido en revisión, aún no validado por el equipo clínico">Prototipo</span>'
                  f'<a class="a-chip" data-perfil href="{root}index.html?perfil">Perfil</a></header>')
        navbar = '<nav class="a-nav"></nav>'
    sc = "".join(f'<script src="{root}assets/{s}"></script>' for s in scripts)
    doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · Dietario</title>
<meta name="description" content="{html.escape(desc or title)}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#2A7A4B">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/icons/apple-touch-icon.png">
<link rel="manifest" href="{root}manifest.webmanifest">
{FONTS}
<link rel="stylesheet" href="{root}assets/app.css">
{head}
</head>
<body class="a-app{' a-bare' if bare else ''}" data-root="{root}" data-nav="{nav}"{bodyattrs}>
{topbar}
{body}
{navbar}
<script src="{root}assets/app.js"></script>
{sc}
</body>
</html>
'''
    out = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    return out

# ---------------------------------------------------------------- bloques de contenido
def blocks(arr, root, accent="var(--a-green)"):
    out = []
    for b in arr:
        k = b[0]
        if k == "table":
            _, h, cols, head, rows, foot = (b + [""])[:6]
            cells = "".join(f'<span class="th">{esc(x)}</span>' for x in head)
            for r in rows:
                cells += "".join(f'<span class="{"c1" if i == 0 else ""}">{esc(x)}</span>' for i, x in enumerate(r))
            hb = f'<b style="padding:0 4px">{esc(h)}</b>' if h else ""
            fb = f'<span class="a-foot" style="padding:0 4px">{esc(foot)}</span>' if foot else ""
            out.append(f'<div class="a-card" style="padding:14px 12px">{hb}<div class="a-tbl" style="--cols:{cols}">{cells}</div>{fb}</div>')
        elif k in ("card", "warn", "amber", "note", "soft"):
            h, lines, foot = b[1], b[2], (b[3] if len(b) > 3 else "")
            cls = {"card": "", "warn": " warn", "amber": " amber", "note": " note", "soft": " soft"}[k]
            out.append(f'<div class="a-card{cls}">{f"<b>{esc(h)}</b>" if h else ""}' + "".join(f"<span>{esc(l)}</span>" for l in lines) +
                       (f'<span class="a-foot">{esc(foot)}</span>' if foot else "") + "</div>")
        elif k == "pend":
            out.append(f'<div class="a-card note"><b>Pendiente · {esc(b[1])}</b>' + "".join(f"<span>{esc(l)}</span>" for l in b[2]) + "</div>")
        elif k == "big":
            out.append(f'<div class="a-card"><span class="a-big" style="color:{accent}">{esc(b[1])}</span>' + "".join(f'<span style="font-size:14.5px">{esc(l)}</span>' for l in b[2]) + "</div>")
        elif k == "p":
            out.extend(f'<p class="a-p">{esc(l)}</p>' for l in b[2])
        elif k == "soon":
            out.append(f'<div class="a-card dash">{esc(b[1])}</div>')
        elif k == "btn":
            mode = b[2]
            href = {"basal": "clinica/calculadoras.html?modo=basal#insulina", "cort": "clinica/calculadoras.html?modo=cort#insulina",
                    "osm": "clinica/calculadoras.html#osmolaridad", "ref": "clinica/calculadoras.html#realimentacion"}[mode]
            out.append(f'<a class="a-btn blue" href="{root}{href}">{esc(b[1])}</a>')
        elif k == "btnReg":
            out.append(f'<a class="a-btn" href="{root}registro/index.html{b[2] if len(b) > 2 and b[2] else ""}">{esc(b[1])}</a>')
        elif k == "html":
            out.append(b[1])
        else:
            raise ValueError(k)
    return "\n".join(out)

def secciones(defs, data, root, accent="var(--a-green)", hash_=True):
    """defs: [(id, título)], data: {id: bloques}"""
    inner = "".join(f'<section data-sec="{html.escape(t)}" id="{i}">{blocks(data[i], root, accent)}</section>' for i, t in defs)
    return f'<div data-secs{" data-hash" if hash_ else ""}>{inner}</div>'

def head(lbl, title, sub="", color="var(--a-green)"):
    return (f'<div class="a-head" style="--c:{color}">{f"<span class=a-lbl>{esc(lbl)}</span>" if lbl else ""}'
            f'<h1 class="a-h a-h1">{esc(title)}</h1>{f"<p class=a-p style=color:var(--a-muted)>{esc(sub)}</p>" if sub else ""}</div>')

def row(href, name, sub, color, soft, root):
    tag = "a" if href else "div"
    attrs = f' href="{root}{href}"' if href else ""
    return (f'<{tag} class="a-row{"" if href else " static"}"{attrs}><span class="a-dot" style="--c:{color};--soft:{soft}"><i></i></span>'
            f'<span class="a-tx"><b>{esc(name)}</b><span>{esc(sub)}</span></span>{CHEV if href else ""}</{tag}>')

def tile(href, name, sub, color, soft, root, extra=""):
    return (f'<a class="a-card a-tile" href="{root}{href}"{extra}><span class="a-dot lg" style="--c:{color};--soft:{soft}"><i></i></span>'
            f'<span class="a-tx"><b>{esc(name)}</b><span>{esc(sub)}</span></span>{CHEV}</a>')

DISCLAIMER_PAC = '<p class="a-p a-foot" style="font-size:12.5px">Información general. No reemplaza la indicación de tu médico.</p>'

# ---------------------------------------------------------------- datos de navegación
CONDS = [
    ("salud/presion-alta.html", "Presión alta", "Hipertensión", "#C2534A", "#F8E6E4"),
    ("salud/diabetes.html", "Diabetes", "Qué es, alimentación y control", "#2A7A4B", "#E3F0E6"),
    (None, "Colesterol alto", "En preparación", "#7C5BA8", "#EEE8F6"),
    ("dietas/fodmap.html#paciente", "Colon irritable", "Dieta baja en FODMAP disponible", "#C98A1E", "#F7EEDC"),
    (None, "Enfermedad renal", "En preparación", "#3E78B8", "#E3EDF7"),
    (None, "Obesidad", "En preparación", "#5B746C", "#EEF2EF"),
]
CATS = [
    ("cv", "Corazón y presión", "Corazón", "#C2534A", "#F8E6E4", [("dash", "Dieta DASH", "Para bajar la presión arterial")]),
    ("gi", "Digestivo", "Digestivo", "#C98A1E", "#F7EEDC", [("fodmap", "Baja en FODMAP", "Colon irritable, en 3 etapas")]),
    ("ren", "Riñón", "Riñón", "#3E78B8", "#E3EDF7", []),
    ("met", "Metabolismo", "Metab.", "#7C5BA8", "#EEE8F6", []),
]
DIETS = {d[0]: (d[1], d[2], c[3], c[4]) for c in CATS for d in c[5]}

# ================================================================ INICIO (perfil, intro, inicio)
def build_index():
    r = ""
    pac_tiles = "".join(
        f'<a class="a-card a-tile" data-misitem="{k}" href="{r}dietas/{k}.html#paciente" hidden><span class="a-dot lg" style="--c:{v[2]};--soft:{v[3]}"><i></i></span>'
        f'<span class="a-tx"><b>{esc(v[0])}</b><span>{esc(v[1])}</span></span>{CHEV}</a>' for k, v in DIETS.items())
    tools = [
        ("clinica/evaluar.html", "Evaluar un paciente", "M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c0-4 3.6-6.5 8-6.5M16 16l2 2 4-4"),
        ("clinica/calculadoras.html", "Calculadoras", "M5 3h14v18H5zM8 7h8M8 12h2M12 12h2M8 16h2M12 16h2"),
        ("clinica/index.html#temas", "Temas clínicos", "M6 3h9l4 4v14H6zM9 12h7M9 16h7"),
        ("dietas/index.html#tripticos", "Trípticos para imprimir", "M3 5l6-2 6 2 6-2v16l-6 2-6-2-6 2zM9 3v16M15 5v16"),
    ]
    tgrid = "".join(f'<a class="a-card a-gtile" href="{r}{h}" style="min-height:112px"><span class="a-dot" style="--soft:var(--a-blue-soft);color:var(--a-blue)">'
                    f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="{ic}"/></svg></span><b>{esc(n)}</b></a>'
                    for h, n, ic in tools)
    cats = "".join(row("dietas/index.html#" + c[0], c[1], " · ".join(d[1] for d in c[5]) or "En preparación", c[3], c[4], r) for c in CATS)
    conds = "".join(row(h, n, s, c, so, r) for h, n, s, c, so in CONDS)
    body = f'''
<div class="a-solo tint" data-estado="perfil" hidden>
 <div class="a-panel">
  <div class="a-solohead">{LEAF}<span class="a-brand">Dietario</span><span class="a-proto">Prototipo</span></div>
  <div class="a-head" style="margin-top:24px"><h1 class="a-h" style="font-size:30px">¿Cómo vas a usar Dietario?</h1><p class="a-p a-muted">Puedes cambiarlo después desde el menú.</p></div>
  <button class="a-card a-tile" type="button" data-elegir="pac" style="padding:20px;align-items:flex-start">
   <span class="a-dot lg" style="width:48px;height:48px"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2A7A4B" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg></span>
   <span class="a-tx"><b>Soy paciente</b><span>Guías de alimentación en lenguaje simple, para leer e imprimir.</span></span></button>
  <a class="a-card a-tile" href="codigo.html" style="padding:20px;align-items:flex-start">
   <span class="a-dot lg" style="width:48px;height:48px;--soft:var(--a-blue-soft)"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2F5D8A" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 3v6a4 4 0 0 0 8 0V3"/><path d="M10 13v3a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="12" r="2"/></svg></span>
   <span class="a-tx"><b>Soy profesional de salud</b><span>Pautas con evidencia, trípticos, calculadoras y temas clínicos. Requiere código.</span></span></a>
  <p class="a-p a-foot" style="margin-top:auto;text-align:center;font-size:12.5px">Material educativo. No reemplaza la indicación de tu médico.</p>
 </div>
</div>

<div class="a-solo" data-estado="intro" hidden>
 <div class="a-panel">
  <div style="display:flex;justify-content:space-between;align-items:center"><div class="a-solohead">{LEAF}<span class="a-brand">Dietario</span></div>
   <button class="a-btn ghost" type="button" data-intro="saltar">Saltar</button></div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px">
   <div id="intro-ico" style="width:120px;height:120px;border-radius:32px;background:var(--a-green-soft);display:grid;place-items:center"></div>
   <span class="a-chip" id="intro-para" style="align-self:flex-start"></span>
   <h1 class="a-h" id="intro-t" style="font-size:30px"></h1>
   <p class="a-p" id="intro-d" style="font-size:17px;color:var(--a-ink2)"></p>
  </div>
  <div class="a-dots" id="intro-dots"><i></i><i></i><i></i></div>
  <button class="a-btn" type="button" data-intro="siguiente" id="intro-btn">Siguiente</button>
 </div>
</div>

<main class="a-body" data-estado="inicio" hidden>
 <div class="a-head"><h1 class="a-h a-h1" id="hola">Hola</h1><p class="a-p a-muted" id="hola-sub"></p></div>
 <div data-pac>
  <div class="a-banner" data-qrnuevo hidden><span style="flex:1"><b>¿Primera vez en Dietario?</b> Guarda tu dieta y conoce el resto de la app.</span></div>
 </div>
 <div data-pac style="display:flex;flex-direction:column;gap:12px">
  <div style="display:flex;justify-content:space-between;align-items:center"><span class="a-lbl">Mis dietas</span><a class="a-btn ghost" href="dietas/index.html">+ Agregar</a></div>
  <a class="a-card dash" href="dietas/index.html" id="sin-mis" style="color:inherit"><b>Aún no guardas ninguna dieta</b><span class="a-muted" style="font-size:14px">Busca la que te indicaron y guárdala para tenerla aquí.</span></a>
  {pac_tiles}
  <div class="a-card soft" id="combinar" hidden style="background:#F1EEF8;border-color:#DCD3EE;color:#38554C"><span class="a-lbl" style="color:#6A4C96">Próximamente</span><b class="a-h" style="font-size:17px;color:var(--a-ink)">Combinar mis dietas</b><span>Qué alimentos sirven para tus dos dietas a la vez y cuáles chocan entre sí. Si chocan, conviene conversarlo con tu nutricionista.</span></div>
  <div class="a-card soft" style="flex-direction:row;align-items:center;gap:12px"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" style="flex:none"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM18 18h3v3h-3z"/></svg><span><b>¿Te entregaron un tríptico?</b> Escanea su código QR y llegas directo a tu dieta.</span></div>
  <span class="a-lbl" style="margin-top:6px">Mi salud</span>
  <div class="a-card list">{conds}</div>
 </div>
 <div data-pro hidden style="display:flex;flex-direction:column;gap:12px">
  <span class="a-lbl">Nutrición clínica</span>
  <div class="a-grid2 a-tgrid">{tgrid}</div>
  <span class="a-lbl" style="margin-top:6px">Dietas por tema</span>
  <div class="a-card list">{cats}</div>
  <p class="a-p a-foot" style="font-size:13px">En preparación: mediterránea, sin gluten, sin lactosa, renal y más.</p>
 </div>
</main>
'''
    page("index.html", "Inicio", body, nav="home", top="Inicio", scripts=("inicio.js",),
         desc="Dietario: guías de alimentación con evidencia para pacientes y profesionales de salud.")

# ================================================================ NOSOTROS y CÓDIGO
def build_nosotros():
    body = f'''<main class="a-body">
 {head("", "Quiénes somos")}
 <div class="a-card"><b class="a-h" style="font-size:17px">[NOMBRE DEL PROYECTO / EQUIPO]</b><span>[Autor: nombre, título, institución] · [Revisión: nutricionista, especialistas]</span><span class="a-foot" style="font-size:13px">Cada ficha muestra su fecha de revisión y se actualiza una vez al año.</span></div>
 <div class="a-card"><b>Cómo se hace</b><span>Las recomendaciones vienen de guías clínicas vigentes y de los estudios que las respaldan. Ante discordancias, manda la guía más reciente.</span></div>
 <div class="a-card"><b>Aviso</b><span>Material educativo general. No reemplaza la indicación de tu médico ni la evaluación de un nutricionista. Las herramientas profesionales son apoyo y no sustituyen el juicio clínico.</span></div>
 <div class="a-card"><b>Tus datos</b><span>Dietario no tiene cuentas ni guarda datos en un servidor. Tu perfil, tus dietas guardadas y tu registro de presión y glicemia quedan solo en este dispositivo. Las calculadoras profesionales no guardan nada.</span></div>
 <div class="a-card list">
  <a class="a-row" href="index.html?perfil"><span class="a-tx"><b>Cambiar perfil</b><span id="perfil-actual"></span></span>{CHEV}</a>
  <a class="a-row" href="index.html?intro"><span class="a-tx"><b>Ver la introducción otra vez</b></span>{CHEV}</a>
 </div>
 <p class="a-p a-foot">Prototipo en revisión: contenido aún no validado por el equipo clínico.</p>
</main>
<script>document.getElementById("perfil-actual").textContent = "Ahora: " + ((window.localStorage && localStorage.getItem("dietario.perfil") === '"pro"') ? "profesional" : "paciente");</script>'''
    page("nosotros.html", "Nosotros", body, nav="nosotros")

def build_codigo():
    body = f'''<div class="a-solo">
 <div class="a-panel">
  <a class="a-btn ghost" href="index.html?perfil" style="align-self:flex-start">← Volver</a>
  <span class="a-dot" style="width:56px;height:56px;border-radius:16px;--soft:var(--a-blue-soft)"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2F5D8A" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg></span>
  <div class="a-head"><h1 class="a-h" style="font-size:28px">Acceso profesional</h1><p class="a-p" style="color:var(--a-ink2)">Ingresa el código de tu servicio o institución.</p></div>
  <form method="post" action="/api/acceso" id="f-codigo" style="display:flex;flex-direction:column;gap:16px">
   <label class="a-field"><span>Código</span><input class="a-code" name="codigo" autocomplete="off" autocapitalize="characters" required aria-describedby="cod-err"></label>
   <input type="hidden" name="next" id="cod-next" value="/clinica/index.html">
   <p class="a-p" id="cod-err" hidden style="color:#B03A2E;font-weight:700;font-size:14px;margin-top:-6px">Código incorrecto.</p>
   <button class="a-btn blue" type="submit">Entrar</button>
  </form>
  <p class="a-p a-foot" style="margin-top:auto;font-size:13.5px">¿No tienes código? Pídelo a [CONTACTO DEL PROYECTO]. Queda recordado en este dispositivo.</p>
 </div>
</div>
<script>
(function(){{
  var q = new URLSearchParams(location.search);
  if (q.has("error")) document.getElementById("cod-err").hidden = false;
  var n = q.get("next"); if (n && n.charAt(0) === "/" && n.charAt(1) !== "/") document.getElementById("cod-next").value = n;
}})();
</script>'''
    page("codigo.html", "Acceso profesional", body, bare=True)

# ================================================================ MI SALUD (paciente)
HTA = {
    "que": [["big", "140/90", ["Si en la consulta tu presión está sobre este valor en más de una ocasión, se habla de presión alta (hipertensión)."]],
            ["p", "", ["La presión alta casi nunca da síntomas, pero con los años daña el corazón, el cerebro y los riñones. Controlarla reduce el riesgo de infarto y de accidente cerebrovascular."]]],
    "ali": [["p", "", ["Lo que comes puede bajar tu presión casi tanto como un remedio."]],
            ["html", '<a class="a-card a-tile" href="../dietas/dash.html#paciente"><span class="a-dot lg" style="--c:#C2534A;--soft:#F8E6E4"><i></i></span><span class="a-tx"><b>Dieta DASH</b><span>Más verduras, frutas y lácteos descremados, menos sal</span></span>' + CHEV + '</a>'],
            ["soon", "Dieta hiposódica · en preparación", []]],
    "ctrl": [["html", '<div class="a-card"><b>Mídete en casa</b><span>Sentado, después de 5 minutos de reposo, con el brazo apoyado a la altura del corazón. Anota dos mediciones en la mañana y dos en la noche.</span><a class="a-btn sm" href="../registro/index.html" style="margin-top:4px">Abrir mi registro</a></div>'],
             ["card", "Tus remedios", ["Tómalos todos los días, aunque te sientas bien. No los suspendas sin hablar con tu médico."]],
             ["card", "Tu meta", ["La fija tu médico según tu edad y tus otras enfermedades. Anótala aquí: ____ / ____"]]],
    "alarma": [["warn", "⚠ Ve a urgencia si tienes", ["Dolor de pecho · falta de aire · debilidad o adormecimiento de un lado del cuerpo · dificultad para hablar · dolor de cabeza muy intenso y repentino"]],
               ["card", "Pide hora con tu médico si", ["Tu presión en casa está seguido sobre tu meta, o los remedios te dan mareos o hinchazón de piernas."]]],
}
KDEFS = [("que", "Qué es"), ("ali", "Mi alimentación"), ("ctrl", "Mi control"), ("alarma", "Cuándo consultar")]

def build_salud():
    r = "../"
    conds = "".join(row(h, n, s, c, so, r) for h, n, s, c, so in CONDS)
    page("salud/index.html", "Mi salud", f'<main class="a-body">{head("", "Mi salud", "Entiende tu condición y cómo cuidarte.")}<div class="a-card list">{conds}</div>{DISCLAIMER_PAC}</main>', nav="salud")
    page("salud/presion-alta.html", "Presión alta",
         f'<main class="a-body">{head("Mi salud", "Presión alta", "", "#C2534A")}{secciones(KDEFS, HTA, r, "#B5463E")}{DISCLAIMER_PAC}</main>',
         nav="salud", back="salud/index.html", top="Mi salud", desc="Presión alta: qué es, alimentación, control en casa y cuándo consultar.")
    pac = dict(DM["DM_PAC"])
    pac["ctrl"] = [(["btnReg", b[1], "?ver=gl"] if b[0] == "btnReg" else b) for b in pac["ctrl"]]
    page("salud/diabetes.html", "Diabetes",
         f'<main class="a-body">{head("Mi salud", "Diabetes", "", "#2A7A4B")}{secciones(KDEFS, pac, r)}{DISCLAIMER_PAC}</main>',
         nav="salud", back="salud/index.html", top="Mi salud", desc="Diabetes: qué es, alimentación, control y cuándo consultar.")

# ================================================================ REGISTRO (paciente)
def build_registro():
    body = '''<main class="a-body" id="reg">
 <div class="a-head"><h1 class="a-h a-h1">Mi registro</h1><p class="a-p a-muted">Se guarda solo en este teléfono. Nadie más lo ve hasta que tú lo muestres.</p></div>
 <div class="a-seg a-noprint" role="group" aria-label="Tipo de medición"><button type="button" data-tipo="pa" aria-pressed="true">Presión</button><button type="button" data-tipo="gl" aria-pressed="false">Glicemia</button></div>
 <div id="resumen"></div>
 <div id="alerta"></div>
 <form class="a-card a-noprint" id="form" hidden style="gap:12px;border-color:var(--a-green)" novalidate>
  <b class="a-h" style="font-size:17px">Nueva medición</b>
  <div class="a-fgrid3" data-solo="pa">
   <label class="a-field"><span>Máxima</span><input class="a-in" id="f-sys" inputmode="numeric" maxlength="3" autocomplete="off"></label>
   <label class="a-field"><span>Mínima</span><input class="a-in" id="f-dia" inputmode="numeric" maxlength="3" autocomplete="off"></label>
   <label class="a-field"><span>Pulso</span><input class="a-in" id="f-pul" inputmode="numeric" maxlength="3" placeholder="opc." autocomplete="off"></label>
  </div>
  <label class="a-field" data-solo="gl" hidden><span>Glicemia (mg/dL)</span><input class="a-in" id="f-gl" inputmode="numeric" maxlength="3" autocomplete="off"></label>
  <div class="a-field"><span>Momento</span><div class="a-pills" id="momentos"></div></div>
  <label class="a-field"><span>Fecha y hora</span><input class="a-in" id="f-t" type="datetime-local" style="font-size:16px"></label>
  <p class="a-p" id="f-err" hidden style="color:#B03A2E;font-weight:700;font-size:14px"></p>
  <div class="a-btns"><button class="a-btn line" type="button" id="cancelar">Cancelar</button><button class="a-btn" type="submit">Guardar</button></div>
 </form>
 <button class="a-btn a-noprint" type="button" id="agregar">+ Agregar medición</button>
 <div class="a-card list" id="lista"></div>
 <button class="a-btn dark a-noprint" type="button" id="llevar">Llevar a mi control</button>
 <div class="a-card a-noprint" id="llevar-panel" hidden style="gap:12px">
  <b class="a-h" style="font-size:17px">¿Cómo lo quieres llevar?</b>
  <button class="a-btn line" type="button" data-print style="justify-content:flex-start"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M7 8V3h10v5M7 17H5a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="7" y="14" width="10" height="7"/></svg>Imprimir o guardar PDF</button>
  <button class="a-btn line" type="button" id="enviar" style="justify-content:flex-start"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7M16 6l-4-4-4 4M12 2v14"/></svg>Enviar archivo (WhatsApp, correo)</button>
  <div style="display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:center;background:var(--a-bg);border-radius:12px;padding:12px">
   <div id="qr" style="width:132px;height:132px;background:#fff;border-radius:8px;display:grid;place-items:center"></div>
   <span style="font-size:13.5px"><b>Muestra este código a tu médico</b><br>Al escanearlo ve tus mediciones de los últimos 14 días. Los datos van dentro del código: no se suben a internet.</span>
  </div>
 </div>
 <details class="a-card a-noprint"><summary style="cursor:pointer;font-weight:800">Borrar mi registro</summary><p class="a-p a-muted" style="margin-top:8px;font-size:14px">Borra todas las mediciones de este teléfono. No se puede deshacer.</p><button class="a-btn line sm" type="button" id="borrar-todo" style="margin-top:8px;color:#A3342A">Borrar todo</button></details>
 <p class="a-p a-foot" style="font-size:12.5px">Tu registro no reemplaza tus controles. Ante valores fuera de rango, sigue las indicaciones de tu médico. Límites de referencia en revisión por el equipo clínico.</p>
 <div class="a-print-only" id="imp-pie"></div>
</main>'''
    page("registro/index.html", "Registro", body, nav="registro", top="Registro", scripts=("qrcode.js", "registro.js"),
         head='<style>.a-print-only{display:none}@media print{.a-print-only{display:block}}</style>', desc="Registro de presión arterial y glicemia en casa.")
    ver = '''<main class="a-body" id="ver">
 <div class="a-head"><span class="a-lbl">Registro del paciente</span><h1 class="a-h a-h1">Mediciones en casa</h1><p class="a-p a-muted" id="ver-sub"></p></div>
 <div id="ver-out"></div>
 <p class="a-p a-foot">Estos datos venían dentro del código QR: no se guardaron en ningún servidor ni en este dispositivo.</p>
</main>'''
    out = page("registro/ver.html", "Registro compartido", ver, nav="", top="Registro compartido", scripts=("registro.js",), bodyattrs=' data-ver')
    t = open(out, encoding="utf-8").read().replace('<nav class="a-nav"></nav>', "").replace('class="a-app"', 'class="a-app a-bare"')
    open(out, "w", encoding="utf-8").write(t)  # quien escanea (el médico) no necesita la navegación del paciente

# ================================================================ DIETAS
def build_dietas():
    r = "../"
    seg = "".join(f'<button type="button" data-cat="{c[0]}" aria-pressed="{"true" if i == 0 else "false"}">{esc(c[2])}</button>' for i, c in enumerate(CATS))
    lists = ""
    for i, c in enumerate(CATS):
        items = "".join(tile(f"dietas/{d[0]}.html#paciente", d[1], d[2], c[3], c[4], r) for d in c[5]) or \
            f'<div class="a-card dash"><b>En preparación</b><span>Pronto agregaremos dietas de este tema.</span></div>'
        lists += f'<div data-catlist="{c[0]}" style="display:flex;flex-direction:column;gap:10px"{"" if i == 0 else " hidden"}><span class="a-lbl" style="color:{c[3]}">{esc(c[1])}</span>{items}</div>'
    trip = "".join(
        f'<div class="a-kv"><b>{esc(DIETS[k][0])}</b><span><a href="{r}tripticos/{k}.pdf" style="font-weight:800;color:var(--a-blue)">Color</a> · '
        f'<a href="{r}tripticos/{k}-bn.pdf" style="font-weight:800;color:var(--a-blue)">Blanco y negro</a></span></div>' for k in DIETS)
    body = f'''<main class="a-body">
 {head("", "Dietas", "Elige un tema y luego la dieta.")}
 <div class="a-seg" role="group" aria-label="Temas">{seg}</div>
 {lists}
 <section id="tripticos" data-pro hidden class="a-card" style="gap:4px"><b>Trípticos para imprimir</b><span class="a-muted" style="font-size:13.5px;margin-bottom:6px">Para entregar y explicar en la consulta. Traen un QR a la ficha del paciente.</span>{trip}</section>
</main>
<script>
(function(){{
  var seg = document.querySelector(".a-seg");
  function show(k){{
    if (!document.querySelector('[data-catlist="' + k + '"]')) return false;
    seg.querySelectorAll("[data-cat]").forEach(function(b){{ b.setAttribute("aria-pressed", b.getAttribute("data-cat") === k); }});
    document.querySelectorAll("[data-catlist]").forEach(function(l){{ l.hidden = l.getAttribute("data-catlist") !== k; }});
    return true;
  }}
  seg.addEventListener("click", function(e){{ var b = e.target.closest("[data-cat]"); if (b) {{ show(b.getAttribute("data-cat")); history.replaceState(null, "", "#" + b.getAttribute("data-cat")); }} }});
  var h = location.hash.slice(1); if (h === "tripticos") {{ var t = document.getElementById("tripticos"); if (!t.hidden) t.scrollIntoView(); }} else if (h) show(h);
}})();
</script>'''
    page("dietas/index.html", "Dietas", body, nav="dietas")

# ================================================================ CLÍNICA (profesional)
TEMAS_NC = [
    ("clinica/realimentacion.html", "Síndrome de realimentación", "#C3412D"),
    ("clinica/requerimientos.html", "Peso de cálculo y requerimientos", "#2F5D8A"),
    ("clinica/renal.html", "Enfermedad renal", "#3E78B8"),
    ("clinica/uci.html", "Paciente crítico (UCI)", "#2F5D8A"),
    ("clinica/pancreatitis.html", "Pancreatitis aguda", "#A8721A"),
]
TEMAS_MET = [("clinica/diabetes.html", "Diabetes", "#2A7A4B"), (None, "Hipertensión · en preparación", "#C2534A"), (None, "Dislipidemia · en preparación", "#7C5BA8")]
CALCS = [
    ("requerimientos", "Requerimientos", "Energía y proteína por situación clínica"),
    ("gasto", "Gasto energético", "Mifflin-St Jeor y Harris-Benedict"),
    ("realimentacion", "Síndrome de realimentación", "Riesgo y plan de inicio día a día"),
    ("enteral", "Nutrición enteral", "Volumen y velocidad de infusión"),
    ("insulina", "Insulina en el hospitalizado", "Basal, corrección y corticoides"),
    ("osmolaridad", "Sodio corregido y osmolaridad", "Crisis hiperglicémicas"),
]

def gtile(href, name, color, r):
    if not href:
        return f'<div class="a-card a-gtile" style="--c:{color};border-style:dashed;color:var(--a-muted)"><span class="a-pip"></span><b>{esc(name)}</b></div>'
    return f'<a class="a-card a-gtile" href="{r}{href}" style="--c:{color}"><span class="a-pip"></span><b>{esc(name)}</b></a>'

def build_clinica_hub():
    r = "../"
    calcs = "".join(f'<a class="a-row" href="calculadoras.html#{k}" style="min-height:52px"><span class="a-tx"><b style="font-size:15px">{esc(n)}</b><span>{esc(s)}</span></span>{CHEV}</a>' for k, n, s in CALCS)
    body = f'''<main class="a-body">
 {head("", "Nutrición y metabolismo", "Requerimientos, cálculos y manejo metabólico.")}
 <a class="a-card a-tile" href="evaluar.html" style="background:var(--a-blue);border-color:var(--a-blue);color:#fff;padding:18px">
  <span class="a-dot lg" style="width:46px;height:46px;--soft:rgba(255,255,255,.16)"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="7" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5M16 16l2 2 4-4"/></svg></span>
  <span class="a-tx"><b style="color:#fff">Evaluar un paciente</b><span style="color:#fff;opacity:.9">Ingresa los datos una vez: requerimientos y alertas según sus riesgos.</span></span></a>
 <span class="a-lbl">Calculadoras</span>
 <div class="a-card list">{calcs}</div>
 <span class="a-lbl">Metabólico</span>
 <div class="a-grid2">{"".join(gtile(h, n, c, r) for h, n, c in TEMAS_MET)}</div>
 <span class="a-lbl" id="temas">Temas de nutrición clínica</span>
 <div class="a-grid2">{"".join(gtile(h, n, c, r) for h, n, c in TEMAS_NC)}</div>
 <p class="a-p a-foot">Apoyo a la decisión clínica: no reemplaza el juicio del tratante ni la evaluación por nutricionista.</p>
</main>'''
    page("clinica/index.html", "Clínica", body, nav="clinica", top="Nutrición y metabolismo")

def tema(path, title, grupo, color, defs, data, sub=""):
    r = "../"
    page(path, title, f'<main class="a-body">{head(grupo, title, sub, color)}{secciones(defs, data, r, color)}'
         '<p class="a-p a-foot">Apoyo a la decisión clínica: no reemplaza el juicio del tratante.</p></main>',
         nav="clinica", back="clinica/index.html", top="Clínica")

def build_temas():
    dmdefs = [("metas", "Metas y monitoreo"), ("ingreso", "Al ingreso: qué esquema"), ("basal", "Insulina basal"), ("corr", "Insulina de corrección"),
              ("cort", "Corticoides"), ("ayuno", "Ayuno y pabellón"), ("nut", "Nutrición enteral y parenteral"), ("hipo", "Hipoglicemia"),
              ("crisis", "Crisis hiperglicémicas"), ("amb", "Inicio de insulina ambulatorio"), ("alta", "Al alta"), ("fuentes", "Fuentes")]
    pro = dict(DM["DM_PRO"])
    tema("clinica/diabetes.html", "Diabetes", "Metabólico", "#2A7A4B", dmdefs, pro)

    A20, H21 = "ASPEN 2020 (da Silva)", "ESPEN hospitalaria 2021"
    realim = {
        "quien": [["table", "Criterios de riesgo", "0.9fr 1.1fr 1.2fr", ["Criterio", "Moderado (2)", "Significativo (1)"], [
            ["IMC", "16–18,5", "<16"], ["Pérdida de peso", "5 % en 1 mes", "7,5 % en 3 meses o >10 % en 6"],
            ["Ingesta", "Nula 5–6 días; <75 % >7 días en enfermedad aguda; <75 % >1 mes", "Nula >7 días; <50 % >5 días en enfermedad aguda; <50 % >1 mes"],
            ["K, P o Mg", "Mínimamente bajos o reposición mínima reciente", "Moderada o significativamente bajos, o reposición importante"],
            ["Grasa subcutánea", "Pérdida moderada", "Pérdida severa"], ["Masa muscular", "Pérdida leve o moderada", "Pérdida severa"],
            ["Comorbilidad de alto riesgo", "Moderada", "Severa"]], A20 + ", tabla 3"],
            ["btn", "Calcular riesgo y plan de inicio", "ref"]],
        "inicio": [["card", "Cómo partir", ["10–20 kcal/kg o 100–150 g de dextrosa las primeras 24 h, contando sueros y diluciones.", "Subir 33 % de la meta cada 1–2 días.", "ESPEN hospitalaria 2021 propone 5–15 kcal/kg según el riesgo."], A20 + "; " + H21],
                   ["card", "Tiamina y vitaminas", ["Tiamina 100 mg antes de alimentar o de iniciar sueros glucosados.", "100 mg/día por 5–7 días en ayuno severo, alcoholismo u otro riesgo alto.", "ESPEN micronutrientes 2024: 100–300 mg/día desde el ingreso si hubo hipoingesta o alcohol.", "Multivitamínico por ≥10 días."], A20 + "; ESPEN micronutrientes 2024"]],
        "vigilar": [["card", "Monitoreo", ["✓ K, P y Mg antes de iniciar y cada 12 h los primeros 3 días en riesgo alto.", "✓ Si están muy bajos, corregir antes de partir.", "✓ Signos vitales cada 4 h las primeras 24 h.", "✓ Peso y balance hídrico diarios."], A20],
                    ["warn", "Si los electrolitos caen o cuesta corregirlos", ["Bajar 50 % las calorías y volver a subir 33 % de la meta cada 1–2 días."], A20],
                    ["card", "Definición", ["Caída de P, K o Mg de 10–20 % (leve), 20–30 % (moderada) o >30 % o falla de órgano (grave), en los 5 días siguientes a reiniciar el aporte."], A20]],
        "evitar": [["card", "Errores frecuentes", ["✕ Partir con la meta completa.", "✕ Olvidar la dextrosa de sueros y diluciones.", "✕ Alimentar sin tiamina previa.", "✕ Seguir subiendo si los electrolitos caen."], ""]],
        "fuentes": [["card", "", ["ASPEN 2020: consenso de síndrome de realimentación (da Silva et al.), tablas 3 y 6.", "ESPEN hospitalaria 2021 (Thibault et al.).", "ESPEN micronutrientes 2024 (Berger et al.)."], ""]],
    }
    tema("clinica/realimentacion.html", "Síndrome de realimentación", "Nutrición clínica", "#C3412D",
         [("quien", "Quién está en riesgo"), ("inicio", "Cómo iniciar"), ("vigilar", "Qué vigilar"), ("evitar", "Qué evitar"), ("fuentes", "Fuentes")], realim)

    req = {
        "peso": [["table", "Peso de referencia", "1fr 1.5fr", ["Situación", "Peso"], [
            ["Sala, IMC <30", "Peso real"],
            ["Sala, obesidad", "Ajustado = ideal + 0,33 × (real − ideal); ideal = peso con IMC 25. Definido para la proteína"],
            ["UCI, IMC >25", "Ideal + 20–25 % del exceso; ideal = 0,9 × (talla − 100) en hombres, (talla − 106) en mujeres"],
            ["Renal", "Habitual o previo al ingreso; si no, ideal. Nunca el real"],
            ["Cirrosis con ascitis", "Ideal según talla"]], "ESPEN hospitalaria 2021, 3.12 · UCI 2023 · renal 2024, R18 · hígado 2020"],
            ["note", "", ["Las dos definiciones de peso ajustado no son intercambiables: 0,33 del exceso en sala (ESPEN 2021) y 20–25 % en UCI (ESPEN 2023)."]]],
        "req": [["table", "Por situación clínica", "1.2fr 1fr 1fr", ["Situación", "kcal/kg/d", "Proteína g/kg/d"], [
            ["Sala, sin riesgo nutricional", "25", "0,8–1,0"], ["Sala, con riesgo nutricional", "30", "≥1,2"],
            ["Polimórbido ≥65 años", "27 (muy bajo peso: 30, llegando lento)", "1,2–1,5; TFGe <30 sin TRR: 0,8"],
            ["Adulto mayor", "30, ajustado al caso", "≥1,0; 1,2–1,5 con enfermedad; hasta 2,0 si es severa"],
            ["UCI", "20–25; 1ª semana <70 %", "1,3, progresiva"], ["Renal", "20–30", "Según escenario"],
            ["Cirrosis", "30–35", "1,2–1,5 (1,5 si desnutrido)"], ["Obesidad hospitalizada", "Sin dieta hipocalórica", "Con peso ajustado"]],
            "ESPEN hospitalaria 2021 R15 y R31 · polimórbido 2024 · geriatría 2019 · UCI 2023 · renal 2024 · hígado 2020"],
            ["note", "", ["Cuando hay calorimetría indirecta, manda la medición."]],
            ["html", '<a class="a-btn blue" href="calculadoras.html#requerimientos">Calcular para un paciente</a>']],
        "fuentes": [["card", "", ["ESPEN hospitalaria 2021 (Thibault).", "ESPEN polimórbido 2024 (Wunderle).", "ESPEN UCI 2023 (Singer).", "ESPEN renal 2024 (Sabatino).", "ESPEN hígado 2020 (Bischoff).", "ESPEN geriatría 2019 (Volkert)."], ""]],
    }
    tema("clinica/requerimientos.html", "Peso de cálculo y requerimientos", "Nutrición clínica", "#2F5D8A",
         [("peso", "Peso de cálculo"), ("req", "Requerimientos por situación"), ("fuentes", "Fuentes")], req)

    renal = {
        "prot": [["table", "Proteína por escenario", "1.6fr 1fr", ["Escenario", "g/kg/d"], [
            ["ERC sin enfermedad aguda", "0,6–0,8"], ["ERC en hemodiálisis crónica, sin enfermedad aguda", "≥1,2"],
            ["IRA o IRA sobre ERC, sin enfermedad crítica", "0,8–1,0"], ["Aguda o crítica sin terapia de reemplazo", "Partir con 1,0 y subir hasta 1,3"],
            ["Crítico con diálisis intermitente", "1,3–1,5"], ["Crítico con terapia continua o prolongada", "1,5–1,7"]], "ESPEN renal 2024, R18"],
            ["card", "Claves", ["No bajar la proteína para retrasar la diálisis.", "Energía 20–30 kcal/kg como punto de partida; sumar las kcal de citrato, lactato y glucosa de la terapia.", "Peso: habitual o previo al ingreso; nunca el real por la sobrecarga de volumen."], "ESPEN renal 2024"]],
        "fuentes": [["card", "", ["ESPEN renal 2024 (Sabatino et al.)."], ""]],
    }
    tema("clinica/renal.html", "Enfermedad renal", "Nutrición clínica", "#3E78B8", [("prot", "Proteína y energía"), ("fuentes", "Fuentes")], renal)

    uci = {
        "claves": [["card", "Energía y proteína", ["Preferir calorimetría indirecta. Sin ella, 20–25 kcal/kg y menos del 70 % de lo estimado la primera semana.",
                                                   "Proteína 1,3 g/kg/d, progresiva; en obesidad, con peso ajustado o guiada por nitrógeno urinario."], "ESPEN UCI 2023"],
                   ["card", "Sustratos", ["Glucosa EV ≤5 mg/kg/min.", "Lípidos EV hasta 1 g/kg/d, con tolerancia hasta 1,5.", "Descontar el propofol: 1,1 kcal/mL de lípido."], "ESPEN UCI 2023"],
                   ["card", "Vía oral", ["Si el paciente come, la vía oral basta cuando cubre ≥70 % de lo requerido entre los días 3 y 7."], "ESPEN UCI 2023"]],
        "fuentes": [["card", "", ["ESPEN UCI 2023 (Singer et al.)."], ""]],
    }
    tema("clinica/uci.html", "Paciente crítico (UCI)", "Nutrición clínica", "#2F5D8A", [("claves", "Claves"), ("fuentes", "Fuentes")], uci)

    panc = {
        "claves": [["card", "Alimentación", ["Leve: comer en 24–48 h según tolerancia, directo a dieta sólida baja en grasa, sin escalera de líquidos.",
                                            "Moderada o severa: la nutrición enteral previene infecciones. Sonda nasogástrica equivalente a la nasoyeyunal, en infusión continua.",
                                            "Nutrición parenteral solo si la enteral no es posible, no se tolera o no cubre las calorías."], "ACG 2024"],
                   ["card", "Hidratación", ["Cristaloide isotónico, de preferencia Ringer lactato.", "1,5 mL/kg/h sin hipovolemia; bolo de 10 mL/kg si la hay.", "Reevaluar a las 6 h y durante 24–48 h."], "ACG 2024"],
                   ["note", "", ["Triglicéridos >1.000 mg/dL ya son causa posible."]]],
        "fuentes": [["card", "", ["ACG 2024: guía de pancreatitis aguda."], ""]],
    }
    tema("clinica/pancreatitis.html", "Pancreatitis aguda", "Nutrición clínica", "#A8721A", [("claves", "Claves"), ("fuentes", "Fuentes")], panc)


# ================================================================ CALCULADORAS y EVALUAR (profesional)
CALC_HEAD = '<link rel="stylesheet" href="../assets/ficha.css"><link rel="stylesheet" href="../assets/herramientas.css"><link rel="stylesheet" href="../assets/app.css">'

def fld(id_, label, unit, attrs, value=""):
    v = f' value="{value}"' if value != "" else ""
    return f'<div class="fld"><label for="{id_}">{label}</label><div class="unit"><input id="{id_}" type="number" {attrs}{v}><span>{unit}</span></div></div>'

PACIENTE_FORM = f'''<form id="f" class="pt" autocomplete="off" novalidate>
  <div class="pt-head"><b>Paciente</b><span class="example" id="exnote">Datos de ejemplo</span></div>
  <div class="pt-grid">
   <div class="fld"><span class="lbl">Sexo</span><div class="seg2" role="radiogroup" aria-label="Sexo">
    <label><input type="radio" name="sexo" id="sexo-m" value="M" checked>H</label><label><input type="radio" name="sexo" id="sexo-f" value="F">M</label></div></div>
   {fld("edad", "Edad", "años", 'inputmode="numeric" min="18" max="110"', "25")}
   {fld("talla", "Talla", "cm", 'inputmode="decimal" min="120" max="230" step="0.5"', "175")}
   {fld("peso", "Peso actual", "kg", 'inputmode="decimal" min="25" max="350" step="0.1"', "76")}
   {fld("habitual", "Peso habitual", "kg", 'inputmode="decimal" min="25" max="350" step="0.1" placeholder="opc."')}
  </div>
  <div class="kpis" id="kpis"></div>
 </form>'''

def build_calculadoras():
    r = "../"
    situ = "".join(f'<option value="{k}"{" selected" if k == "uci" else ""}>{v}</option>' for k, v in [
        ("sala_riesgo", "Sala, con riesgo nutricional"), ("sala_sin_riesgo", "Sala, sin riesgo nutricional"), ("polimorbido", "Paciente médico polimórbido ≥65 años"),
        ("geriatria", "Adulto mayor (guía geriátrica)"), ("uci", "UCI / paciente crítico"), ("renal", "Enfermedad renal (ERC o IRA)"), ("cirrosis", "Cirrosis")])
    pills = lambda name, opts, cur: "".join(f'<button type="button" class="a-pill" data-g="{name}" data-v="{v}" aria-pressed="{"true" if v == cur else "false"}">{t}</button>' for v, t in opts)
    body = f'''<main class="a-body" style="max-width:1000px">
 {head("Herramienta profesional · adultos hospitalizados", "Calculadoras", "", "var(--a-blue)")}
 <div id="pac-box">{PACIENTE_FORM}</div>
 <div data-secs data-hash id="calcs">
 <section data-sec="Requerimientos" id="requerimientos">
  <div class="calc">
   <div class="fset">
    <div class="fld"><label for="situacion">Situación clínica</label><select id="situacion" form="f">{situ}</select></div>
    <div class="fld" id="box-renal" hidden><label for="renal">Escenario renal</label><select id="renal" form="f">
     <option value="erc_estable">ERC sin enfermedad aguda</option><option value="erc_hd">ERC en hemodiálisis crónica</option>
     <option value="ira_no_critico">IRA o IRA sobre ERC, no crítico</option><option value="agudo_sin_trr" selected>Agudo o crítico, sin terapia de reemplazo</option>
     <option value="critico_hdi">Crítico con diálisis intermitente</option><option value="critico_trrc">Crítico con terapia continua</option></select></div>
    <div id="box-cirrosis" hidden class="stack"><label class="chk"><input type="checkbox" id="ascitis" form="f">Ascitis</label><label class="chk"><input type="checkbox" id="desnutrido" form="f">Desnutrido o con pérdida muscular</label></div>
    <label class="chk" id="box-tfg" hidden><input type="checkbox" id="tfg" form="f">TFGe &lt;30 sin terapia de reemplazo</label>
    <div class="fld" id="box-geria" hidden><label for="enfermedad">Enfermedad</label><select id="enfermedad" form="f">
     <option value="ninguna">Sin enfermedad relevante</option><option value="aguda" selected>Aguda o crónica</option><option value="severa">Severa, lesión o desnutrición</option></select></div>
   </div>
   <div class="results" aria-live="polite" id="results"></div>
  </div>
 </section>
 <section data-sec="Gasto energético (Harris-Benedict)" id="gasto">
  <div class="blk">
   <div class="mini" id="geb-out"></div>
   <div class="frow"><div class="fld"><label for="f-act">Factor de actividad</label><input id="f-act" type="number" inputmode="decimal" step="0.05" min="1" max="2" value="1.2"></div>
    <div class="fld"><label for="f-est">Factor de estrés</label><input id="f-est" type="number" inputmode="decimal" step="0.05" min="1" max="2" value="1.0"></div></div>
   <div class="mini" id="get-out"></div>
   <p class="src">Mifflin-St Jeor (1990) y Harris-Benedict revisada (Roza y Shizgal, 1984). GET = GEB × actividad × estrés; los factores los ingresas tú: las guías no fijan sus valores.</p>
  </div>
  <div class="a-card note">Referencia de uso habitual. Las guías prefieren calorimetría o kcal/kg: en UCI estas ecuaciones pueden errar hasta 60 % (ESPEN UCI 2023) y Harris-Benedict sobrestimó 29 % en adultos mayores polimórbidos (ESPEN 2024). "Evaluar un paciente" usa las kcal/kg de las guías.</div>
 </section>
 <section data-sec="Síndrome de realimentación" id="realimentacion">
  <div class="rsteps">
   <div class="blk"><div class="bh"><span class="num">1</span><h2>¿Está en riesgo?</h2>
     <details class="pop"><summary aria-label="Cómo se clasifica">?</summary><div>Criterios ASPEN 2020. <b>Significativo:</b> 1 criterio de la columna significativa. <b>Moderado:</b> 2 criterios de la columna moderada. El IMC se toma de los datos del paciente.</div></details></div>
    <div class="crit" id="crit"></div><div id="refeed-out"></div></div>
   <div class="blk"><div class="bh"><span class="num">2</span><h2>Plan de inicio</h2>
     <details class="pop"><summary aria-label="Regla">?</summary><div>ASPEN 2020: 10–20 kcal/kg o 100–150 g de dextrosa las primeras 24 h, contando sueros y diluciones; subir 33 % de la meta cada 1–2 días. ESPEN hospitalaria 2021 propone 5–15 kcal/kg según el riesgo.</div></details></div>
    <div class="frow3">
     <div class="fld"><label for="rf-ini">Inicio</label><select id="rf-ini"><option value="10" selected>10 kcal/kg</option><option value="15">15 kcal/kg</option><option value="20">20 kcal/kg</option></select></div>
     <div class="fld"><label for="rf-meta">Meta</label><div class="unit"><input id="rf-meta" type="number" inputmode="numeric" min="300" step="10"><span>kcal</span></div></div>
     <div class="fld"><label for="rf-cada">Subir cada</label><select id="rf-cada"><option value="1">1 día</option><option value="2" selected>2 días</option></select></div>
    </div><div id="plan"></div></div>
   <div class="blk"><div class="bh"><span class="num">3</span><h2>Tiamina y electrolitos</h2></div>
    <ul class="checks">
     <li><b>Tiamina 100 mg</b> antes de alimentar o de iniciar sueros glucosados.</li>
     <li><b>Tiamina 100 mg/día por 5–7 días</b> si hay ayuno severo, alcoholismo u otro riesgo alto de déficit.</li>
     <li><b>Multivitamínico</b> por ≥10 días (en NP, diario mientras dure).</li>
     <li><b>K, P y Mg</b> antes de iniciar y cada 12 h los primeros 3 días en riesgo alto. Si están muy bajos, corregir antes de partir.</li>
     <li><b>Si caen o cuesta corregirlos:</b> bajar 50 % las calorías y volver a subir 33 % de la meta cada 1–2 días.</li>
     <li><b>Signos vitales</b> cada 4 h las primeras 24 h; peso y balance hídrico diarios.</li>
    </ul>
    <p class="src">ASPEN 2020 (da Silva), tabla 6. Más detalle en el tema <a href="realimentacion.html" style="color:var(--tool)">Síndrome de realimentación</a>.</p></div>
  </div>
 </section>
 <section data-sec="Nutrición enteral" id="enteral">
  <div class="blk narrow"><div class="bh"><h2>Velocidad de nutrición enteral</h2>
    <details class="pop"><summary aria-label="Cómo se calcula">?</summary><div>Volumen = meta de kcal ÷ densidad; velocidad = volumen ÷ horas. Toma la densidad y la proteína por litro de la etiqueta del producto que se dispensa.</div></details></div>
   <div class="frow">
    <div class="fld"><label for="ne-kcal">Meta</label><div class="unit"><input id="ne-kcal" type="number" inputmode="numeric" min="0" step="10" value="1900"><span>kcal</span></div></div>
    <div class="fld"><label for="ne-dens">Densidad</label><div class="unit"><input id="ne-dens" type="number" inputmode="decimal" min="0.5" max="2.5" step="0.05" value="1.2"><span>kcal/mL</span></div></div>
    <div class="fld"><label for="ne-h">Horas</label><div class="unit"><input id="ne-h" type="number" inputmode="numeric" min="1" max="24" value="24"><span>h</span></div></div>
    <div class="fld"><label for="ne-p">Proteína</label><div class="unit"><input id="ne-p" type="number" inputmode="decimal" min="0" step="1" placeholder="opc."><span>g/L</span></div></div>
   </div>
   <label class="chk"><input type="checkbox" id="ne-sync" checked>Usar la meta de Requerimientos</label>
   <div class="mini" id="ne-out"></div></div>
 </section>
 <section data-sec="Insulina en el hospitalizado" id="insulina" class="a-blue">
  <div class="a-seg" role="group" aria-label="Modo"><button type="button" data-modo="basal" aria-pressed="true">Basal y corrección</button><button type="button" data-modo="cort" aria-pressed="false">Con corticoides</button></div>
  <label class="a-field"><span>Peso real (kg)</span><input class="a-in" id="i-peso" inputmode="decimal" value="80" autocomplete="off"></label>
  <div data-modo-box="basal" style="display:flex;flex-direction:column;gap:16px">
   <div class="a-card" style="gap:12px">
    <span class="a-lbl">¿Usaba insulina basal?</span><div class="a-pills">{pills("prev", [("no", "No"), ("si", "Sí")], "no")}</div>
    <label class="a-field" id="i-prev-box" hidden><span>Dosis basal previa (UI/día)</span><input class="a-in" id="i-prev" inputmode="decimal" autocomplete="off"></label>
    <span class="a-lbl">Sensibilidad</span><div class="a-pills">{pills("sens", [("sensible", "Sensible"), ("normal", "Habitual"), ("resistente", "Resistente")], "normal")}</div>
    <span class="a-foot">Sensible: mayor frágil, ERC avanzada, IMC &lt;20, baja ingesta o ayuno prolongado. Resistente: IMC &gt;30, diabetes de larga data, requerimientos altos o corticoides.</span>
    <span class="a-lbl">Glicemias sobre 200</span><div class="a-pills">{pills("hi", [("0", "No"), ("1", "Sí")], "0")}</div>
    <span class="a-lbl">Insulina basal</span><div class="a-pills">{pills("tipo", [("glargina", "Glargina U100"), ("nph", "NPH")], "glargina")}</div>
   </div>
   <div id="ib-out" aria-live="polite" style="display:flex;flex-direction:column;gap:16px"></div>
  </div>
  <div data-modo-box="cort" hidden style="display:flex;flex-direction:column;gap:16px">
   <div class="a-card" style="gap:12px">
    <span class="a-lbl">Grupo</span><div class="a-pills">{pills("grupo", [("1", "Grupo 1 · 0,3"), ("2", "Grupo 2 · 0,5")], "2")}</div>
    <span class="a-foot" id="grupo-txt"></span>
    <span class="a-lbl">Corticoide</span><div class="a-pills">{pills("cort", [("prednisona", "Prednisona"), ("metilprednisolona", "Metilprednisolona"), ("hidrocortisona", "Hidrocortisona"), ("dexametasona", "Dexametasona"), ("betametasona", "Betametasona")], "prednisona")}</div>
    <label class="a-field"><span>Dosis diaria (mg)</span><input class="a-in" id="i-cd" inputmode="decimal" value="60" autocomplete="off"></label>
    <span class="a-lbl">Insulina prandial</span><div class="a-pills">{pills("prand", [("analogo", "Análogo rápido · 4 comidas"), ("cristalina", "Cristalina · 3 comidas")], "analogo")}</div>
   </div>
   <div id="ic-out" aria-live="polite" style="display:flex;flex-direction:column;gap:16px"></div>
  </div>
  <div class="a-card note">Cálculo de apoyo según el consenso; la indicación final es del médico tratante. No se guarda ningún dato. Más detalle en el tema <a href="diabetes.html#basal" style="font-weight:800">Diabetes</a>.</div>
 </section>
 <section data-sec="Sodio corregido y osmolaridad" id="osmolaridad" class="a-blue">
  <div class="a-fgrid"><label class="a-field"><span>Sodio medido (mEq/L)</span><input class="a-in" id="o-na" inputmode="decimal" value="138" autocomplete="off"></label>
   <label class="a-field"><span>Glicemia (mg/dL)</span><input class="a-in" id="o-gl" inputmode="decimal" value="720" autocomplete="off"></label></div>
  <div id="o-out" aria-live="polite" style="display:flex;flex-direction:column;gap:16px"></div>
  <p class="a-p a-foot">Consenso SOCHIDIAB 2026, cap. 6. Sospecha y estudio en el tema <a href="diabetes.html#crisis" style="font-weight:800">Diabetes → Crisis hiperglicémicas</a>.</p>
 </section>
 </div>
 <details class="more foot"><summary>Fuentes</summary><div>ESPEN hospitalaria 2021 (Thibault), ESPEN polimórbido 2024 (Wunderle), ESPEN UCI 2023 (Singer), ESPEN renal 2024 (Sabatino), ESPEN hígado 2020 (Bischoff), ESPEN geriatría 2019 (Volkert), ASPEN realimentación 2020 (da Silva), ESPEN micronutrientes 2024 (Berger), Consenso intrahospitalario SOCHIDIAB 2026. Revisión: noviembre 2026.</div></details>
</main>'''
    page("clinica/calculadoras.html", "Calculadoras", body, nav="clinica", back="clinica/index.html", top="Calculadoras",
         head=CALC_HEAD, scripts=("nutricalc.js", "calculadoras.js"), desc="Calculadoras de nutrición e insulina para adultos hospitalizados.")

def build_evaluar():
    ctx = [("riesgo", "Riesgo nutricional"), ("ayuno", "Ingesta <50 % por >5 días"), ("uci", "UCI"), ("erc", "Enfermedad renal"), ("cirr", "Cirrosis")]
    chips = "".join(f'<button type="button" class="a-pill" data-ctx="{k}" aria-pressed="false">{esc(t)}</button>' for k, t in ctx)
    body = f'''<main class="a-body a-blue" style="max-width:1000px">
 {head("Profesional", "Evaluar un paciente", "Ingresa los datos una vez: requerimientos según su situación y alertas por riesgo. No se guarda nada.", "var(--a-blue)")}
 {PACIENTE_FORM}
 <span class="a-lbl">Contexto clínico</span>
 <div class="a-pills" id="ctx">{chips}</div>
 <div id="ctx-extra" style="display:flex;flex-direction:column;gap:10px">
  <div class="fld" id="ev-renal-box" hidden><label for="ev-renal">Escenario renal</label><select id="ev-renal">
   <option value="erc_estable">ERC sin enfermedad aguda</option><option value="erc_hd">ERC en hemodiálisis crónica</option>
   <option value="ira_no_critico">IRA o IRA sobre ERC, no crítico</option><option value="agudo_sin_trr" selected>Agudo o crítico, sin terapia de reemplazo</option>
   <option value="critico_hdi">Crítico con diálisis intermitente</option><option value="critico_trrc">Crítico con terapia continua</option></select></div>
  <label class="chk" id="ev-ascitis-box" hidden><input type="checkbox" id="ev-ascitis">Ascitis</label>
 </div>
 <span class="a-lbl">Alertas</span>
 <div id="ev-alertas" style="display:flex;flex-direction:column;gap:10px"></div>
 <span class="a-lbl">Requerimientos</span>
 <div id="ev-res" class="a-grid2"></div>
 <p class="a-p a-foot" id="ev-src"></p>
 <a class="a-btn line" href="calculadoras.html#requerimientos">Ajustar en la calculadora completa</a>
</main>'''
    page("clinica/evaluar.html", "Evaluar un paciente", body, nav="clinica", back="clinica/index.html", top="Evaluar paciente",
         head=CALC_HEAD, scripts=("nutricalc.js", "evaluar.js"), desc="Evaluación nutricional transitoria del paciente hospitalizado.")

if __name__ == "__main__":
    build_index(); build_nosotros(); build_codigo(); build_salud(); build_registro(); build_dietas(); build_clinica_hub(); build_temas()
    build_calculadoras(); build_evaluar()
    print("ok")
