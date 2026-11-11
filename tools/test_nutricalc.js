// Pruebas de site/assets/nutricalc.js. Uso: node tools/test_nutricalc.js
const C = require("../site/assets/nutricalc.js");
let fallas = 0, n = 0;
function eq(nombre, real, esperado, tol = 0.5) {
  n++;
  const ok = (real === null && esperado === null) || Math.abs(real - esperado) <= tol;
  if (!ok) { fallas++; console.log("✗", nombre, "→", real, "esperado", esperado); }
}
function igual(nombre, real, esperado) { n++; if (real !== esperado) { fallas++; console.log("✗", nombre, "→", real, "esperado", esperado); } }

// Pesos
eq("IMC 76 kg 175 cm", C.imc(76, 175), 24.82, 0.01);
eq("Ideal IMC25 175 cm", C.pesoIdealIMC25(175), 76.5625, 0.001);
eq("Ideal UCI hombre 175", C.pesoIdealUCI("M", 175), 67.5, 0.001);
eq("Ideal UCI mujer 160", C.pesoIdealUCI("F", 160), 48.6, 0.001);
eq("Ajustado hosp 120 kg 175 cm", C.pesoAjustadoHosp(120, 175), 76.5625 + 0.33 * 43.4375, 0.001);
eq("Ajustado hosp sin exceso = real", C.pesoAjustadoHosp(60, 175), 60, 0.001);
eq("Ajustado UCI mujer 120/160 al 25 %", C.pesoAjustadoUCI("F", 120, 160, 0.25), 48.6 + 0.25 * 71.4, 0.001);
eq("Pérdida 72→66,5", C.perdidaPeso(72, 66.5), 7.64, 0.01);

// Caso 1: politrauma UCI, hombre 76 kg 1,75 m (IMC 24,8 → peso real)
let r = C.requerimientos({ sexo: "M", edad: 25, peso: 76, talla: 175, situacion: "uci" });
eq("UCI caso1 kcal min", r.energia.min, 1520); eq("UCI caso1 kcal max", r.energia.max, 1900);
eq("UCI caso1 semana1 <70 %", r.energia.semana1.max, 1330); eq("UCI caso1 proteína", r.proteina.min, 99);
igual("UCI caso1 peso", r.energia.pesoTxt, "peso real");

// UCI obesa: mujer 120 kg 160 cm → ideal 48,6; ref 62,88–66,45
r = C.requerimientos({ sexo: "F", edad: 50, peso: 120, talla: 160, situacion: "uci" });
eq("UCI obesa kcal min", r.energia.min, Math.round(20 * 62.88)); eq("UCI obesa kcal max", r.energia.max, Math.round(25 * 66.45));
eq("UCI obesa prot min", r.proteina.min, Math.round(1.3 * 62.88)); eq("UCI obesa prot max", r.proteina.max, Math.round(1.3 * 66.45));

// Caso 2: pancreatitis UCI, 75 kg IMC 30,1 (talla ≈157,9) mujer → peso ajustado UCI
r = C.requerimientos({ sexo: "F", edad: 57, peso: 75, talla: 157.9, situacion: "uci" });
const id2 = 0.9 * (157.9 - 106);
eq("Caso2 prot min", r.proteina.min, Math.round(1.3 * (id2 + 0.2 * (75 - id2))));

// Caso 4: DM2 70 años ERC 4 sin diálisis, neumonía en sala (agudo sin TRR), 85 kg 168 cm, sin habitual → ideal IMC25 = 70,56
r = C.requerimientos({ sexo: "M", edad: 70, peso: 85, talla: 168, situacion: "renal", renal: "agudo_sin_trr" });
eq("Caso4 peso ref", r.proteina.pesoRef, 70.6, 0.05);
eq("Caso4 prot min (no 0,6)", r.proteina.min, 71); eq("Caso4 prot max", r.proteina.max, 92);
eq("Caso4 kcal", r.energia.min, 1411);
// mismo con peso habitual 88 kg
r = C.requerimientos({ sexo: "M", edad: 70, peso: 85, talla: 168, pesoHabitual: 88, situacion: "renal", renal: "erc_estable" });
eq("ERC estable prot min con habitual", r.proteina.min, Math.round(0.6 * 88));

// Caso 5: cirrosis con ascitis, 60 kg, talla 165 → peso ideal IMC 25 = 68,06 (no el real con ascitis)
r = C.requerimientos({ sexo: "M", edad: 55, peso: 60, talla: 165, situacion: "cirrosis", ascitis: true });
eq("Cirrosis ascitis peso", r.energia.pesoRef, 68.1, 0.05);
eq("Cirrosis kcal min", r.energia.min, Math.round(30 * 68.0625)); eq("Cirrosis prot max", r.proteina.max, Math.round(1.5 * 68.0625));
r = C.requerimientos({ sexo: "M", edad: 55, peso: 60, talla: 165, situacion: "cirrosis", desnutrido: true });
eq("Cirrosis desnutrido prot", r.proteina.min, 90);

// Sala con riesgo, obeso 120 kg 175 cm → ajustado hosp
r = C.requerimientos({ sexo: "M", edad: 45, peso: 120, talla: 175, situacion: "sala_riesgo" });
eq("Sala obeso prot", r.proteina.min, Math.round(1.2 * C.pesoAjustadoHosp(120, 175)));
igual("Sala con riesgo prot max abierto", r.proteina.max, null);
// Polimórbido ≥65, 70 kg normal; y con TFG <30
r = C.requerimientos({ sexo: "F", edad: 80, peso: 70, talla: 165, situacion: "polimorbido" });
eq("Polimórbido kcal", r.energia.min, 1890); eq("Polimórbido prot", r.proteina.max, 105);
r = C.requerimientos({ sexo: "F", edad: 80, peso: 70, talla: 165, situacion: "polimorbido", tfgMenor30: true });
eq("Polimórbido TFG<30", r.proteina.min, 56);
r = C.requerimientos({ sexo: "F", edad: 80, peso: 45, talla: 165, situacion: "polimorbido" });
eq("Polimórbido muy bajo peso 30 kcal/kg", r.energia.min, 1350);
// Geriatría severa
r = C.requerimientos({ sexo: "M", edad: 82, peso: 60, talla: 170, situacion: "geriatria", enfermedad: "severa" });
eq("Geriatría kcal", r.energia.min, 1800); eq("Geriatría prot max", r.proteina.max, 120);

// Validaciones
igual("Rechaza menor de edad", C.requerimientos({ sexo: "M", edad: 15, peso: 60, talla: 170, situacion: "uci" }).ok, false);
igual("Rechaza renal sin escenario", C.requerimientos({ sexo: "M", edad: 50, peso: 60, talla: 170, situacion: "renal" }).ok, false);

// Realimentación ASPEN 2020
let f = C.realimentacion({ imc: 15.5 }, 45);
igual("IMC <16 → significativo", f.riesgo, "significativo"); eq("Inicio 10 kcal/kg", f.inicio.kcalMin, 450); eq("Inicio 20 kcal/kg", f.inicio.kcalMax, 900);
f = C.realimentacion({ imc: 17.5, ingesta: 1 }, 50); igual("2 moderados → moderado", f.riesgo, "moderado");
f = C.realimentacion({ imc: 17.5 }, 50); igual("1 moderado → no en riesgo", f.enRiesgo, false);
f = C.realimentacion({ imc: 16 }, 50); igual("IMC 16 exacto → moderado (16–18,5)", f.criterios.imc, 1);
f = C.realimentacion({ imc: 22, electrolitos: 2 }, 70); igual("Electrolitos muy bajos → significativo", f.riesgo, "significativo");

// Plan de realimentación: meta 1800, inicio 600 (60 kg × 10), cada 1 día
let pl = C.planRealimentacion(1800, 600, 1);
igual("Plan días", pl.map(x=>x.dia).join(","), "1,2,3"); igual("Plan kcal", pl.map(x=>x.kcal).join(","), "600,1194,1800");
pl = C.planRealimentacion(2000, 1000, 2); igual("Plan cada 2 días", pl.map(x=>x.dia+":"+x.kcal).join(","), "1:1000,3:1660,5:2000");

let v = C.velocidadEnteral(1800, 1.2, 24, 56);
eq("NE volumen", v.volumen, 1500); eq("NE mL/h", v.mlh, 62.5, 0.05); eq("NE proteína", v.proteina, 84);


// Gasto energético basal: H 25 años 175 cm 76 kg
eq("Mifflin H", C.gebMifflin("M", 76, 175, 25), 1733.75, 0.01);
eq("Harris-Benedict revisada H", C.gebHarrisBenedict("M", 76, 175, 25), 1804.4, 0.1);
eq("Mifflin M", C.gebMifflin("F", 60, 160, 40), 1239, 0.01);

// Insulina basal (consenso SOCHIDIAB 2026, cap. 3)
let ib = C.insulinaBasal({ peso: 80, previa: 0, sens: "normal", sobre200: false, tipo: "glargina" });
eq("Basal 0,2 UI/kg", ib.dosis, 16);
ib = C.insulinaBasal({ peso: 80, previa: 0, sens: "normal", sobre200: true, tipo: "nph" });
eq("Basal 0,3 UI/kg con >200", ib.dosis, 24); eq("NPH 2/3 AM", ib.posologia.am, 16); eq("NPH 1/3 PM", ib.posologia.pm, 8);
ib = C.insulinaBasal({ peso: 70, previa: 0, sens: "sensible", tipo: "glargina" }); eq("Insulinosensible 0,1", ib.dosis, 7);
ib = C.insulinaBasal({ peso: 90, previa: 30, sens: "normal", tipo: "glargina" }); eq("70 % de la previa", ib.dosis, 21);
ib = C.insulinaBasal({ peso: 90, previa: 30, sens: "sensible", tipo: "glargina" }); eq("50 % de la previa", ib.dosis, 15);
ib = C.insulinaBasal({ peso: 60, previa: 40, sens: "normal", tipo: "glargina" }); eq("Sobrebasalizado → por peso", ib.dosis, 12); igual("Alerta sobrebasalización", !!ib.alerta, true);
igual("Columna resistente", C.insulinaBasal({ peso: 70, sens: "resistente" }).correccion.join(","), "0,4,6,8,10,12,14,16");

// Basal por infusión EV y basal-bolo (consenso 2026, tabla 6)
ib = C.insulinaBasal({ peso: 80, origen: "ev", ev: 2, sens: "normal", tipo: "glargina" }); eq("Basal desde EV: 50 % de 48", ib.dosis, 24);
igual("Basal EV sin dato", C.insulinaBasal({ peso: 80, origen: "ev", sens: "normal" }).ok, false);
let bb = C.insulinaBasalBolo({ peso: 80, origen: "peso", prandial: "analogo" });
eq("BB por peso 0,5", bb.ddt, 40); eq("BB basal 50 %", bb.basal, 20); eq("BB por comida (4)", bb.porComida, 5);
eq("BB riesgo hipo 0,3", C.insulinaBasalBolo({ peso: 80, origen: "peso", riesgoHipo: true }).ddt, 24);
eq("BB >200: 0,6", C.insulinaBasalBolo({ peso: 80, origen: "peso", sobre200: true }).ddt, 48);
bb = C.insulinaBasalBolo({ peso: 70, origen: "previa", previa: 60, prandial: "cristalina" });
eq("BB 70 % DDT previa", bb.ddt, 42); eq("BB basal", bb.basal, 21); eq("BB por comida (3)", bb.porComida, 7);
eq("BB desde EV", C.insulinaBasalBolo({ peso: 80, origen: "ev", ev: 2 }).ddt, 48);
igual("Escala ADA por DDT", [C.escalaPorDDT(30), C.escalaPorDDT(60), C.escalaPorDDT(90)].join(","), "sensible,normal,resistente");

// Corticoides: los 3 casos clínicos del consenso (cap. 5)
let ic = C.insulinaCorticoides({ peso: 80, grupo: 2, corticoide: "prednisona", dosisMg: 60, prandial: "analogo" });
eq("Caso 1 total", ic.total, 72); eq("Caso 1 basal", ic.basal, 28); eq("Caso 1 por comida (4)", ic.porComida, 10);
ic = C.insulinaCorticoides({ peso: 61, grupo: 1, corticoide: "dexametasona", dosisMg: 16, prandial: "cristalina" });
eq("Caso 2 total", ic.total, 42); eq("Caso 2 basal", ic.basal, 16); eq("Caso 2 por comida (3)", ic.porComida, 8);
ic = C.insulinaCorticoides({ peso: 54, grupo: 1, corticoide: "hidrocortisona", dosisMg: 150, prandial: "cristalina" });
eq("Caso 3 total", ic.total, 32); eq("Caso 3 basal", ic.basal, 12); eq("Caso 3 por comida", ic.porComida, 6);
ic = C.insulinaCorticoides({ peso: 70, grupo: 1, corticoide: "prednisona", dosisMg: 35, prandial: "analogo" });
eq("Dosis entre tramos → tramo inferior", ic.extra, 0.3);
igual("Prednisona ≤10 avisa", !!C.insulinaCorticoides({ peso: 70, grupo: 1, corticoide: "prednisona", dosisMg: 10 }).aviso, true);
igual("Tabla grupo 2 >300", C.insulinaCorticoides({ peso: 80, grupo: 2, corticoide: "prednisona", dosisMg: 60, prandial: "analogo" }).tabla[6].dosis, 20);

// Crisis hiperglicémicas
eq("Na corregido", C.sodioCorregido(138, 720), 147.92, 0.01); eq("Osm efectiva", C.osmolaridadEfectiva(138, 720), 316, 0.01);

console.log(fallas ? `\n${fallas} de ${n} pruebas fallaron` : `✓ ${n} pruebas OK`);
process.exit(fallas ? 1 : 0);
