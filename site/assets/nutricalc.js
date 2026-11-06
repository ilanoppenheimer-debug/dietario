/* Dietario · Cálculos de nutrición hospitalaria (adultos).
   Funciones puras, sin interfaz. Probadas en tools/test_nutricalc.js.
   Cada resultado incluye la fórmula aplicada y su fuente.

   Fuentes (versión vigente en noviembre 2026):
   - ESPEN hospitalaria 2021 (Thibault): R15 dieta estándar 25 kcal/kg y 0,8–1,0 g/kg; dieta hospitalaria 30 kcal/kg y ≥1,2 g/kg
     (peso real); 3.12: en obesidad, peso ajustado = ideal + 0,33 × (real − ideal), ideal = peso con IMC 25.
   - ESPEN paciente médico polimórbido 2024 (Wunderle): ≥65 años 27 kcal/kg peso real; muy bajo peso 30 kcal/kg, lento;
     proteína 1,2–1,5 g/kg; TFGe <30 sin terapia de reemplazo 0,8 g/kg.
   - ESPEN UCI 2023 (Singer): sin calorimetría 20–25 kcal/kg; primera semana <70 % de lo estimado; proteína 1,3 g/kg
     progresiva; con IMC >25, peso de referencia = ideal [0,9 × (talla − 100) hombre, (talla − 106) mujer] + 20–25 % del exceso.
   - ESPEN renal 2024 (Sabatino): energía 20–30 kcal/kg como punto de partida; proteína según escenario; usar peso habitual
     o previo al ingreso antes que el ideal; no usar el peso real.
   - ESPEN hígado 2020 (Bischoff): 30–35 kcal/kg y 1,2–1,5 g/kg (1,5 si desnutrido); con ascitis, peso ideal según talla.
   - ESPEN geriatría 2019 (Volkert): 30 kcal/kg; proteína ≥1,0 g/kg, 1,2–1,5 con enfermedad, hasta 2,0 si es severa.
   - ASPEN realimentación 2020 (da Silva): criterios de riesgo (tabla 3); inicio 10–20 kcal/kg o 100–150 g de dextrosa
     las primeras 24 h, subir 33 % de la meta cada 1–2 días; tiamina 100 mg antes de alimentar.
*/
(function (root) {
  "use strict";

  var r1 = function (x) { return Math.round(x * 10) / 10; };
  var r0 = function (x) { return Math.round(x); };

  function imc(pesoKg, tallaCm) { var t = tallaCm / 100; return pesoKg / (t * t); }
  function pesoIdealIMC25(tallaCm) { var t = tallaCm / 100; return 25 * t * t; }
  function pesoIdealUCI(sexo, tallaCm) { return 0.9 * (tallaCm - (sexo === "F" ? 106 : 100)); }
  function pesoAjustadoHosp(pesoKg, tallaCm) {
    var ideal = pesoIdealIMC25(tallaCm);
    return pesoKg > ideal ? ideal + 0.33 * (pesoKg - ideal) : pesoKg;
  }
  function pesoAjustadoUCI(sexo, pesoKg, tallaCm, fraccion) {
    var ideal = pesoIdealUCI(sexo, tallaCm);
    return pesoKg > ideal ? ideal + fraccion * (pesoKg - ideal) : pesoKg;
  }
  function perdidaPeso(habitual, actual) { return habitual > 0 ? (habitual - actual) * 100 / habitual : null; }

  var SITUACIONES = {
    sala_riesgo: "Sala, con riesgo nutricional",
    sala_sin_riesgo: "Sala, sin riesgo nutricional",
    polimorbido: "Paciente médico polimórbido ≥65 años",
    geriatria: "Adulto mayor (guía geriátrica)",
    uci: "UCI / paciente crítico",
    renal: "Enfermedad renal (ERC o IRA)",
    cirrosis: "Cirrosis"
  };

  var RENAL = {
    erc_estable:   { t: "ERC sin enfermedad aguda", p: [0.6, 0.8] },
    erc_hd:        { t: "ERC en hemodiálisis crónica, sin enfermedad aguda", p: [1.2, null] },
    ira_no_critico:{ t: "IRA o IRA sobre ERC, sin enfermedad crítica", p: [0.8, 1.0] },
    agudo_sin_trr: { t: "Enfermedad aguda o crítica, sin terapia de reemplazo", p: [1.0, 1.3] },
    critico_hdi:   { t: "Crítico con diálisis intermitente", p: [1.3, 1.5] },
    critico_trrc:  { t: "Crítico con terapia continua o prolongada", p: [1.5, 1.7] }
  };

  /* Entrada: {sexo:"M"|"F", edad, peso, talla, pesoHabitual?, situacion, renal?, ascitis?, desnutrido?,
               tfgMenor30?, enfermedad? ("ninguna"|"aguda"|"severa")}
     Salida: {ok, errores[], imc, peso:{...}, energia:{min,max,porKg:[a,b],pesoRef,nota}, proteina:{...}, avisos[], fuentes[]} */
  function requerimientos(e) {
    var err = [];
    if (!(e.peso >= 25 && e.peso <= 350)) err.push("Peso fuera de rango (25–350 kg).");
    if (!(e.talla >= 120 && e.talla <= 230)) err.push("Talla fuera de rango (120–230 cm).");
    if (!(e.edad >= 18 && e.edad <= 110)) err.push("La calculadora es para adultos de 18 a 110 años.");
    if (!SITUACIONES[e.situacion]) err.push("Elige una situación clínica.");
    if (e.situacion === "renal" && !RENAL[e.renal]) err.push("Elige el escenario renal.");
    if (err.length) return { ok: false, errores: err };

    var I = imc(e.peso, e.talla), out = { ok: true, errores: [], imc: r1(I), avisos: [], fuentes: [] };
    var ideal25 = pesoIdealIMC25(e.talla);
    out.peso = { real: e.peso, ideal25: r1(ideal25) };
    if (e.pesoHabitual) out.perdida = r1(perdidaPeso(e.pesoHabitual, e.peso));

    var kcal, prot, wE, wP, wEtxt, wPtxt, nE = "", nP = "", fuente;

    switch (e.situacion) {
      case "sala_riesgo":
      case "sala_sin_riesgo":
        var conRiesgo = e.situacion === "sala_riesgo";
        kcal = conRiesgo ? [30, 30] : [25, 25];
        prot = conRiesgo ? [1.2, null] : [0.8, 1.0];
        fuente = "ESPEN hospitalaria 2021, R15 y 3.12";
        if (I >= 30) {
          var adj = pesoAjustadoHosp(e.peso, e.talla);
          wP = adj; wPtxt = "peso ajustado = ideal (IMC 25) + 0,33 × exceso";
          wE = adj; wEtxt = wPtxt;
          nE = "ESPEN 2021 define el peso ajustado para la proteína; usarlo para la energía es una extrapolación: validar o usar calorimetría.";
          out.avisos.push("Obesidad: no indicar dieta hipocalórica en el hospitalizado (ESPEN 2021, R31).");
        } else { wE = wP = e.peso; wEtxt = wPtxt = "peso real"; }
        break;

      case "polimorbido":
        fuente = "ESPEN polimórbido 2024, R6–R10";
        wE = wP = e.peso; wEtxt = wPtxt = "peso real";
        if (I < 18.5) {
          kcal = [30, 30];
          nE = "Muy bajo peso: llegar a la meta en forma lenta y cautelosa (alto riesgo de realimentación).";
        } else kcal = [27, 27];
        prot = e.tfgMenor30 ? [0.8, 0.8] : [1.2, 1.5];
        if (e.tfgMenor30) nP = "TFGe <30 sin terapia de reemplazo: 0,8 g/kg.";
        if (e.edad < 65) out.avisos.push("La cifra de 27 kcal/kg está definida para ≥65 años; en menores, usar 'Sala'.");
        if (I >= 30) out.avisos.push("Obesidad: la guía usa peso real; considera el peso ajustado o calorimetría.");
        break;

      case "geriatria":
        fuente = "ESPEN geriatría 2019";
        wE = wP = e.peso; wEtxt = wPtxt = "peso real";
        kcal = [30, 30];
        prot = e.enfermedad === "severa" ? [1.5, 2.0] : e.enfermedad === "aguda" ? [1.2, 1.5] : [1.0, null];
        nE = "Valor orientador: ajustar según estado nutricional, actividad, enfermedad y tolerancia.";
        if (e.edad < 65) out.avisos.push("Guía geriátrica: pensada para ≥65 años.");
        break;

      case "uci":
        fuente = "ESPEN UCI 2023, R21–R25 y R5.2";
        kcal = [20, 25]; prot = [1.3, 1.3];
        if (I > 25) {
          var lo = pesoAjustadoUCI(e.sexo, e.peso, e.talla, 0.20), hi = pesoAjustadoUCI(e.sexo, e.peso, e.talla, 0.25);
          out.peso.idealUCI = r1(pesoIdealUCI(e.sexo, e.talla));
          wE = [lo, hi]; wP = [lo, hi];
          wEtxt = wPtxt = "peso ideal [0,9 × (talla − " + (e.sexo === "F" ? "106" : "100") + ")] + 20–25 % del exceso";
        } else { wE = wP = e.peso; wEtxt = wPtxt = "peso real"; }
        nE = "Preferir calorimetría indirecta. Si se usa esta estimación, la primera semana aportar menos del 70 %.";
        nP = "Aportar en forma progresiva. Si hay nitrógeno urinario o medición de masa magra, guiarse por ellos.";
        out.avisos.push("Glucosa ≤5 mg/kg/min; lípidos EV hasta 1 g/kg/d, tolerancia hasta 1,5 (ESPEN UCI 2023).");
        break;

      case "renal":
        fuente = "ESPEN renal 2024, R18 y comentario de energía";
        kcal = [20, 30]; prot = RENAL[e.renal].p;
        if (e.pesoHabitual) { wE = wP = e.pesoHabitual; wEtxt = wPtxt = "peso habitual o previo al ingreso"; }
        else { wE = wP = ideal25; wEtxt = wPtxt = "peso ideal (IMC 25), porque no se ingresó el habitual"; }
        nE = "Punto de partida sin calorimetría. Sumar las kcal de citrato, lactato y glucosa de la diálisis.";
        nP = RENAL[e.renal].t + ". No usar el peso real (sobrecarga de volumen).";
        break;

      case "cirrosis":
        fuente = "ESPEN hígado 2020, R57–R58";
        kcal = [30, 35]; prot = e.desnutrido ? [1.5, 1.5] : [1.2, 1.5];
        if (e.ascitis) { wE = wP = ideal25; wEtxt = wPtxt = "peso ideal según talla (IMC 25), por ascitis"; }
        else { wE = wP = e.peso; wEtxt = wPtxt = "peso real"; }
        nP = "No restringir proteína, tampoco con encefalopatía. Colación nocturna.";
        break;
    }

    function rango(porKg, w) {
      var wl = Array.isArray(w) ? w[0] : w, wh = Array.isArray(w) ? w[1] : w;
      return { min: r0(porKg[0] * wl), max: porKg[1] == null ? null : r0(porKg[1] * wh) };
    }
    var E = rango(kcal, wE), P = rango(prot, wP);
    out.energia = { min: E.min, max: E.max, porKg: kcal, pesoRef: Array.isArray(wE) ? wE.map(r1) : r1(wE), pesoTxt: wEtxt, nota: nE };
    out.proteina = { min: P.min, max: P.max, porKg: prot, pesoRef: Array.isArray(wP) ? wP.map(r1) : r1(wP), pesoTxt: wPtxt, nota: nP };
    if (e.situacion === "uci") out.energia.semana1 = { max: r0(0.7 * E.max) };
    out.fuentes.push(fuente);
    if (out.perdida != null && out.perdida >= 5) out.avisos.push("Pérdida de peso de " + out.perdida.toLocaleString("es-CL") + " %: revisar riesgo de realimentación.");
    return out;
  }

  /* Realimentación ASPEN 2020. criterios: {imc, perdida, ingesta, electrolitos, grasa, musculo, comorbilidad}
     cada uno: 0 = no, 1 = moderado, 2 = significativo. El IMC puede venir como número. */
  function realimentacion(c, pesoKg) {
    var niv = {};
    ["perdida", "ingesta", "electrolitos", "grasa", "musculo", "comorbilidad"].forEach(function (k) { niv[k] = +c[k] || 0; });
    if (typeof c.imc === "number") niv.imc = c.imc < 16 ? 2 : c.imc <= 18.5 ? 1 : 0; else niv.imc = +c.imc || 0;
    var sig = 0, mod = 0;
    Object.keys(niv).forEach(function (k) { if (niv[k] === 2) sig++; else if (niv[k] === 1) mod++; });
    var riesgo = sig >= 1 ? "significativo" : mod >= 2 ? "moderado" : mod === 1 ? "bajo (1 criterio moderado)" : "sin criterios";
    var out = { riesgo: riesgo, criterios: niv, enRiesgo: sig >= 1 || mod >= 2 };
    if (out.enRiesgo && pesoKg) {
      out.inicio = { kcalMin: r0(10 * pesoKg), kcalMax: r0(20 * pesoKg), dextrosa: [100, 150] };
    }
    return out;
  }

  /* Plan de progresión en realimentación (ASPEN 2020): parte en inicioKcal y sube 33 % de la meta
     cada "cada" días (1 o 2) hasta llegar a la meta. Devuelve [{dia, kcal, pct}]. */
  function planRealimentacion(metaKcal, inicioKcal, cada) {
    var plan = [], k = Math.min(inicioKcal, metaKcal), dia = 1, paso = metaKcal * 0.33;
    plan.push({ dia: 1, kcal: r0(k), pct: r0(100 * k / metaKcal) });
    while (k < metaKcal && plan.length < 30) {
      dia += cada; k = Math.min(metaKcal, k + paso); if (metaKcal - k < 0.05 * metaKcal) k = metaKcal;
      plan.push({ dia: dia, kcal: r0(k), pct: r0(100 * k / metaKcal) });
    }
    return plan;
  }

  function balanceNitrogenado(proteinaG, nuuG) {
    return { balance: r1(proteinaG / 6.25 - (nuuG + 4)), proteinaNeutra: r0((nuuG + 4) * 6.25) };
  }

  function velocidadEnteral(metaKcal, kcalPorMl, horas, protPorL) {
    var vol = metaKcal / kcalPorMl;
    var o = { volumen: r0(vol), mlh: r1(vol / horas) };
    if (protPorL) o.proteina = r0(vol / 1000 * protPorL);
    return o;
  }

  var api = { imc: imc, pesoIdealIMC25: pesoIdealIMC25, pesoIdealUCI: pesoIdealUCI, pesoAjustadoHosp: pesoAjustadoHosp,
              pesoAjustadoUCI: pesoAjustadoUCI, perdidaPeso: perdidaPeso, requerimientos: requerimientos,
              realimentacion: realimentacion, planRealimentacion: planRealimentacion, balanceNitrogenado: balanceNitrogenado, velocidadEnteral: velocidadEnteral,
              SITUACIONES: SITUACIONES, RENAL: RENAL };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.NutriCalc = api;
})(this);
