/* Dietario · pantalla de inicio: elegir perfil → introducción (solo la primera vez) → inicio. */
(function () {
  "use strict";
  var D = window.Dietario, q = new URLSearchParams(location.search), body = document.body;
  var $ = function (s) { return document.querySelector(s); };
  var estados = { perfil: $('[data-estado="perfil"]'), intro: $('[data-estado="intro"]'), inicio: $('[data-estado="inicio"]') };

  /* Vuelta desde /api/acceso con el código correcto */
  if (q.get("acceso") === "ok") {
    D.setPerfil("pro");
    var sig = q.get("next") || "";
    if (D.get("intro.pro", false) && /^\/clinica\//.test(sig) && sig.indexOf("//") < 0) { location.replace(sig); return; }
    history.replaceState(null, "", "index.html" + (D.get("intro.pro", false) ? "" : "?intro")); q = new URLSearchParams(location.search);
  }

  var SLIDES = {
    pac: [
      ["Tu dieta, explicada en simple", "Qué comer, cuánto y por qué, con alimentos y medidas de uso habitual en Chile.", '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h9"/><path d="M12 12l6.4 6.4"/>'],
      ["Guarda tus dietas y lleva tu registro", "Ten a mano las dietas que te indicaron y anota tu presión o glicemia para mostrarlas en tu control.", '<path d="M3 12h4l3-8 4 16 3-8h4"/>'],
      ["Un apoyo, no un reemplazo", "Basado en guías clínicas y revisado por profesionales. Complementa lo que te indicaron tu médico y tu nutricionista.", '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>']
    ],
    pro: [
      ["Pautas con evidencia", "Cada dieta trae su versión profesional: indicación, magnitud del efecto, evidencia y cómo prescribirla.", '<path d="M6 3h9l4 4v14H6zM9 12h7M9 16h7"/>'],
      ["Explica en la consulta", "Muestra la versión del paciente desde la misma ficha y entrégale el tríptico impreso, a color o en blanco y negro.", '<rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="10" y="4" width="7" height="16" rx="1.5"/><path d="M17 4h4v16h-4"/>'],
      ["Herramientas clínicas", "Evaluar un paciente, calculadoras y temas de nutrición y metabolismo, siempre con la guía de origen al lado.", '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>']
    ]
  };

  function mostrar(cual) {
    Object.keys(estados).forEach(function (k) { estados[k].hidden = k !== cual; });
    var bare = cual !== "inicio";
    body.classList.toggle("a-bare", bare);
    document.querySelector(".a-top").hidden = bare;
    document.querySelector(".a-nav").hidden = bare;
    window.scrollTo(0, 0);
  }

  var n = 0;
  function pintarIntro() {
    var p = D.perfil() === "pro" ? "pro" : "pac", s = SLIDES[p][n], color = p === "pro" ? "#2F5D8A" : "#2A7A4B";
    $("#intro-t").textContent = s[0]; $("#intro-d").textContent = s[1];
    $("#intro-ico").innerHTML = '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="' + color + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + s[2] + "</svg>";
    $("#intro-ico").style.background = p === "pro" ? "var(--a-blue-soft)" : "var(--a-green-soft)";
    var para = $("#intro-para"); para.textContent = p === "pro" ? "Para profesionales de salud" : "Para pacientes"; para.classList.toggle("pro", p === "pro");
    [].forEach.call($("#intro-dots").children, function (d, i) { d.classList.toggle("on", i === n); });
    var b = $("#intro-btn"); b.textContent = n === 2 ? "Empezar" : "Siguiente"; b.classList.toggle("blue", p === "pro");
    document.body.classList.toggle("a-pro", p === "pro");
  }
  function terminarIntro() {
    D.set("intro." + (D.perfil() === "pro" ? "pro" : "pac"), true);
    location.replace("index.html");
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-elegir],[data-intro]"); if (!el) return;
    if (el.hasAttribute("data-elegir")) {
      D.setPerfil("pac");
      if (D.get("intro.pac", false)) location.replace("index.html"); else { n = 0; pintarIntro(); mostrar("intro"); history.replaceState(null, "", "index.html?intro"); }
    } else if (el.getAttribute("data-intro") === "saltar") terminarIntro();
    else if (n < 2) { n++; pintarIntro(); } else terminarIntro();
  });

  /* ---------- inicio ---------- */
  function pintarInicio() {
    var pro = D.isPro();
    $("#hola").textContent = pro ? "Hola, colega" : "Hola";
    $("#hola-sub").textContent = pro ? "Pautas para indicar y material para entregar." : "Tu alimentación, explicada en simple.";
    var mis = D.mis();
    document.querySelectorAll("[data-misitem]").forEach(function (a) { a.hidden = mis.indexOf(a.getAttribute("data-misitem")) < 0; });
    $("#sin-mis").hidden = mis.length > 0;
    $("#combinar").hidden = mis.length < 2;
    var b = $("[data-qrnuevo]");
    if (b && D.get("qrNuevo", false) && !D.get("intro.pac", false)) {
      b.hidden = false;
      b.insertAdjacentHTML("beforeend", '<a class="a-chip" href="index.html?intro" style="background:var(--a-green);color:#fff">Conocer</a><button class="a-x" type="button" aria-label="Cerrar aviso">✕</button>');
      b.querySelector(".a-x").addEventListener("click", function () { D.set("intro.pac", true); b.hidden = true; });
    }
  }

  if (q.has("perfil") || !D.perfil()) mostrar("perfil");
  else if (q.has("intro") || !D.get("intro." + (D.isPro() ? "pro" : "pac"), false)) { pintarIntro(); mostrar("intro"); }
  else { pintarInicio(); mostrar("inicio"); }
})();
