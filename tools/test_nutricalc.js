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

// Caso 1 manual: politrauma UCI, hombre 76 kg 1,75 m (IMC 24,8 → peso real)
let r = C.requerimientos({ sexo: "M", edad: 25, peso: 76, talla: 175, situacion: "uci" });
eq("UCI caso1 kcal min", r.energia.min, 1520); eq("UCI caso1 kcal max", r.energia.max, 1900);
eq("UCI caso1 semana1 <70 %", r.energia.semana1.max, 1330); eq("UCI caso1 proteína", r.proteina.min, 99);
igual("UCI caso1 peso", r.energia.pesoTxt, "peso real");

// UCI obesa: mujer 120 kg 160 cm → ideal 48,6; ref 62,88–66,45
r = C.requerimientos({ sexo: "F", edad: 50, peso: 120, talla: 160, situacion: "uci" });
eq("UCI obesa kcal min", r.energia.min, Math.round(20 * 62.88)); eq("UCI obesa kcal max", r.energia.max, Math.round(25 * 66.45));
eq("UCI obesa prot min", r.proteina.min, Math.round(1.3 * 62.88)); eq("UCI obesa prot max", r.proteina.max, Math.round(1.3 * 66.45));

// Caso 2 manual: pancreatitis UCI, 75 kg IMC 30,1 (talla ≈157,9) mujer → peso ajustado UCI
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

// Balance nitrogenado y enteral
let b = C.balanceNitrogenado(100, 12);
eq("BN 100 g prot, NUU 12", b.balance, -0.0, 0.05); eq("Proteína neutra NUU 16", C.balanceNitrogenado(0, 16).proteinaNeutra, 125);
let v = C.velocidadEnteral(1800, 1.2, 24, 56);
eq("NE volumen", v.volumen, 1500); eq("NE mL/h", v.mlh, 62.5, 0.05); eq("NE proteína", v.proteina, 84);

console.log(fallas ? `\n${fallas} de ${n} pruebas fallaron` : `✓ ${n} pruebas OK`);
process.exit(fallas ? 1 : 0);
