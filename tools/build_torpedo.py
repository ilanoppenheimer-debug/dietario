"""Genera site/herramientas/nutricion-hospitalaria.html (torpedo) desde los datos de este archivo.
Regla: solo cifras de guías vigentes; las fórmulas clásicas del manual 2014 van marcadas como tales.
Uso: python3 tools/build_torpedo.py"""
import os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site/herramientas/nutricion-hospitalaria.html")

E = html.escape
def table(head, rows):
    th = "".join(f"<th>{E(h)}</th>" for h in head)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f'<td data-label="{E(head[i])}"><div class="c">{c}</div></td>' for i, c in enumerate(r)) + "</tr>"
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

T = lambda s: f'<span class="tag">{s}</span>'
OLD = '<span class="tag old">Manual 2014</span>'

S = []  # (id, título, html)

S.append(("peso", "Peso de cálculo", table(
    ["Situación", "Peso de referencia", "Fuente"], [
    ["Sala, IMC &lt;30", "Peso real", T("ESPEN hosp. 2021")],
    ["Sala, obesidad", "Peso ajustado = ideal + 0,33 × (real − ideal); ideal = peso con IMC 25. Definido para la proteína", T("ESPEN hosp. 2021, 3.12")],
    ["UCI, IMC &gt;25", "Ideal + 20–25 % del exceso; ideal = 0,9 × (talla cm − 100) en hombres, (talla − 106) en mujeres", T("ESPEN UCI 2023")],
    ["Renal", "Peso habitual o previo al ingreso; si no, ideal. Nunca el real (sobrecarga de volumen)", T("ESPEN renal 2024, R18")],
    ["Cirrosis con ascitis", "Peso ideal según talla", T("ESPEN hígado 2020")],
    ]) + '<p class="src">Las dos definiciones de peso ajustado no son intercambiables: 0,33 del exceso en sala (ESPEN 2021) y 20–25 % en UCI (ESPEN 2023).</p>'))

S.append(("req", "Requerimientos por situación", table(
    ["Situación", "Energía kcal/kg/d", "Proteína g/kg/d", "Fuente"], [
    ["Sala, sin riesgo nutricional", "25", "0,8–1,0", T("ESPEN hosp. 2021, R15")],
    ["Sala, con riesgo nutricional", "30", "≥1,2", T("ESPEN hosp. 2021, R15")],
    ["Paciente médico polimórbido ≥65 años", "27 (muy bajo peso: 30, llegando lento)", "1,2–1,5; TFGe &lt;30 sin TRR: 0,8", T("ESPEN polimórbido 2024")],
    ["Adulto mayor", "30, ajustado al caso", "≥1,0; 1,2–1,5 con enfermedad; hasta 2,0 si es severa", T("ESPEN geriatría 2019")],
    ["UCI", "20–25 sin calorimetría; 1ª semana &lt;70 % de lo estimado", "1,3, progresiva", T("ESPEN UCI 2023")],
    ["Renal", "20–30 como punto de partida", "Según escenario (tabla siguiente)", T("ESPEN renal 2024")],
    ["Cirrosis", "30–35", "1,2–1,5 (1,5 si desnutrido)", T("ESPEN hígado 2020")],
    ["Obesidad hospitalizada", "No indicar dieta hipocalórica", "Con peso ajustado", T("ESPEN hosp. 2021, R31")],
    ]) + '<p class="src">Cuando hay calorimetría indirecta, manda la medición.</p>'))

S.append(("renal", "Proteína en el paciente renal", table(
    ["Escenario", "Proteína g/kg/d"], [
    ["ERC sin enfermedad aguda", "0,6–0,8"],
    ["ERC en hemodiálisis crónica, sin enfermedad aguda", "≥1,2"],
    ["IRA o IRA sobre ERC, sin enfermedad crítica", "0,8–1,0"],
    ["Enfermedad aguda o crítica sin terapia de reemplazo", "Partir con 1,0 y subir hasta 1,3"],
    ["Crítico con diálisis intermitente", "1,3–1,5"],
    ["Crítico con terapia continua o prolongada", "1,5–1,7"],
    ]) + '<p class="src">' + T("ESPEN renal 2024, R18") + ' No bajar la proteína para retrasar la diálisis. Sumar las kcal de citrato, lactato y glucosa de la terapia.</p>'))

S.append(("realim", "Síndrome de realimentación", table(
    ["Criterio", "Riesgo moderado (2 criterios)", "Riesgo significativo (1 criterio)"], [
    ["IMC", "16–18,5", "&lt;16"],
    ["Pérdida de peso", "5 % en 1 mes", "7,5 % en 3 meses o &gt;10 % en 6 meses"],
    ["Ingesta", "Nula 5–6 días; &lt;75 % &gt;7 días en enfermedad aguda; &lt;75 % &gt;1 mes", "Nula &gt;7 días; &lt;50 % &gt;5 días en enfermedad aguda; &lt;50 % &gt;1 mes"],
    ["K, P o Mg antes de alimentar", "Mínimamente bajos, o reposición mínima reciente", "Moderada o significativamente bajos, o reposición importante reciente"],
    ["Grasa subcutánea", "Pérdida moderada", "Pérdida severa"],
    ["Masa muscular", "Pérdida leve o moderada", "Pérdida severa"],
    ["Comorbilidad de alto riesgo", "Moderada", "Severa"],
    ]) + '''<ul class="lst">
<li><b>Inicio:</b> 10–20 kcal/kg o 100–150 g de dextrosa las primeras 24 h, contando sueros y diluciones; subir 33 % de la meta cada 1–2 días. ESPEN hospitalaria 2021 propone 5–15 kcal/kg según el riesgo.</li>
<li><b>Electrolitos:</b> K, P y Mg antes de iniciar y cada 12 h los primeros 3 días en riesgo alto. Si están muy bajos, corregir antes de partir. Si caen o cuesta corregirlos, bajar 50 % las calorías y volver a subir 33 % cada 1–2 días.</li>
<li><b>Tiamina:</b> 100 mg antes de alimentar o de iniciar sueros glucosados; 100 mg/día por 5–7 días en ayuno severo, alcoholismo u otro riesgo alto. ESPEN micronutrientes 2024: 100–300 mg/día desde el ingreso si hubo hipoingesta o alcohol. Multivitamínico por ≥10 días.</li>
<li><b>Definición:</b> caída de P, K o Mg de 10–20 % (leve), 20–30 % (moderada) o &gt;30 % o falla de órgano (grave) en los 5 días siguientes a reiniciar la alimentación.</li>
</ul><p class="src">''' + T("ASPEN 2020") + " " + T("ESPEN hosp. 2021") + "</p>"))

S.append(("uci", "UCI: claves", '''<ul class="lst">
<li>Preferir calorimetría indirecta. Sin ella, 20–25 kcal/kg y menos del 70 % de lo estimado la primera semana.</li>
<li>Proteína 1,3 g/kg/d, en forma progresiva; en obesidad, con peso ajustado o guiada por nitrógeno urinario.</li>
<li>Glucosa EV ≤5 mg/kg/min. Lípidos EV hasta 1 g/kg/d, con tolerancia hasta 1,5.</li>
<li>Descontar el propofol: 1,1 kcal/mL de lípido.</li>
<li>Si el paciente come, la vía oral es suficiente cuando cubre ≥70 % de lo requerido entre los días 3 y 7.</li>
</ul><p class="src">''' + T("ESPEN UCI 2023") + "</p>"))

S.append(("pancreatitis", "Pancreatitis aguda", '''<ul class="lst">
<li><b>Leve:</b> comer en 24–48 h según tolerancia, directo a dieta sólida baja en grasa, sin escalera de líquidos.</li>
<li><b>Moderada o severa:</b> la nutrición enteral previene infecciones. Sonda nasogástrica equivalente a la nasoyeyunal, en infusión continua. Nutrición parenteral solo si la enteral no es posible, no se tolera o no cubre las calorías.</li>
<li><b>Hidratación:</b> cristaloide isotónico, de preferencia Ringer lactato; 1,5 mL/kg/h sin hipovolemia (bolo de 10 mL/kg si la hay); reevaluar a las 6 h y por 24–48 h.</li>
<li>Triglicéridos &gt;1.000 mg/dL ya son causa posible.</li>
</ul><p class="src">''' + T("ACG 2024") + "</p>"))

S.append(("dm", "Diabético hospitalizado", table(
    ["Tema", "Regla"], [
    ["Cuándo tratar", "Insulina con glicemia persistente ≥180 mg/dL (2 veces en 24 h)"],
    ["Meta", "UCI 140–180 mg/dL. Sala 100–180. Hasta 250 en enfermedad terminal, falla renal avanzada o diálisis, o alto riesgo de hipoglicemia"],
    ["Monitoreo", "Antes de cada comida; sin ingesta, cada 4–6 h; con insulina EV, cada 30 min a 2 h. A1c al ingreso si no hay una de los últimos 3 meses"],
    ["Esquema", "UCI: infusión EV. Sala y come: basal + prandial + corrección. Sin ingesta: basal ± corrección. No usar solo corrección"],
    ["Dosis inicial", "0,3–0,6 U/kg/d, o 80 % de la dosis de la casa; mitad basal, mitad nutricional. En DM1 nunca suspender la basal"],
    ["NE continua", "Mantener basal; 1 U por 10–15 g de hidratos de la fórmula más corrección. Si se interrumpe la NE, dextrosa EV"],
    ["NP", "Insulina regular en la bolsa, 1 U por 10 g de dextrosa, si usó &gt;20 U de corrección en 24 h"],
    ["Hipoglicemia (&lt;70)", "15 g de hidrato rápido; repetir y medir cada 15 min hasta &gt;70"],
    ]) + '<p class="src">' + T("ADA Standards of Care 2026, cap. 16") + " Dieta con hidratos controlados; ADA no fija un porcentaje. No indicar dieta hipocalórica.</p>"))

S.append(("formulas", "Fórmulas clásicas", table(
    ["Fórmula", "Uso"], [
    ["% pérdida de peso = (habitual − actual) × 100 ÷ habitual", "Significativa: 1–2 % en 1 semana; 5 % en 1 mes; 7,5 % en 3 meses; 10 % en 6 meses"],
    ["IMC = kg ÷ m²", "&lt;18,5 bajo peso; 25 sobrepeso; 30 obesidad"],
    ["Balance N = proteína ÷ 6,25 − (NUU + 4)", "Meta +2 a +4 g/d; en el crítico, el menos negativo posible"],
    ["Proteína para BN neutro = (NUU + 4) × 6,25", "NUU 16 g/d → 125 g/d de proteína"],
    ["NUU sin aporte proteico (g/d)", "&lt;5 normal; 5–10 hipercatabolismo leve; 11–15 moderado; &gt;15 severo"],
    ["1 g N = 6,25 g de proteína", "—"],
    ["Densidad energética", "Aminoácidos 4 kcal/g; dextrosa 3,4 kcal/g; lípidos al 10/20/30 % = 1,1/2,1/3,1 kcal/mL"],
    ]) + '<p class="src">' + OLD + " Conceptos y aritmética del Manual de Terapia Nutricional UDD 2014. Los requerimientos de ese manual fueron reemplazados por las guías de arriba.</p>"))

S.append(("cambios", "Qué cambió respecto del manual 2014", '''<ul class="lst changes">
<li><b>Crítico:</b> proteína 1,3 g/kg (no 1,5 con techo 2,5); energía &lt;70 % la primera semana si se estima con ecuaciones.</li>
<li><b>Sala:</b> 30 kcal/kg y ≥1,2 g/kg con riesgo; en el polimórbido ≥65 años, 27 kcal/kg y 1,2–1,5 g/kg.</li>
<li><b>Peso ajustado:</b> ideal + 0,33 del exceso en sala; ideal + 20–25 % en UCI.</li>
<li><b>Obeso hospitalizado:</b> no hipocalórico.</li>
<li><b>Renal:</b> no restringir proteína en el agudo ni para retrasar la diálisis; peso habitual, no real.</li>
<li><b>Cirrosis:</b> no restringir proteína, tampoco con encefalopatía; con ascitis, peso ideal.</li>
<li><b>Lípidos EV:</b> hasta 1 g/kg/d, con tolerancia hasta 1,5.</li>
<li><b>Realimentación:</b> inicio 10–20 kcal/kg (ASPEN) o 5–15 (ESPEN), subiendo 33 % cada 1–2 días.</li>
<li><b>Pancreatitis leve:</b> comer en 24–48 h, sin ayuno de varios días.</li>
</ul>'''))

toc = "".join(f'<a href="#{i}">{t}</a>' for i, t, _ in S)
secs = "\n".join(f'<section id="{i}"><h2>{t}</h2>{h}</section>' for i, t, h in S)

page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Nutrición en el hospitalizado · Guías de Alimentación</title>
<meta name="description" content="Torpedo de nutrición en el adulto hospitalizado: peso de cálculo, requerimientos, realimentación, UCI, renal, pancreatitis y diabetes.">
<meta name="robots" content="noindex">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="../assets/ficha.css">
<link rel="stylesheet" href="../assets/herramientas.css">
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><symbol id="i-leaf" viewBox="0 0 32 32"><path d="M5 27C5 13 13 5 27 5c0 14-8 22-22 22z" fill="currentColor"/><path d="M5 27L20 12" stroke="var(--leaf)" stroke-width="2" stroke-linecap="round"/></symbol></defs></svg>
<div class="proto"><b>Prototipo en revisión.</b> Referencia para profesionales; contenido aún no validado por el equipo clínico.</div>
<header class="sitebar">
  <div class="in" style="max-width:1100px">
    <a class="home" href="../index.html"><span class="mark"><svg><use href="#i-leaf"/></svg></span>Guías de Alimentación</a>
    <nav class="toolnav" aria-label="Herramientas">
      <a href="calculadora.html">Calculadora</a>
      <a href="nutricion-hospitalaria.html" aria-current="page">Torpedo hospitalizado</a>
    </nav>
  </div>
</header>
<div class="page">
<main class="torp">
  <div class="tool-head">
    <span class="eyebrow">Torpedo · Adultos hospitalizados</span>
    <h1>Nutrición en el hospitalizado</h1>
    <p>Cifras de las guías vigentes, con su fuente al lado. Para calcular un caso, usa la <a href="calculadora.html" style="color:var(--tool);font-weight:700">calculadora</a>.</p>
  </div>
  <nav class="toc" aria-label="Contenido">{toc}</nav>
{secs}
  <footer style="font-size:.84rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px">
    Guías: ESPEN hospitalaria 2021, ESPEN polimórbido 2024, ESPEN UCI 2023, ESPEN renal 2024, ESPEN hígado 2020, ESPEN geriatría 2019, ESPEN micronutrientes 2024, ASPEN realimentación 2020, ACG pancreatitis aguda 2024, ADA Standards of Care 2026. Revisión: noviembre 2026.
  </footer>
</main>
</div>
</body>
</html>
'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(page)
print("ok", OUT)
