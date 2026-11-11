/* Dietario · calculadoras profesionales (usa nutricalc.js). Cálculo transitorio: no se guarda nada. */
(function(){
  var C = window.NutriCalc, $ = function(id){ return document.getElementById(id); };
  var nf = function(x, d){ return x == null ? "" : x.toLocaleString("es-CL", {maximumFractionDigits: d == null ? 0 : d}); };
  var num = function(id){ var v = parseFloat(String($(id).value).replace(",", ".")); return isNaN(v) ? null : v; };
  var last = null, metaTocada = false;

  /* ---------- Criterios de realimentación ---------- */
  var CRIT = [
    {k:"imc", t:"IMC", m:"16–18,5", s:"&lt;16", auto:true},
    {k:"perdida", t:"Pérdida de peso", m:"5 % en 1 mes", s:"7,5 % en 3 meses o &gt;10 % en 6 meses"},
    {k:"ingesta", t:"Ingesta", m:"Nula 5–6 días; &lt;75 % por &gt;7 días en enfermedad aguda; &lt;75 % por &gt;1 mes", s:"Nula &gt;7 días; &lt;50 % por &gt;5 días en enfermedad aguda; &lt;50 % por &gt;1 mes"},
    {k:"electrolitos", t:"K, P o Mg antes de alimentar", m:"Mínimamente bajos, o reposición mínima reciente", s:"Moderada o significativamente bajos, o reposición importante reciente"},
    {k:"grasa", t:"Grasa subcutánea", m:"Pérdida moderada", s:"Pérdida severa"},
    {k:"musculo", t:"Masa muscular", m:"Pérdida leve o moderada", s:"Pérdida severa"},
    {k:"comorbilidad", t:"Comorbilidad de riesgo", m:"Moderada", s:"Severa", hint:"Alcohol o drogas, cáncer, malabsorción, disfagia, trastorno alimentario, cirugía bariátrica, ayuno prolongado, entre otras."}
  ];
  $("crit").innerHTML = CRIT.map(function(c){
    var opts = [["0","No"],["1","Mod."],["2","Signif."]].map(function(o){
      return '<label data-v="'+o[0]+'"><input type="radio" name="c-'+c.k+'" id="c-'+c.k+'-'+o[0]+'" value="'+o[0]+'"'+(o[0]==="0"?" checked":"")+(c.auto?" disabled":"")+'>'+o[1]+'</label>';
    }).join("");
    return '<div class="row"><div class="ct"><b>'+c.t+'</b>'+(c.auto?'<span class="auto">automático</span>':'')+
      '<details class="pop"><summary aria-label="Umbrales de '+c.t+'">?</summary><div><b>Moderado:</b> '+c.m+'<br><b>Significativo:</b> '+c.s+(c.hint?'<br>'+c.hint:'')+'</div></details></div>'+
      '<div class="lvl3" role="radiogroup" aria-label="'+c.t+'">'+opts+'</div></div>';
  }).join("");

  function input(){
    return { sexo: document.querySelector('input[name="sexo"]:checked').value, edad: num("edad"), peso: num("peso"), talla: num("talla"),
      pesoHabitual: num("habitual") || undefined, situacion: $("situacion").value, renal: $("renal").value,
      ascitis: $("ascitis").checked, desnutrido: $("desnutrido").checked, tfgMenor30: $("tfg").checked, enfermedad: $("enfermedad").value };
  }
  function toggles(){
    var s = $("situacion").value;
    $("box-renal").hidden = s !== "renal"; $("box-cirrosis").hidden = s !== "cirrosis";
    $("box-tfg").hidden = s !== "polimorbido"; $("box-geria").hidden = s !== "geriatria";
  }
  function rangoTxt(o, unit){
    if (o.max == null) return "≥ " + nf(o.min) + "<small>" + unit + "</small>";
    if (o.min === o.max) return nf(o.min) + "<small>" + unit + "</small>";
    return nf(o.min) + "–" + nf(o.max) + "<small>" + unit + "</small>";
  }
  function porKgTxt(a){ return a[1] == null ? "≥" + nf(a[0], 1) : a[0] === a[1] ? nf(a[0], 1) : nf(a[0], 1) + "–" + nf(a[1], 1); }
  function pesoTxt(p){ return Array.isArray(p) ? nf(p[0], 1) + "–" + nf(p[1], 1) + " kg" : nf(p, 1) + " kg"; }

  function render(){
    toggles();
    var e = input(), r = C.requerimientos(e), out = $("results");
    if (!r.ok){ out.innerHTML = '<div class="alerts">' + r.errores.map(function(x){ return '<div class="alert err">' + x + '</div>'; }).join("") + '</div>'; $("kpis").innerHTML = ""; last = null; refeed(); return; }
    last = r;
    $("kpis").innerHTML = '<span class="kpi">IMC<b>' + nf(r.imc, 1) + '</b></span><span class="kpi">Ideal (IMC 25)<b>' + nf(r.peso.ideal25, 1) + ' kg</b></span>' +
      (r.peso.idealUCI ? '<span class="kpi">Ideal UCI<b>' + nf(r.peso.idealUCI, 1) + ' kg</b></span>' : '') +
      (r.perdida != null ? '<span class="kpi">Pérdida<b>' + nf(r.perdida, 1) + ' %</b></span>' : '');
    var E = r.energia, P = r.proteina;
    function card(k, o, unit, extra){
      var det = (o.nota ? '<p>' + o.nota + '</p>' : '') + '<p>Peso: ' + o.pesoTxt + '.</p>';
      return '<div class="res"><div class="rh"><span class="k">' + k + '</span><details class="pop"><summary aria-label="Notas de ' + k + '">?</summary><div>' + det + '</div></details></div>' +
        '<div class="v">' + rangoTxt(o, unit) + '</div><div class="f">' + porKgTxt(o.porKg) + (unit === "kcal/día" ? ' kcal/kg' : ' g/kg') + ' × ' + pesoTxt(o.pesoRef) + '</div>' + (extra || '') + '</div>';
    }
    out.innerHTML = card("Energía", E, "kcal/día", E.semana1 ? '<div class="w1">1ª semana: &lt;' + nf(E.semana1.max) + ' kcal/día</div>' : '') +
      card("Proteína", P, "g/día") +
      (r.avisos.length ? '<div class="alerts">' + r.avisos.map(function(x){ return '<div class="alert">' + x + '</div>'; }).join("") + '</div>' : '') +
      '<p class="src">' + r.fuentes.join("; ") + '</p>';
    if ($("ne-sync").checked && E.max) { $("ne-kcal").value = E.max; ne(); }
    if (!metaTocada) $("rf-meta").value = E.max || E.min;
    refeed();
  }

  function refeed(){
    var e = input(), I = (e.peso && e.talla) ? C.imc(e.peso, e.talla) : null;
    var lvlImc = I == null ? 0 : I < 16 ? 2 : I <= 18.5 ? 1 : 0;
    ["0","1","2"].forEach(function(v){ var x = $("c-imc-" + v); if (x) x.checked = (+v === lvlImc); });
    var c = { imc: I == null ? 0 : I };
    CRIT.forEach(function(k){ if (!k.auto) { var s = document.querySelector('input[name="c-' + k.k + '"]:checked'); c[k.k] = s ? +s.value : 0; } });
    var R = C.realimentacion(c, e.peso || 0);
    var col = R.riesgo === "significativo" ? "var(--stop)" : R.riesgo === "moderado" ? "var(--slow)" : "var(--leaf)";
    $("refeed-out").innerHTML = '<div class="verdict" style="--c:' + col + '"><b>Riesgo ' + R.riesgo + '</b><p>' +
      (R.enRiesgo ? 'Inicia con el plan del paso 2 y sigue el paso 3.' : 'Sin criterios suficientes según ASPEN. Igual revisa electrolitos al iniciar si hubo ayuno.') + '</p></div>';
    plan(R.enRiesgo);
  }

  function plan(enRiesgo){
    var w = num("peso"), meta = num("rf-meta"), ini = +$("rf-ini").value, cada = +$("rf-cada").value;
    if (!w || !meta) { $("plan").innerHTML = ""; return; }
    var p = C.planRealimentacion(meta, ini * w, cada);
    $("plan").innerHTML = (enRiesgo ? '' : '<p class="src">El paciente no cumple criterios de riesgo; el plan se muestra como referencia.</p>') +
      '<div class="ptable"><div class="pr ph"><span>Día</span><span>kcal/día</span><span>% de la meta</span></div>' +
      p.map(function(x){ return '<div class="pr"><span>' + x.dia + '</span><span>' + nf(x.kcal) + '</span><span><i style="width:' + x.pct + '%"></i>' + x.pct + ' %</span></div>'; }).join("") +
      '</div><p class="src">Alternativa: 100–150 g de dextrosa el día 1. Incluye la dextrosa de sueros y diluciones.</p>';
  }

  function ne(){
    var k = num("ne-kcal"), d = num("ne-dens"), h = num("ne-h"), p = num("ne-p");
    if (!k || !d || !h) { $("ne-out").innerHTML = ""; return; }
    var v = C.velocidadEnteral(k, d, h, p);
    $("ne-out").innerHTML = '<div class="out"><span class="k">Velocidad</span><span class="v">' + nf(v.mlh, 1) + '<small> mL/h</small></span></div>' +
      '<div class="out"><span class="k">Volumen</span><span class="v">' + nf(v.volumen) + '<small> mL/d</small></span></div>' +
      (v.proteina != null ? '<div class="out"><span class="k">Proteína</span><span class="v">' + nf(v.proteina) + '<small> g/d</small></span></div>' : '');
  }

  document.addEventListener("input", function(e){
    var t = e.target;
    if (t.form === $("f") || t.closest("#f")) { $("exnote").hidden = true; render(); }
  });
  document.addEventListener("change", function(e){ if (e.target.form === $("f") || e.target.closest("#f")) render(); });
  $("crit").addEventListener("change", refeed);
  $("rf-meta").addEventListener("input", function(){ metaTocada = true; refeed(); });
  ["rf-ini","rf-cada"].forEach(function(id){ $(id).addEventListener("change", refeed); });
  ["ne-dens","ne-h","ne-p"].forEach(function(id){ $(id).addEventListener("input", ne); });
  $("ne-kcal").addEventListener("input", function(){ $("ne-sync").checked = false; ne(); });
  $("ne-sync").addEventListener("change", render);
  /* cerrar otros "?" al abrir uno */
  document.addEventListener("toggle", function(e){
    if (e.target.classList && e.target.classList.contains("pop") && e.target.open)
      document.querySelectorAll("details.pop[open]").forEach(function(d){ if (d !== e.target) d.open = false; });
  }, true);
  render(); ne();

  /* ---------- Gasto energético basal ---------- */
  function geb(){
    var e = input(), out = $("geb-out"), get = $("get-out");
    if (!(e.peso && e.talla && e.edad)) { out.innerHTML = get.innerHTML = ""; return; }
    var m = C.gebMifflin(e.sexo, e.peso, e.talla, e.edad), h = C.gebHarrisBenedict(e.sexo, e.peso, e.talla, e.edad);
    var fa = num("f-act") || 1, fe = num("f-est") || 1;
    out.innerHTML = '<div class="out"><span class="k">GEB · Mifflin-St Jeor</span><span class="v">' + nf(m) + '<small> kcal</small></span></div>' +
      '<div class="out"><span class="k">GEB · Harris-Benedict</span><span class="v">' + nf(h) + '<small> kcal</small></span></div>';
    get.innerHTML = '<div class="out"><span class="k">GET · Mifflin</span><span class="v">' + nf(m * fa * fe) + '<small> kcal/d</small></span></div>' +
      '<div class="out"><span class="k">GET · Harris-Benedict</span><span class="v">' + nf(h * fa * fe) + '<small> kcal/d</small></span></div>';
  }
  ["f-act","f-est"].forEach(function(id){ $(id).addEventListener("input", geb); });
  document.addEventListener("input", function(e){ if (e.target.closest && e.target.closest("#f")) geb(); });
  document.addEventListener("change", function(e){ if (e.target.closest && e.target.closest("#f")) geb(); });
  geb();

  /* ---------- Insulina: basal, corrección, basal-bolo y corticoides ---------- */
  var MODOS = { basal: "Insulina basal + escala de corrección: esquema de elección en sala (consenso 2026).",
    corr: "Escala fija según sensibilidad: no depende del peso.",
    bb: "Basal-bolo: DM1, insulinopenia marcada o prednisona >20 mg/día (consenso 2026). DDT 50 % basal y 50 % bolos.",
    cort: "Método del consenso para hiperglicemia por corticoides." };
  var m0 = new URLSearchParams(location.search).get("modo");
  var st = { modo: MODOS[m0] ? m0 : "basal", origen: "peso", sens: "normal", hi: "0", tipo: "glargina", hipo: "0", prand: "analogo",
    esc: "normal", cins: "cristalina", cmom: "comidas", grupo: "2", cort: "prednisona", prandc: "analogo" };
  var $$ = function (s) { return document.querySelectorAll(s); };
  function tablaCorr(col, titulo, pie) {
    return '<div class="a-card" style="gap:0"><span class="a-lbl" style="color:var(--a-blue);margin-bottom:6px">' + titulo + '</span>' +
      C.CORRECCION.tramos.map(function (t, i) { return '<div class="a-kv"><span>' + t + ' mg/dL</span><b>' + C.CORRECCION[col][i] + ' UI</b></div>'; }).join("") +
      '<span class="a-foot" style="margin-top:8px">' + pie + '</span></div>';
  }
  var COL = { sensible: "sensible", normal: "normal", resistente: "resistente" }, NCOL = { sensible: "Sensible", normal: "Normal", resistente: "Resistente" };
  function pintarControles() {
    $$("[data-g]").forEach(function (b) { if (b.closest("#insulina")) b.setAttribute("aria-pressed", st[b.getAttribute("data-g")] === b.getAttribute("data-v")); });
    $$("[data-modo]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-modo") === st.modo); });
    $$("#insulina [data-ver]").forEach(function (x) { x.hidden = x.getAttribute("data-ver").split(" ").indexOf(st.modo) < 0; });
    $("modo-txt").textContent = MODOS[st.modo];
    $("i-prev-box").hidden = st.origen !== "previa"; $("i-ev-box").hidden = st.origen !== "ev";
    $("i-prev-lbl").textContent = st.modo === "bb" ? "Dosis diaria total previa (UI/día)" : "Dosis basal previa (UI/día)";
    $("hi-box").hidden = st.origen !== "peso" || (st.modo === "bb" && st.hipo === "1");
    $("grupo-txt").textContent = st.grupo === "1" ? "Sin diabetes previa; DM sin insulina con HbA1c <8,5 %; o ≥70 años, IMC <20 o VFG <30." : "DM <70 años con insulina previa, o sin insulina con HbA1c >8,5 %; con IMC >20 y VFG >30.";
  }
  var err = function (t) { return '<div class="a-card warn"><b>' + t + '</b></div>'; };
  function insulina() {
    pintarControles();
    var peso = num("i-peso"), out = $("i-out"), html = "";
    if (st.modo === "basal") {
      var r = C.insulinaBasal({ peso: peso, origen: st.origen, previa: num("i-prev") || 0, ev: num("i-ev") || 0, sens: st.sens, sobre200: st.hi === "1", tipo: st.tipo });
      if (!r.ok) { out.innerHTML = err(r.error); return; }
      var pos = r.posologia.nph ? "NPH: " + r.posologia.am + " UI en la mañana y " + r.posologia.pm + " UI a las 22 h" : "Glargina U100: " + r.dosis + " UI en monodosis nocturna";
      html = '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">Insulina basal</span><span class="a-big">' + r.dosis + ' <small>UI/día</small></span>' +
        '<b style="font-size:14px">' + pos + '</b><span class="a-foot" style="font-size:13px">' + r.como + ' · Consenso SOCHIDIAB 2026</span></div>' +
        (r.alerta ? '<div class="a-card warn"><b>⚠ ' + r.alerta + '</b></div>' : '') +
        (st.origen === "ev" ? '<div class="a-card note">Superponer la primera dosis SC con la infusión antes de suspenderla. El consenso sugiere contrastar con el cálculo por peso y, si difieren, promediar.</div>' : '') +
        '<div class="a-card note">Más la escala de corrección (modo Corrección), columna ' + NCOL[st.sens].toLowerCase() + '. Ajuste diario de la basal según el ayuno en el tema Diabetes.</div>';
    } else if (st.modo === "corr") {
      var cuando = st.cmom === "ayuno" ? (st.cins === "cristalina" ? "Cada 6 h" : "Cada 4 h") : (st.cins === "cristalina" ? "Antes de desayuno, almuerzo y cena (no en la once: se superpone con la cena)" : "Antes de desayuno, almuerzo, once y cena");
      html = tablaCorr(COL[st.esc], "Corrección · escala " + NCOL[st.esc].toLowerCase(), "<b>" + cuando + ".</b> Si no logra la meta: +2 UI por tramo. Bajo 70: protocolo de hipoglicemia. No corregir de noche sin ingesta. Consenso SOCHIDIAB 2026, cap. 3, tabla 4.");
    } else if (st.modo === "bb") {
      var b = C.insulinaBasalBolo({ peso: peso, origen: st.origen, previa: num("i-prev") || 0, ev: num("i-ev") || 0, riesgoHipo: st.hipo === "1", sobre200: st.hi === "1", prandial: st.prand });
      if (!b.ok) { out.innerHTML = err(b.error); return; }
      html = '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">Dosis diaria total (DDT)</span><span class="a-big">' + b.ddt + ' <small>UI/día</small></span>' +
        '<span class="a-foot" style="font-size:13px">' + b.como + (st.origen !== "peso" ? ' · ' + nf(b.porKg, 2) + ' UI/kg/día' : '') + ' · Consenso SOCHIDIAB 2026, tabla 6</span>' +
        '<div class="a-fgrid" style="margin-top:6px"><div style="background:var(--a-bg);border-radius:12px;padding:10px"><span class="a-lbl" style="font-size:11px">Basal 50 %</span><br><b style="font-size:20px">' + b.basal + ' UI</b><br><span class="a-foot">glargina o NPH (2/3 AM · 1/3 22 h)</span></div>' +
        '<div style="background:var(--a-bg);border-radius:12px;padding:10px"><span class="a-lbl" style="font-size:11px">Bolos 50 %</span><br><b style="font-size:20px">' + b.porComida + ' UI</b><br><span class="a-foot">× ' + b.comidas + ' comidas (' + b.bolos + ' UI)</span></div></div></div>' +
        (b.alerta ? '<div class="a-card warn"><b>⚠ ' + b.alerta + '</b></div>' : '') +
        (st.origen === "previa" ? '<div class="a-card note">Alta frecuencia de sobrebasalización ambulatoria: si la basal previa supera 0,5 UI/kg/día, recalcular por peso.</div>' : '') +
        (st.origen === "ev" ? '<div class="a-card note">La DDT desde la infusión puede diferir mucho de la teórica por peso: contrastar ambas y, si difieren, promediar. Superponer la SC antes de suspender la infusión.</div>' : '') +
        tablaCorr(b.escalaSugerida, "Corrección sugerida · escala " + NCOL[b.escalaSugerida].toLowerCase(), "Escala según la DDT (ADA 2026, sección 16): &lt;40 UI sensible, 40–80 normal, &gt;80 resistente. Se suma a cada bolo. Comida &lt;50 %: omitir o reducir el bolo.");
    } else {
      var c = C.insulinaCorticoides({ peso: peso, grupo: +st.grupo, corticoide: st.cort, dosisMg: num("i-cd"), prandial: st.prandc });
      if (!c.ok) { out.innerHTML = err(c.error); return; }
      var basalTxt = st.cort === "prednisona" || st.cort === "metilprednisolona" ? "NPH junto al corticoide" : st.cort === "hidrocortisona" ? "Según glicemias" : "Glargina";
      html = '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">Dosis diaria total final</span><span class="a-big">' + c.total + ' <small>UI/día</small></span>' +
        '<span class="a-foot" style="font-size:13px">(' + nf(c.base, 1) + ' + ' + nf(c.extra, 1) + ' por ' + st.cort + ') UI/kg × ' + nf(peso, 1) + ' kg</span>' +
        '<div class="a-fgrid" style="margin-top:6px"><div style="background:var(--a-bg);border-radius:12px;padding:10px"><span class="a-lbl" style="font-size:11px">Basal 40 %</span><br><b style="font-size:20px">' + c.basal + ' UI</b><br><span class="a-foot">' + basalTxt + '</span></div>' +
        '<div style="background:var(--a-bg);border-radius:12px;padding:10px"><span class="a-lbl" style="font-size:11px">Prandial 60 %</span><br><b style="font-size:20px">' + c.porComida + ' UI</b><br><span class="a-foot">fijas × ' + c.comidas + ' comidas</span></div></div></div>' +
        (c.aviso ? '<div class="a-card amber"><b>' + c.aviso + '</b></div>' : '') +
        '<div class="a-card" style="gap:0"><span class="a-lbl" style="color:var(--a-blue);margin-bottom:6px">Dosis por comida (fija ± corrección)</span>' +
        c.tabla.map(function (x) { return '<div class="a-kv"><span>' + x.tramo + ' mg/dL <span class="a-muted">' + (x.ajuste > 0 ? "+" + x.ajuste : x.ajuste < 0 ? "−" + (-x.ajuste) : "") + '</span></span><b>' + x.dosis + ' UI</b></div>'; }).join("") +
        '<span class="a-foot" style="margin-top:8px">Bajo 70: protocolo de hipoglicemia. Dosis entre tramos de la tabla: se usa el tramo inferior. Consenso SOCHIDIAB 2026, cap. 5, tablas 4–6.</span></div>';
    }
    out.innerHTML = html;
  }
  $("insulina").addEventListener("click", function (e) {
    var b = e.target.closest("[data-g],[data-modo]"); if (!b) return;
    if (b.hasAttribute("data-modo")) st.modo = b.getAttribute("data-modo"); else st[b.getAttribute("data-g")] = b.getAttribute("data-v");
    insulina();
  });
  ["i-peso", "i-prev", "i-ev", "i-cd"].forEach(function (id) { $(id).addEventListener("input", insulina); });
  insulina();

  /* ---------- Sodio corregido y osmolaridad ---------- */
  function osm(){
    var na = num("o-na"), g = num("o-gl");
    if (!na || !g) { $("o-out").innerHTML = ""; return; }
    var nc = C.sodioCorregido(na, g), os = C.osmolaridadEfectiva(na, g);
    var txt = os > 300 ? (g > 600 ? "Cumple glicemia y osmolaridad de estado hiperosmolar: confirmar con cetonas y pH." : "Osmolaridad efectiva >300 sin glicemia >600: buscar otra causa o crisis mixta.") : "";
    $("o-out").innerHTML = '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">Sodio corregido</span><span class="a-big">' + nf(nc, 1) + ' <small>mEq/L</small></span><span class="a-foot" style="font-size:13px">Na + 1,6 × (glicemia − 100) / 100</span></div>' +
      '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">Osmolaridad efectiva</span><span class="a-big">' + nf(os) + ' <small>mOsm/kg</small></span><span class="a-foot" style="font-size:13px">2 × Na medido + glicemia / 18 · criterio de estado hiperosmolar: &gt;300</span></div>' +
      (txt ? '<div class="a-card warn"><b>⚠ ' + txt + '</b></div>' : '');
  }
  ["o-na","o-gl"].forEach(function(id){ $(id).addEventListener("input", osm); });
  osm();

  /* El formulario del paciente solo aplica a las cuatro primeras calculadoras */
  var box = document.getElementById("calcs");
  function pac(id){ document.getElementById("pac-box").hidden = id === "insulina" || id === "osmolaridad"; }
  box.addEventListener("seccion", function(e){ pac(e.detail.id); });
  var vis = [].filter.call(box.children, function(s){ return s.hasAttribute("data-sec") && !s.hidden; })[0];
  if (vis) pac(vis.id);
})();
