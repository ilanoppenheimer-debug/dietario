/* Dietario · Evaluar un paciente. Elige la situación según el contexto marcado y muestra requerimientos y alertas.
   Cálculo transitorio en el navegador: no se guarda nada. */
(function () {
  "use strict";
  var C = window.NutriCalc, $ = function (id) { return document.getElementById(id); };
  var nf = function (x, d) { return x == null ? "" : x.toLocaleString("es-CL", { maximumFractionDigits: d == null ? 0 : d }); };
  var num = function (id) { var v = parseFloat(String($(id).value).replace(",", ".")); return isNaN(v) ? null : v; };
  var ctx = { riesgo: false, ayuno: false, uci: false, erc: false, cirr: false };

  // ejemplo inicial del mock: mujer 68 años, 160 cm, 41 kg, ingesta <50 %
  $("sexo-f").checked = true; $("edad").value = 68; $("talla").value = 160; $("peso").value = 41; ctx.ayuno = true;

  function situacion(e) {
    if (ctx.uci) return "uci";
    if (ctx.erc) return "renal";
    if (ctx.cirr) return "cirrosis";
    if (e.edad >= 65) return "polimorbido";
    return (ctx.riesgo || ctx.ayuno) ? "sala_riesgo" : "sala_sin_riesgo";
  }
  function rango(o, unit) {
    if (o.max == null) return "≥ " + nf(o.min) + " <small>" + unit + "</small>";
    if (o.min === o.max) return nf(o.min) + " <small>" + unit + "</small>";
    return nf(o.min) + "–" + nf(o.max) + " <small>" + unit + "</small>";
  }
  function porKg(a) { return a[1] == null ? "≥" + nf(a[0], 1) : a[0] === a[1] ? nf(a[0], 1) : nf(a[0], 1) + "–" + nf(a[1], 1); }
  function peso(p) { return Array.isArray(p) ? nf(p[0], 1) + "–" + nf(p[1], 1) + " kg" : nf(p, 1) + " kg"; }
  function alerta(t, d, c, href) {
    return '<a class="a-card" href="' + href + '" style="border:2px solid ' + c + ';gap:4px"><b style="color:' + c + '">' + t + '</b><span>' + d + "</span></a>";
  }

  function render() {
    document.querySelectorAll("[data-ctx]").forEach(function (b) { b.setAttribute("aria-pressed", ctx[b.getAttribute("data-ctx")]); });
    $("ev-renal-box").hidden = !ctx.erc; $("ev-ascitis-box").hidden = !ctx.cirr;
    var e = {
      sexo: document.querySelector('input[name="sexo"]:checked').value, edad: num("edad"), talla: num("talla"), peso: num("peso"),
      pesoHabitual: num("habitual") || undefined, renal: $("ev-renal").value, ascitis: $("ev-ascitis").checked, desnutrido: false,
      enfermedad: "aguda"
    };
    e.situacion = situacion(e);
    var r = C.requerimientos(e);
    if (!r.ok) {
      $("ev-res").innerHTML = ""; $("ev-src").textContent = "";
      $("ev-alertas").innerHTML = r.errores.map(function (x) { return '<div class="a-card warn"><b>' + x + "</b></div>"; }).join("");
      $("kpis").innerHTML = ""; return;
    }
    $("kpis").innerHTML = '<span class="kpi">IMC<b>' + nf(r.imc, 1) + '</b></span><span class="kpi">Situación<b style="font-family:inherit">' + C.SITUACIONES[e.situacion] + "</b></span>" +
      (r.perdida != null ? '<span class="kpi">Pérdida<b>' + nf(r.perdida, 1) + " %</b></span>" : "");

    /* alertas */
    var A = [], RF = C.realimentacion({ imc: r.imc, ingesta: ctx.ayuno ? 2 : 0 }, e.peso);
    if (RF.riesgo === "significativo") A.push(alerta("Riesgo significativo de realimentación",
      "IMC " + nf(r.imc, 1) + (ctx.ayuno ? " e ingesta &lt;50 % por &gt;5 días" : "") + ". Partir con " + nf(RF.inicio.kcalMin) + "–" + nf(RF.inicio.kcalMax) + " kcal y tiamina antes de alimentar.", "var(--a-red)", "realimentacion.html"));
    else if (RF.riesgo === "moderado" || RF.criterios.imc === 1) A.push(alerta("Revisar riesgo de realimentación", "Hay al menos un criterio moderado; completa los demás criterios en la calculadora.", "var(--a-amber)", "calculadoras.html#realimentacion"));
    if (ctx.erc) A.push(alerta("Enfermedad renal", "Proteína con peso habitual, no el real. No bajar la proteína para retrasar la diálisis.", "#3E78B8", "renal.html"));
    if (ctx.uci) A.push(alerta("Paciente crítico", "Primera semana &lt;70 % de la meta. Preferir calorimetría.", "var(--a-blue)", "uci.html"));
    if (ctx.cirr) A.push(alerta("Cirrosis", "No restringir proteína, tampoco con encefalopatía." + (e.ascitis ? " Con ascitis se calcula con peso ideal." : ""), "#A8721A", "requerimientos.html"));
    if (r.imc >= 30) A.push(alerta("Obesidad", "No indicar dieta hipocalórica; proteína con peso ajustado.", "#7C5BA8", "requerimientos.html"));
    if (e.edad >= 65 && !ctx.uci) A.push(alerta("Adulto mayor", "Proteína ≥1,0 g/kg; 1,2–1,5 si hay enfermedad (ESPEN geriatría 2019).", "var(--a-green)", "requerimientos.html"));
    r.avisos.forEach(function (x) { A.push('<div class="a-card note">' + x + "</div>"); });
    $("ev-alertas").innerHTML = A.join("") || '<div class="a-card dash">Sin alertas con los datos ingresados.</div>';

    var E = r.energia, P = r.proteina;
    var card = function (k, o, unit, u2, extra) {
      return '<div class="a-card"><span class="a-lbl" style="color:var(--a-blue)">' + k + '</span><span class="a-big" style="font-size:28px">' + rango(o, unit) + "</span>" + (extra || "") +
        '<span class="a-foot" style="font-size:13px">' + porKg(o.porKg) + " " + u2 + " × " + peso(o.pesoRef) + " (" + o.pesoTxt + ")</span>" + (o.nota ? '<span class="a-foot">' + o.nota + "</span>" : "") + "</div>";
    };
    $("ev-res").innerHTML = card("Energía", E, "kcal/día", "kcal/kg", E.semana1 ? '<b style="font-size:13.5px;color:var(--a-blue)">1ª semana: &lt;' + nf(E.semana1.max) + " kcal/día</b>" : "") + card("Proteína", P, "g/día", "g/kg");
    $("ev-src").textContent = "Fuente: " + r.fuentes.join("; ") + ". Ajusta la situación o los detalles en la calculadora completa.";
  }

  $("ctx").addEventListener("click", function (e) {
    var b = e.target.closest("[data-ctx]"); if (!b) return;
    var k = b.getAttribute("data-ctx"); ctx[k] = !ctx[k]; render();
  });
  document.addEventListener("input", function (e) { if (e.target.closest("#f")) { $("exnote").hidden = true; render(); } });
  document.addEventListener("change", function (e) { if (e.target.closest("#f") || e.target.id === "ev-renal" || e.target.id === "ev-ascitis") render(); });
  render();
})();
