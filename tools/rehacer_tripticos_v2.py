"""Tríptico v2: más informativo, menos para llenar, con QR a la ficha de la dieta.
Reescribe src/tripticos/dash.html y fodmap.html conservando portada, solapa y estilos."""
import re, os, qrcode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src/tripticos")
BASE = "https://dietario.vercel.app/"

def qr_svg(url):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    q.add_data(url); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    d = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="-2 -2 {n+4} {n+4}" shape-rendering="crispEdges" aria-label="Código QR"><rect x="-2" y="-2" width="{n+4}" height="{n+4}" fill="#fff"/><path d="{d}" fill="#000"/></svg>'

CSS = """
.qr{display:grid;grid-template-columns:25mm 1fr;gap:3mm;align-items:center;border:0.4mm solid var(--ink);border-radius:3mm;padding:2.6mm}
.qr svg{width:25mm;height:25mm;display:block}
.qr b{font-family:var(--f-display);font-size:10pt;display:block;margin-bottom:1mm}
.qr p{font-size:7.8pt;line-height:1.3}
.qr .u{font-family:var(--f-mono);font-size:7.6pt;margin-top:1.2mm;display:block;font-weight:500}
.menu{display:flex;flex-direction:column}
.menu > div{display:grid;grid-template-columns:18mm 1fr;gap:2mm;font-size:8.2pt;line-height:1.32;padding:1.5mm 0;border-top:0.25mm solid var(--line)}
.menu > div:first-child{border-top:0}
.menu b{font-family:var(--f-mono);font-size:6.3pt;letter-spacing:.05em;color:var(--leaf);padding-top:.5mm;font-weight:500}
.lst{margin:0;padding-left:3.6mm;font-size:8.2pt;line-height:1.33}
.lst li{margin:0.5mm 0}
.lst.two{columns:2;column-gap:5mm}
.lst.two li{break-inside:avoid}
.light .lst{font-size:8.1pt}
.light{padding-top:1.6mm;padding-bottom:1.6mm}
.light h3{font-size:9.6pt}
.doc{border:0.3mm dashed var(--muted);border-radius:3mm;padding:2.6mm;display:flex;flex-direction:column;gap:2.2mm}
.doc h3{font-size:8.8pt}
.doc .row{display:flex;gap:2mm;align-items:flex-end;font-size:8pt}
.doc .row span:first-child{font-weight:700;white-space:nowrap}
.doc .fill{flex:1;min-width:0;height:4mm}
.doc .ln{border-bottom:0.3mm solid var(--ink);height:5.2mm}
.grp h3{font-size:9pt;margin-bottom:0.6mm}
.grp p{font-size:8.2pt;line-height:1.33}
.stp{display:flex;flex-direction:column;gap:1.6mm;counter-reset:s}
.stp div{display:grid;grid-template-columns:5.5mm 1fr;gap:2mm;font-size:8.2pt;line-height:1.32;counter-increment:s}
.stp div::before{content:counter(s);font-family:var(--f-display);font-weight:800;font-size:8pt;width:5mm;height:5mm;border-radius:50%;border:0.35mm solid var(--ink);display:grid;place-items:center}
.ttab{width:100%;border-collapse:collapse;font-size:7.8pt}
.ttab th{font-size:6pt;padding:1mm 1mm;border-bottom:0.4mm solid var(--ink)}
.ttab td{height:auto;padding:1.1mm 1mm;border-bottom:0.25mm solid var(--line)}
.stage2{display:grid;grid-template-columns:8mm 1fr;gap:2.5mm;align-items:start;border-left:1.4mm solid var(--c);padding:0.6mm 0 0.6mm 2.6mm}
.stage2 .n{font-family:var(--f-display);font-weight:800;font-size:16pt;color:var(--c);line-height:1}
.stage2 h3{font-size:9pt}
.stage2 p{font-size:8pt;line-height:1.32}
"""
BN_EXTRA = """
.stage2{border-left-color:#000!important}.stage2 .n{color:#000!important}
.menu b{color:#000}
"""

DOC_BOX = '''<div class="doc">
      <h3>Indicaciones de tu médico</h3>
      <div class="ln"></div><div class="ln"></div>
      {extra}
      <div class="row"><span>Próximo control:</span><span class="fill" style="border-bottom:0.3mm solid var(--ink)"></span></div>
    </div>'''

def qr_box(slug, nombre):
    return f'''<div class="qr">{qr_svg(BASE + slug)}<div><b>Guía completa en tu celular</b><p>Escanea el código para ver la ficha de la {nombre}, con más ejemplos y trucos. También la puedes imprimir.</p><span class="u">dietario.vercel.app/{slug}</span></div></div>'''

def split(src):
    head = src[:src.index("<!-- ============ EXTERIOR")]
    head = head.replace("</style>", CSS + "</style>", 1)
    solapa = re.search(r"(<!-- Solapa.*?)\n  <!-- Contratapa -->", src, re.S).group(1)
    portada = re.search(r"(<!-- Portada -->.*?)\n</div>\n\n<!-- ============ INTERIOR", src, re.S).group(1)
    return head, solapa, portada

def write(slug, head, ext, inter, tail="</body></html>\n"):
    html = head + "<!-- ============ EXTERIOR ============ -->\n<div class=\"sheet out\">\n  " + ext + "\n</div>\n\n<!-- ============ INTERIOR ============ -->\n<div class=\"sheet in\">\n" + inter + "\n</div>\n" + tail
    open(os.path.join(SRC, slug + ".html"), "w").write(html)

# ---------------- DASH ----------------
s = open(os.path.join(SRC, "dash.html")).read()
head, solapa, portada = split(s)
script = s[s.index("<script>"):s.index("</script>") + 9]
script = script.replace("""var d="";for(var i=0;i<g[6];i++)d+='<span class="dot"></span>';""", "")
script = script.replace("""'<div class="dots" style="color:var('+g[1]+')">'+d+(g[7]?'<span class="wk">por semana</span>':'')+'</div></div>';""", "'<span></span></div>';")
contra = f'''<!-- Contratapa -->
  <div class="p">
    <span class="eb">Para recordar</span>
    <h2>Un día DASH a la chilena</h2>
    <div class="menu">
      <div><b>DESAYUNO</b><span>Avena cocida en leche descremada, con plátano y un puñadito de nueces.</span></div>
      <div><b>MEDIA MAÑANA</b><span>Una manzana o una naranja.</span></div>
      <div><b>ALMUERZO</b><span>Lentejas con zapallo y verduras, sin cubo de caldo. Ensalada chilena con limón y aceite de oliva. Fruta de postre.</span></div>
      <div><b>ONCE</b><span>Pan integral pequeño con palta y quesillo. Té o café sin azúcar.</span></div>
      <div><b>CENA</b><span>Pollo al horno sin piel, verduras salteadas y ½ taza de arroz integral.</span></div>
      <div><b>NOCHE</b><span>Un yogurt descremado sin azúcar.</span></div>
    </div>
    {qr_box("dash", "dieta DASH")}
    {DOC_BOX.format(extra='<div class="row"><span>Mi meta de presión: menos de</span><span class="fill" style="border-bottom:0.3mm solid var(--ink)"></span></div>')}
  </div>'''
inter = '''  <!-- Panel 1: porciones -->
  <div class="p">
    <span class="eb">Cuánto comer</span>
    <h2>Tus porciones del día</h2>
    <p class="muted" style="font-size:7.6pt">Referencia para un adulto de unas 2.000 calorías. Tu médico o nutricionista puede ajustarla.</p>
    <div id="groups"></div>
  </div>

  <!-- Panel 2: sal -->
  <div class="p">
    <span class="eb">Lo más importante</span>
    <div class="salt">
      <svg viewBox="0 0 100 120"><path d="M30 40c0-14 8-26 20-26s20 12 20 26v62c0 6-4 10-10 10H40c-6 0-10-4-10-10z" fill="#fff" stroke="#8C2B47" stroke-width="4"/><path d="M30 40h40" stroke="#8C2B47" stroke-width="4"/><circle cx="42" cy="26" r="2.5" fill="#8C2B47"/><circle cx="50" cy="22" r="2.5" fill="#8C2B47"/><circle cx="58" cy="26" r="2.5" fill="#8C2B47"/><text x="50" y="88" text-anchor="middle" font-family="Bricolage Grotesque" font-weight="800" font-size="20" fill="#8C2B47">5 g</text></svg>
      <div>
        <h3>Sal: menos de 1 cucharadita al día</h3>
        <p style="font-size:8pt">En total, sumando la que ya viene en los alimentos. La mayor parte no sale del salero.</p>
      </div>
    </div>
    <div class="grp"><h3>Dónde se esconde la sal</h3>
      <ul class="lst two"><li>Pan y marraqueta</li><li>Jamón, salame, vienesas</li><li>Quesos maduros</li><li>Cubos de caldo y sopas en sobre</li><li>Papas fritas y snacks</li><li>Salsa de soya y kétchup</li></ul></div>
    <div style="display:flex;gap:2.5mm;align-items:center"><span class="sello">ALTO EN<br>SODIO</span><p style="font-size:8pt">Si ves este sello, busca otra opción o cómelo solo de vez en cuando.</p></div>
    <div class="grp"><h3>Da sabor sin sal</h3><p>Ajo, cebolla, limón, orégano, comino, pimienta, hierbas frescas y merkén sin sal.</p></div>
    <div class="grp"><h3>Trucos que funcionan</h3>
      <ul class="lst"><li>Saca el salero de la mesa.</li><li>Agrega una verdura al almuerzo y otra a la cena.</li><li>Compara el sodio de las etiquetas entre marcas.</li><li>Cocina en casa más seguido.</li><li>El gusto se acostumbra a menos sal en 2 a 3 semanas.</li></ul></div>
  </div>

  <!-- Panel 3: semáforo -->
  <div class="p">
    <span class="eb">Qué comer</span>
    <h2>El semáforo</h2>
    <div class="light l-go" style="--c:var(--go)"><h3>Todos los días</h3>
      <ul class="lst two"><li>Verduras de todos los colores</li><li>Frutas enteras</li><li>Porotos, lentejas, garbanzos</li><li>Avena, arroz y pan integral</li><li>Leche y yogurt descremados</li><li>Pescado</li><li>Pollo sin piel, huevo</li><li>Nueces y almendras sin sal</li><li>Aceite de oliva o canola</li><li>Palta</li></ul></div>
    <div class="light l-slow" style="--c:var(--slow)"><h3>Con moderación</h3>
      <ul class="lst"><li>Pan blanco y marraqueta (traen sal)</li><li>Quesos: mejor quesillo o queso fresco</li><li>Carne roja magra, 1 a 2 veces por semana</li><li>Jugos de fruta: mejor la fruta entera</li><li>Mantequilla</li><li>Legumbres en lata: enjuágalas antes</li></ul></div>
    <div class="light l-stop" style="--c:var(--stop)"><h3>Evitar</h3>
      <ul class="lst two"><li>Jamón, salame, longaniza</li><li>Cubos de caldo, sopas en sobre</li><li>Snacks salados</li><li>Comida rápida</li><li>Bebidas y jugos azucarados</li><li>Pasteles y galletas</li></ul></div>
    <div class="warn">
      <h3>Avisa a tu médico si…</h3>
      <ul><li>Tienes enfermedad renal o el potasio alto.</li><li>Te sientes mareado al levantarte.</li><li>Tienes diabetes con insulina, celiaquía o intolerancia a la lactosa.</li></ul>
    </div>
  </div>'''
write("dash", head, solapa + "\n\n  " + contra + "\n\n  " + portada, inter, script + "\n</body>\n</html>\n")

# ---------------- FODMAP ----------------
s = open(os.path.join(SRC, "fodmap.html")).read()
head, solapa, portada = split(s)
panel1 = re.search(r"(  <!-- Panel 1: cambios -->.*?)\n\n  <!-- Panel 2", s, re.S).group(1)
panel1 = panel1.replace("<p class=\"muted\" style=\"font-size:7.6pt\">Carnes, pescados, huevos y aceites no tienen FODMAP. Ojo con cebolla y ajo en polvo e inulina en caldos, aliños y panes.</p>", "")
contra = f'''<!-- Contratapa -->
  <div class="p">
    <span class="eb">El plan</span>
    <h2>Las 3 etapas</h2>
    <div class="stage2" style="--c:var(--beet)"><span class="n">1</span><div><h3>Quitar · 2 a 6 semanas</h3><p>Cambia los alimentos altos en FODMAP por otros bajos. Si no mejoras en este plazo, la dieta no es para ti: vuelve a comer normal y consúltalo.</p></div></div>
    <div class="stage2" style="--c:var(--slow)"><span class="n">2</span><div><h3>Probar de a uno · 6 a 8 semanas</h3><p>Vuelve a comer un grupo a la vez, en cantidad creciente, y anota cómo te sientes.</p></div></div>
    <div class="stage2" style="--c:var(--leaf)"><span class="n">3</span><div><h3>Tu dieta · para siempre</h3><p>Come de todo y limita solo lo que te hizo mal, en la cantidad que te hizo mal.</p></div></div>
    {qr_box("fodmap", "dieta baja en FODMAP")}
    {DOC_BOX.format(extra='<div class="row"><span>Etapa 1 por</span><span class="fill" style="border-bottom:0.3mm solid var(--ink);flex:0 0 14mm"></span><span>semanas · Nutricionista:</span><span class="fill" style="border-bottom:0.3mm solid var(--ink)"></span></div>')}
  </div>'''
inter = panel1 + '''

  <!-- Panel 2: comer tranquilo -->
  <div class="p">
    <span class="eb">Etapa 1</span>
    <h2>Puedes comer tranquilo</h2>
    <div class="light l-go" style="--c:var(--go)"><h3>Proteínas y grasas</h3><p class="grp" style="font-size:8.2pt">Carnes, pollo, pescado, huevo, tofu firme y aceites. No tienen FODMAP.</p></div>
    <div class="light l-go" style="--c:var(--go)"><h3>Cereales y tubérculos</h3><p style="font-size:8.2pt">Arroz, papa, avena, quínoa, pan sin gluten.</p></div>
    <div class="light l-go" style="--c:var(--go)"><h3>Verduras</h3><p style="font-size:8.2pt">Zanahoria, zapallo italiano, pepino, lechuga, tomate, espinaca, pimentón, parte verde del cebollín.</p></div>
    <div class="light l-go" style="--c:var(--go)"><h3>Frutas (una por vez)</h3><p style="font-size:8.2pt">Plátano firme, naranja, mandarina, kiwi, frutillas, piña.</p></div>
    <div class="light l-go" style="--c:var(--go)"><h3>Lácteos</h3><p style="font-size:8.2pt">Leche y yogurt sin lactosa, quesos maduros (gauda, mantecoso, parmesano).</p></div>
    <div class="grp"><h3>✕ Revisa las etiquetas</h3><p>Evita productos con cebolla o ajo en polvo, inulina, fibra de achicoria, miel o endulzantes terminados en "-ol" (sorbitol, manitol). Suelen estar en caldos, aliños, panes y dulces "sin azúcar".</p></div>
    <div class="grp"><h3>Errores frecuentes</h3><ul class="lst"><li>Quedarse en la etapa 1 para siempre.</li><li>Confundirla con una dieta sin gluten.</li><li>Quitar más alimentos de los necesarios.</li></ul></div>
  </div>

  <!-- Panel 3: reintroducción -->
  <div class="p">
    <span class="eb">Etapa 2</span>
    <h2>Cómo volver a probar</h2>
    <div class="stp">
      <div><span><b>Un grupo a la vez.</b> Sigue la dieta y agrega solo el alimento de prueba.</span></div>
      <div><span><b>3 días, de menos a más</b>, como en la tabla. Anota tus síntomas.</span></div>
      <div><span><b>Si te cae mal, para.</b> Espera a estar sin síntomas.</span></div>
      <div><span><b>Descansa 2 a 3 días</b> antes del siguiente grupo.</span></div>
    </div>
    <table class="ttab">
      <thead><tr><th>Grupo · alimento</th><th>Día 1</th><th>Día 2</th><th>Día 3</th></tr></thead>
      <tbody>
        <tr><td><b>Lactosa</b> · leche</td><td>¼ taza</td><td>½ taza</td><td>1 taza</td></tr>
        <tr><td><b>Fructosa</b> · miel</td><td>1 cdta</td><td>2 cdtas</td><td>1 cda</td></tr>
        <tr><td><b>Sorbitol</b> · palta</td><td>¼</td><td>⅓</td><td>½</td></tr>
        <tr><td><b>Manitol</b> · champiñón</td><td>¼ taza</td><td>½ taza</td><td>1 taza</td></tr>
        <tr><td><b>Trigo</b> · pan molde</td><td>½ reb.</td><td>1 reb.</td><td>2 reb.</td></tr>
        <tr><td><b>Cebolla</b> cocida</td><td>1 cda</td><td>2 cdas</td><td>¼ taza</td></tr>
        <tr><td><b>Ajo</b></td><td>¼ diente</td><td>½</td><td>1 diente</td></tr>
        <tr><td><b>Legumbres</b> · lentejas</td><td>¼ taza</td><td>½ taza</td><td>¾ taza</td></tr>
      </tbody>
    </table>
    <div class="warn">
      <h3>Consulta antes si…</h3>
      <ul><li>Bajas de peso sin querer o ves sangre en las deposiciones.</li><li>Los síntomas te despiertan en la noche.</li><li>Has tenido problemas con la comida o con tu peso.</li></ul>
    </div>
  </div>'''
write("fodmap", head, solapa + "\n\n  " + contra + "\n\n  " + portada, inter)

bn = open(os.path.join(SRC, "bn.css")).read()
if ".stage2" not in bn:
    open(os.path.join(SRC, "bn.css"), "a").write(BN_EXTRA)
print("ok")
