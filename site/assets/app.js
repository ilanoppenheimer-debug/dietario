/* Dietario · comportamiento común de la app.
   - Perfil (paciente/profesional) e introducción: se guardan en este dispositivo (localStorage), no son datos de salud.
   - Navegación inferior (celular) o lateral (computador) según el perfil.
   - Selector de secciones: cualquier [data-secs] con hijos [data-sec="Título"] muestra una sección a la vez.
   - Mis dietas: [data-mis="id"] guarda o quita la dieta.
   Nada de esto sale del dispositivo. */
(function () {
  "use strict";
  var D = window.Dietario = window.Dietario || {};
  var body = document.body;
  var ROOT = body.getAttribute("data-root") || "";

  /* ---------- almacenamiento seguro ---------- */
  function get(k, def) { try { var v = localStorage.getItem("dietario." + k); return v == null ? def : JSON.parse(v); } catch (e) { return def; } }
  function set(k, v) { try { localStorage.setItem("dietario." + k, JSON.stringify(v)); } catch (e) {} }
  D.get = get; D.set = set; D.root = ROOT;

  D.perfil = function () { return get("perfil", null); };
  D.setPerfil = function (p) { set("perfil", p); };
  D.isPro = function () { return D.perfil() === "pro"; };

  /* Llegada por QR del tríptico: entra como paciente sin pasar por la introducción. */
  if (body.hasAttribute("data-qr") && !D.perfil()) { D.setPerfil("pac"); set("qrNuevo", true); }

  var pro = D.isPro();
  body.classList.toggle("a-pro", pro);
  document.querySelectorAll("[data-pro]").forEach(function (el) { el.hidden = !pro; });
  document.querySelectorAll("[data-pac]").forEach(function (el) { el.hidden = pro; });

  /* ---------- íconos ---------- */
  var ICON = {
    home: "M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
    salud: "M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z",
    registro: "M3 12h4l3-8 4 16 3-8h4",
    dietas: "M4 6h16M4 12h16M4 18h10",
    clinica: "M4 20V10M10 20V4M16 20v-7M22 20H2",
    nosotros: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 11v6M12 7.5v.5"
  };
  function svg(d, extra) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + (extra || "") + '><path d="' + d + '"/></svg>'; }
  D.svg = svg;
  var LEAF = '<span class="a-mark"><svg width="20" height="20" viewBox="0 0 32 32" aria-hidden="true"><path d="M5 27C5 13 13 5 27 5c0 14-8 22-22 22z" fill="#FFFFFF"/></svg></span>';

  /* ---------- navegación ---------- */
  var nav = document.querySelector(".a-nav");
  if (nav) {
    var items = [["home", "Inicio", "index.html"]];
    if (!pro) items.push(["salud", "Mi salud", "salud/index.html"], ["registro", "Registro", "registro/index.html"]);
    items.push(["dietas", "Dietas", "dietas/index.html"]);
    if (pro) items.push(["clinica", "Clínica", "clinica/index.html"]);
    items.push(["nosotros", "Nosotros", "nosotros.html"]);
    var cur = body.getAttribute("data-nav");
    nav.innerHTML = '<a class="a-sbrand" href="' + ROOT + 'index.html">' + LEAF + '<span class="a-brand" style="font-size:19px">Dietario</span></a>' +
      items.map(function (n) {
        return '<a href="' + ROOT + n[2] + '"' + (n[0] === cur ? ' aria-current="page"' : "") + ">" + svg(ICON[n[0]]) + "<span>" + n[1] + "</span></a>";
      }).join("") +
      '<div class="a-sfoot"><a class="a-chip' + (pro ? " pro" : "") + '" href="' + ROOT + 'index.html?perfil">' + (pro ? "Profesional" : "Paciente") + ' · cambiar</a>' +
      '<span>Material educativo. Complementa, no reemplaza, la indicación de tu médico o nutricionista.</span></div>';
    nav.setAttribute("aria-label", "Navegación principal");
  }
  var chip = document.querySelector(".a-top .a-chip[data-perfil]");
  if (chip) { chip.textContent = pro ? "Profesional" : "Paciente"; chip.classList.toggle("pro", pro); chip.href = ROOT + "index.html?perfil"; }

  /* ---------- selector de secciones ---------- */
  var UP = "M6 15l6-6 6 6", DOWN = "M6 9l6 6 6-6";
  function slug(t) { return t.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  D.secciones = function (box) {
    if (box._secs) return box._secs;
    var secs = [].filter.call(box.children, function (c) { return c.hasAttribute("data-sec"); });
    if (!secs.length) return;
    secs.forEach(function (s) {
      if (!s.id) s.id = slug(s.getAttribute("data-sec"));
      var h = document.createElement("h2"); h.className = "a-sectitle"; h.textContent = s.getAttribute("data-sec"); s.insertBefore(h, s.firstChild);
    });
    var sel = document.createElement("div"); sel.className = "a-sel";
    sel.innerHTML = '<button type="button" class="a-selbtn" aria-expanded="false"><span class="a-selk"></span><b></b>' +
      svg(DOWN, ' width="20" height="20" style="color:var(--a-green)"') + '</button><div class="a-sellist" hidden role="list"></div>';
    box.parentNode.insertBefore(sel, box);
    var btn = sel.querySelector(".a-selbtn"), list = sel.querySelector(".a-sellist");
    list.innerHTML = secs.map(function (s, i) { return '<button type="button" class="a-selitem" role="listitem" data-i="' + i + '">' + s.getAttribute("data-sec") + "</button>"; }).join("");
    function open(o) { list.hidden = !o; btn.setAttribute("aria-expanded", o); btn.querySelector("path").setAttribute("d", o ? UP : DOWN); }
    function show(i, push) {
      i = Math.max(0, Math.min(secs.length - 1, i));
      secs.forEach(function (s, j) { s.hidden = j !== i; });
      btn.querySelector(".a-selk").textContent = "Sección " + (i + 1) + " de " + secs.length;
      btn.querySelector("b").textContent = secs[i].getAttribute("data-sec");
      [].forEach.call(list.children, function (b, j) { b.setAttribute("aria-current", j === i ? "true" : "false"); });
      if (push && box.hasAttribute("data-hash")) history.replaceState(null, "", "#" + secs[i].id);
      box.dispatchEvent(new CustomEvent("seccion", { detail: { id: secs[i].id, i: i } }));
    }
    btn.addEventListener("click", function () { open(list.hidden); });
    list.addEventListener("click", function (e) {
      var b = e.target.closest(".a-selitem"); if (!b) return;
      show(+b.getAttribute("data-i"), true); open(false); btn.focus();
    });
    document.addEventListener("click", function (e) { if (!sel.contains(e.target)) open(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !list.hidden) { open(false); btn.focus(); } });
    var api = {
      show: function (id) { var i = secs.findIndex(function (s) { return s.id === id; }); if (i >= 0) show(i, true); return i >= 0; },
      ids: secs.map(function (s) { return s.id; })
    };
    var start = 0;
    if (box.hasAttribute("data-hash") && location.hash) {
      var h = location.hash.slice(1), k = secs.findIndex(function (s) { return s.id === h; });
      if (k >= 0) { start = k; setTimeout(function () { window.scrollTo(0, 0); }, 0); }
    }
    show(start, false);
    box._secs = api;
    return api;
  };
  document.querySelectorAll("[data-secs]").forEach(function (b) { if (!b.closest("[hidden]")) D.secciones(b); });

  /* ---------- Mis dietas ---------- */
  D.mis = function () { return get("misdietas", []); };
  function pintarMis() {
    var mis = D.mis();
    document.querySelectorAll("[data-mis]").forEach(function (b) {
      var on = mis.indexOf(b.getAttribute("data-mis")) >= 0;
      b.setAttribute("aria-pressed", on);
      b.textContent = on ? "✓ En Mis dietas" : "+ Agregar a Mis dietas";
    });
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-mis]"); if (!b) return;
    var id = b.getAttribute("data-mis"), mis = D.mis(), i = mis.indexOf(id);
    if (i >= 0) mis.splice(i, 1); else mis.push(id);
    set("misdietas", mis); pintarMis();
  });
  pintarMis();

  /* ---------- barra superior que se esconde al bajar (celular) ---------- */
  var top = document.querySelector(".a-top");
  if (top) {
    var lastY = window.scrollY, ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY, d = y - lastY;
        if (y < 80 || d < -6) body.classList.remove("a-hidetop");
        else if (d > 6 && !document.querySelector(".a-sellist:not([hidden])")) body.classList.add("a-hidetop");
        if (Math.abs(d) > 6) lastY = y;
        ticking = false;
      });
    }, { passive: true });
    document.addEventListener("focusin", function () { if (document.activeElement && top.contains(document.activeElement)) body.classList.remove("a-hidetop"); });
  }

  /* ---------- botones de imprimir ---------- */
  document.addEventListener("click", function (e) { if (e.target.closest("[data-print]")) window.print(); });

  /* ---------- app instalable y sin conexión ---------- */
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register(ROOT + "sw.js").catch(function () {}); });
  }
})();
