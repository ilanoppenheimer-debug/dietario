/* Dietario · registro de presión arterial y glicemia del paciente.
   Los datos se guardan solo en este dispositivo (localStorage "dietario.registro"). No hay servidor.
   Para el control: impresión (o PDF), archivo CSV y un código QR que lleva los datos dentro de la URL (#fragmento,
   que el navegador no envía al servidor).
   Límites de referencia (pendientes de validación clínica): PA en casa 135/85; PA ≥180/110 alerta; glicemia <70 baja. */
(function () {
  "use strict";
  var D = window.Dietario, $ = function (s) { return document.querySelector(s); };
  var MOM = { pa: ["Mañana", "Noche"], gl: ["Ayunas", "Antes de comer", "Después de comer", "Al acostarse", "Otro"] };
  var REF = { sys: 135, dia: 85, sysU: 180, diaU: 110, hipo: 70 };
  var DIA = 864e5;
  var nf = function (x) { return Math.round(x).toLocaleString("es-CL"); };
  function fecha(t, larga) {
    var d = new Date(t);
    return d.toLocaleDateString("es-CL", larga ? { weekday: "short", day: "numeric", month: "short" } : { day: "numeric", month: "short" }) +
      " · " + d.toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" });
  }
  function avg(a) { return a.length ? a.reduce(function (s, x) { return s + x; }, 0) / a.length : null; }
  function paAlta(r) { return r.s >= REF.sys || r.d >= REF.dia; }
  function paUrg(r) { return r.s >= REF.sysU || r.d >= REF.diaU; }

  /* ---------------- vista compartida por QR ---------------- */
  if (document.body.hasAttribute("data-ver")) { ver(); return; }

  var data = D.get("registro", { pa: [], gl: [] });
  var tipo = new URLSearchParams(location.search).get("ver") === "gl" ? "gl" : "pa";
  var mom = null;
  function guardar() { D.set("registro", data); }

  function resumenPA(lista) {
    var r7 = lista.filter(function (r) { return r.t >= Date.now() - 7 * DIA; });
    if (!r7.length) return '<div class="a-card dash"><b>Sin mediciones de los últimos 7 días</b><span>Agrega tus mediciones para ver tu promedio.</span></div>';
    var s = avg(r7.map(function (r) { return r.s; })), d = avg(r7.map(function (r) { return r.d; })), alto = s >= REF.sys || d >= REF.dia;
    var pts = r7.slice().sort(function (a, b) { return a.t - b.t; }).slice(-14);
    var y = function (v) { return Math.round(105 - (Math.max(50, Math.min(200, v)) - 50) * 100 / 150); };
    var x = function (i) { return Math.round(10 + i * 300 / Math.max(1, pts.length - 1)); };
    var poly = function (k) { return pts.map(function (p, i) { return x(i) + "," + y(p[k]); }).join(" "); };
    return '<div class="a-card"><span class="a-lbl">Promedio últimos 7 días · ' + r7.length + ' mediciones</span>' +
      '<span class="a-big">' + nf(s) + "/" + nf(d) + ' <small>mmHg</small></span>' +
      '<span style="font-size:13.5px;font-weight:700;color:' + (alto ? "var(--a-amber-ink)" : "var(--a-green-dk)") + '">' +
      (alto ? "Sobre 135/85, el límite para mediciones en casa" : "Bajo 135/85, el límite para mediciones en casa") + "</span>" +
      (pts.length > 1 ? '<svg viewBox="0 0 320 112" width="100%" role="img" aria-label="Presión máxima y mínima de los últimos 7 días">' +
        '<line x1="0" y1="' + y(135) + '" x2="320" y2="' + y(135) + '" stroke="#B07A0E" stroke-dasharray="4 4" stroke-width="1.5"/>' +
        '<text x="318" y="' + (y(135) - 4) + '" text-anchor="end" font-size="10" fill="#8A5E00">135</text>' +
        '<line x1="0" y1="' + y(85) + '" x2="320" y2="' + y(85) + '" stroke="#B07A0E" stroke-dasharray="2 5" stroke-width="1"/>' +
        '<text x="318" y="' + (y(85) - 4) + '" text-anchor="end" font-size="10" fill="#8A5E00">85</text>' +
        '<polyline points="' + poly("s") + '" fill="none" stroke="#C2534A" stroke-width="2.5" stroke-linejoin="round"/>' +
        '<polyline points="' + poly("d") + '" fill="none" stroke="#3E78B8" stroke-width="2.5" stroke-linejoin="round"/></svg>' +
        '<div style="display:flex;gap:14px;font-size:12.5px;color:var(--a-muted)"><span><i style="display:inline-block;width:10px;height:3px;background:#C2534A;vertical-align:middle;margin-right:5px"></i>Máxima</span><span><i style="display:inline-block;width:10px;height:3px;background:#3E78B8;vertical-align:middle;margin-right:5px"></i>Mínima</span></div>' : "") +
      "</div>";
  }
  function resumenGL(lista) {
    var r7 = lista.filter(function (r) { return r.t >= Date.now() - 7 * DIA; });
    if (!r7.length) return '<div class="a-card dash"><b>Sin mediciones de los últimos 7 días</b><span>Agrega tus mediciones para ver tus promedios.</span></div>';
    var ay = avg(r7.filter(function (r) { return r.m === "Ayunas"; }).map(function (r) { return r.v; }));
    var po = avg(r7.filter(function (r) { return r.m === "Después de comer"; }).map(function (r) { return r.v; }));
    var lo = r7.filter(function (r) { return r.v < REF.hipo; }).length;
    var cell = function (v, t, c) { return '<div style="display:flex;flex-direction:column"><span class="a-big" style="font-size:26px' + (c ? ";color:" + c : "") + '">' + v + '</span><span class="a-muted" style="font-size:12px">' + t + "</span></div>"; };
    return '<div class="a-card"><span class="a-lbl">Últimos 7 días · ' + r7.length + ' mediciones</span><div class="a-fgrid3">' +
      cell(ay == null ? "—" : nf(ay), "Promedio en ayunas") + cell(po == null ? "—" : nf(po), "Promedio después de comer") +
      cell(lo, "Bajo 70", lo ? "#A3342A" : "") + "</div></div>";
  }
  function alerta() {
    var a = "";
    if (tipo === "pa" && data.pa.length) {
      var u = data.pa.slice().sort(function (x, y) { return y.t - x.t; })[0];
      if (paUrg(u)) a = ["Presión muy alta en tu última medición", "Repite la medición en 5 minutos. Si sigue igual o tienes dolor de pecho, falta de aire, debilidad o dificultad para hablar, ve a urgencia."];
    }
    if (tipo === "gl" && data.gl.some(function (r) { return r.v < REF.hipo && r.t >= Date.now() - 7 * DIA; }))
      a = ["Tuviste una glicemia bajo 70", "Si vuelve a pasar: toma 15 g de azúcar (3 cucharaditas en agua o 3 sobres), mídete de nuevo en 15 minutos y repite si sigue bajo 70. Avisa a tu médico."];
    $("#alerta").innerHTML = a ? '<div class="a-card warn"><b>⚠ ' + a[0] + "</b><span>" + a[1] + "</span></div>" : "";
  }
  function filas(t, lista, conBorrar) {
    var desde = Date.now() - 30 * DIA;
    var l = lista.filter(function (r) { return r.t >= desde; }).sort(function (a, b) { return b.t - a.t; });
    if (!l.length) return '<div class="a-row static"><span class="a-tx"><span>Sin mediciones de los últimos 30 días.</span></span></div>';
    return l.map(function (r) {
      var v, flag = "", ink = "var(--a-ink)";
      if (t === "pa") { v = r.s + "/" + r.d + " mmHg" + (r.p ? " · pulso " + r.p : ""); if (paUrg(r)) { flag = "Muy alta"; ink = "#A3342A"; } else if (paAlta(r)) { flag = "Sobre 135/85"; ink = "#8A5E00"; } }
      else { v = r.v + " mg/dL"; if (r.v < REF.hipo) { flag = "Baja"; ink = "#A3342A"; } }
      return '<div class="a-row static" style="min-height:52px"><span class="a-tx"><b style="font-size:15px;color:' + ink + '">' + v + "</b><span>" + fecha(r.t, true) + " · " + r.m.toLowerCase() + "</span></span>" +
        (flag ? '<span style="font-size:12px;font-weight:800;color:' + ink + '">' + flag + "</span>" : "") +
        (conBorrar ? '<button class="a-x a-noprint" type="button" data-borrar="' + t + ":" + r.t + '" aria-label="Borrar esta medición" style="width:40px;height:40px;border:0;background:none;color:var(--a-faint);font-size:16px;cursor:pointer">✕</button>' : "") +
        "</div>";
    }).join("");
  }
  function pintar() {
    document.querySelectorAll("[data-tipo]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-tipo") === tipo); });
    document.querySelectorAll("[data-solo]").forEach(function (el) { el.hidden = el.getAttribute("data-solo") !== tipo; });
    $("#resumen").innerHTML = tipo === "pa" ? resumenPA(data.pa) : resumenGL(data.gl);
    alerta();
    $("#lista").innerHTML = filas(tipo, data[tipo], true);
    if (!mom || MOM[tipo].indexOf(mom) < 0) mom = MOM[tipo][0];
    $("#momentos").innerHTML = MOM[tipo].map(function (m) { return '<button type="button" class="a-pill" data-mom="' + m + '" aria-pressed="' + (m === mom) + '">' + m + "</button>"; }).join("");
    impresion();
    if (!$("#llevar-panel").hidden) qr();
  }

  /* ---------------- formulario ---------------- */
  function ahoraLocal() { var d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 16); }
  function abrirForm(o) { $("#form").hidden = !o; $("#agregar").hidden = o; $("#f-err").hidden = true; if (o) { $("#f-t").value = ahoraLocal(); $(tipo === "pa" ? "#f-sys" : "#f-gl").focus(); } }
  $("#agregar").addEventListener("click", function () { abrirForm(true); $("#llevar-panel").hidden = true; });
  $("#cancelar").addEventListener("click", function () { abrirForm(false); });
  document.querySelectorAll("[data-tipo]").forEach(function (b) { b.addEventListener("click", function () { tipo = b.getAttribute("data-tipo"); history.replaceState(null, "", "?ver=" + tipo); pintar(); }); });
  $("#momentos").addEventListener("click", function (e) { var b = e.target.closest("[data-mom]"); if (b) { mom = b.getAttribute("data-mom"); pintar(); } });
  ["#f-sys", "#f-dia", "#f-pul", "#f-gl"].forEach(function (s) { $(s).addEventListener("input", function () { this.value = this.value.replace(/\D/g, "").slice(0, 3); }); });
  $("#form").addEventListener("submit", function (e) {
    e.preventDefault();
    var t = new Date($("#f-t").value).getTime(), err = "";
    if (!t || t > Date.now() + 36e5) err = "Revisa la fecha y hora.";
    if (tipo === "pa") {
      var s = +$("#f-sys").value, d = +$("#f-dia").value, p = +$("#f-pul").value || null;
      if (!(s >= 60 && s <= 260) || !(d >= 30 && d <= 160) || s <= d) err = err || "Revisa los valores: la máxima va entre 60 y 260, la mínima entre 30 y 160, y la máxima debe ser mayor.";
      else if (p && !(p >= 30 && p <= 220)) err = "Revisa el pulso (entre 30 y 220).";
      if (!err) { data.pa.push({ t: t, s: s, d: d, p: p, m: mom }); $("#f-sys").value = $("#f-dia").value = $("#f-pul").value = ""; }
    } else {
      var v = +$("#f-gl").value;
      if (!(v >= 20 && v <= 600)) err = err || "Revisa el valor: entre 20 y 600 mg/dL.";
      if (!err) { data.gl.push({ t: t, v: v, m: mom }); $("#f-gl").value = ""; }
    }
    if (err) { $("#f-err").textContent = err; $("#f-err").hidden = false; return; }
    guardar(); abrirForm(false); pintar();
  });
  $("#lista").addEventListener("click", function (e) {
    var b = e.target.closest("[data-borrar]"); if (!b) return;
    var k = b.getAttribute("data-borrar").split(":"), t = +k[1];
    data[k[0]] = data[k[0]].filter(function (r) { return r.t !== t; }); guardar(); pintar();
  });
  $("#borrar-todo").addEventListener("click", function () {
    if (!confirm("¿Borrar todas tus mediciones de este teléfono?")) return;
    data = { pa: [], gl: [] }; guardar(); pintar();
  });

  /* ---------------- llevar al control ---------------- */
  $("#llevar").addEventListener("click", function () { var p = $("#llevar-panel"); p.hidden = !p.hidden; abrirForm(false); if (!p.hidden) qr(); });

  function impresion() {
    var hoy = new Date().toLocaleDateString("es-CL", { day: "numeric", month: "long", year: "numeric" });
    var seccion = function (t, titulo, res) {
      return '<h2 class="a-h" style="font-size:18px;margin:14px 0 6px">' + titulo + "</h2>" + res + '<div class="a-card list" style="margin-top:8px">' + filas(t, data[t], false) + "</div>";
    };
    $("#imp-pie").innerHTML = '<div style="border-bottom:2px solid #15332A;padding-bottom:8px;margin-bottom:6px"><b class="a-h" style="font-size:22px">Registro en casa · Dietario</b><br>' +
      '<span>Nombre: ______________________________ · Impreso el ' + hoy + "</span></div>" +
      seccion("pa", "Presión arterial (últimos 30 días)", resumenPA(data.pa)) + seccion("gl", "Glicemia capilar (últimos 30 días)", resumenGL(data.gl)) +
      '<p class="a-p a-foot" style="margin-top:10px">Mediciones hechas por el paciente en su casa. Referencia en casa: 135/85 mmHg.</p>';
  }
  /* En la impresión se ocultan resumen y lista de pantalla: va el informe completo con ambas mediciones. */
  var st = document.createElement("style");
  st.textContent = "@media print{#resumen,#alerta,#lista,.a-head,.a-foot{display:none!important}#imp-pie .a-foot{display:block!important}}";
  document.head.appendChild(st);

  function csv() {
    var l = ["tipo;fecha;hora;momento;maxima;minima;pulso;glicemia"];
    var f = function (t) { var d = new Date(t); return d.toLocaleDateString("es-CL") + ";" + d.toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" }); };
    data.pa.slice().sort(function (a, b) { return a.t - b.t; }).forEach(function (r) { l.push("presion;" + f(r.t) + ";" + r.m + ";" + r.s + ";" + r.d + ";" + (r.p || "") + ";"); });
    data.gl.slice().sort(function (a, b) { return a.t - b.t; }).forEach(function (r) { l.push("glicemia;" + f(r.t) + ";" + r.m + ";;;;" + r.v); });
    return "﻿" + l.join("\r\n");
  }
  $("#enviar").addEventListener("click", function () {
    var nombre = "registro-dietario-" + new Date().toISOString().slice(0, 10) + ".csv";
    var file = new File([csv()], nombre, { type: "text/csv" });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      navigator.share({ files: [file], title: "Mi registro de presión y glicemia" }).catch(function () {});
    } else {
      var a = document.createElement("a"); a.href = URL.createObjectURL(file); a.download = nombre; document.body.appendChild(a); a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    }
  });

  /* Formato compacto del QR: v1~base(horas, base 36)~pa~gl. Cada medición: horas desde base . valores . momento (índice). */
  function codificar() {
    var desde = Date.now() - 14 * DIA, H = 36e5;
    var pa = data.pa.filter(function (r) { return r.t >= desde; }).sort(function (a, b) { return b.t - a.t; }).slice(0, 56);
    var gl = data.gl.filter(function (r) { return r.t >= desde; }).sort(function (a, b) { return b.t - a.t; }).slice(0, 56);
    var todos = pa.concat(gl); if (!todos.length) return null;
    var base = Math.floor(Math.min.apply(null, todos.map(function (r) { return r.t; })) / H);
    var b36 = function (n) { return n.toString(36); };
    var P = pa.map(function (r) { return [b36(Math.round(r.t / H) - base), b36(r.s), b36(r.d), r.p ? b36(r.p) : "", MOM.pa.indexOf(r.m)].join("."); }).join(",");
    var G = gl.map(function (r) { return [b36(Math.round(r.t / H) - base), b36(r.v), MOM.gl.indexOf(r.m)].join("."); }).join(",");
    return "1~" + b36(base) + "~" + P + "~" + G;
  }
  function qr() {
    var box = $("#qr"), c = codificar();
    if (!c) { box.innerHTML = '<span class="a-muted" style="font-size:12px;text-align:center;padding:8px">Sin mediciones de los últimos 14 días</span>'; return; }
    var url = location.origin + "/registro/ver.html#" + c;
    try {
      var q = window.qrcode(0, "L"); q.addData(url); q.make();
      var n = q.getModuleCount(), cell = Math.max(2, Math.floor(132 / (n + 8)));
      box.innerHTML = q.createSvgTag({ cellSize: cell, margin: cell * 4, scalable: true });
      var svgEl = box.querySelector("svg"); svgEl.setAttribute("width", "132"); svgEl.setAttribute("height", "132");
      svgEl.setAttribute("role", "img"); svgEl.setAttribute("aria-label", "Código QR con tus mediciones de los últimos 14 días");
    } catch (e) { box.innerHTML = '<span class="a-muted" style="font-size:12px">Demasiadas mediciones para un código. Usa imprimir o enviar archivo.</span>'; }
  }

  pintar();

  /* ---------------- ver.html: decodifica el QR ---------------- */
  function ver() {
    var out = $("#ver-out"), h = decodeURIComponent(location.hash.slice(1)).split("~");
    if (h[0] !== "1" || h.length < 4) { out.innerHTML = '<div class="a-card warn"><b>No se pudo leer el registro</b><span>Pide al paciente que vuelva a mostrar el código.</span></div>'; return; }
    var H = 36e5, base = parseInt(h[1], 36), p36 = function (x) { return parseInt(x, 36); };
    var pa = h[2] ? h[2].split(",").map(function (s) { var a = s.split("."); return { t: (base + p36(a[0])) * H, s: p36(a[1]), d: p36(a[2]), p: a[3] ? p36(a[3]) : null, m: MOM.pa[+a[4]] || "—" }; }) : [];
    var gl = h[3] ? h[3].split(",").map(function (s) { var a = s.split("."); return { t: (base + p36(a[0])) * H, v: p36(a[1]), m: MOM.gl[+a[2]] || "—" }; }) : [];
    data = { pa: pa, gl: gl };
    var ult = Math.max.apply(null, pa.concat(gl).map(function (r) { return r.t; }));
    $("#ver-sub").textContent = pa.length + " de presión y " + gl.length + " de glicemia · hasta el " + new Date(ult).toLocaleDateString("es-CL", { day: "numeric", month: "long" });
    var lista = function (t, l) { return '<div class="a-card list">' + filasVer(t, l) + "</div>"; };
    function filasVer(t, l) {
      return l.sort(function (a, b) { return b.t - a.t; }).map(function (r) {
        var v = t === "pa" ? r.s + "/" + r.d + (r.p ? " · " + r.p + " lpm" : "") : r.v + " mg/dL";
        var bad = t === "pa" ? paAlta(r) : r.v < REF.hipo;
        return '<div class="a-row static" style="min-height:44px"><span class="a-tx"><b style="font-size:15px;' + (bad ? "color:#A3342A" : "") + '">' + v + "</b><span>" + fecha(r.t, true) + " · " + r.m.toLowerCase() + "</span></span></div>";
      }).join("") || '<div class="a-row static"><span class="a-tx"><span>Sin mediciones.</span></span></div>';
    }
    /* promedios relativos a la última medición (los datos pueden tener días) */
    var ref = ult, r7 = function (l) { return l.filter(function (r) { return r.t >= ref - 7 * DIA; }); };
    var pa7 = r7(pa), gl7 = r7(gl);
    var resPA = pa7.length ? '<div class="a-card"><span class="a-lbl">Promedio 7 días previos a la última · ' + pa7.length + ' mediciones</span><span class="a-big">' +
      nf(avg(pa7.map(function (r) { return r.s; }))) + "/" + nf(avg(pa7.map(function (r) { return r.d; }))) + ' <small>mmHg</small></span><span class="a-foot">Referencia en casa: 135/85</span></div>' : "";
    var ay = avg(gl7.filter(function (r) { return r.m === "Ayunas"; }).map(function (r) { return r.v; }));
    var po = avg(gl7.filter(function (r) { return r.m === "Después de comer"; }).map(function (r) { return r.v; }));
    var resGL = gl7.length ? '<div class="a-card"><span class="a-lbl">Glicemia · 7 días previos a la última</span><span>Ayunas: <b>' + (ay == null ? "—" : nf(ay)) +
      "</b> · Después de comer: <b>" + (po == null ? "—" : nf(po)) + "</b> · Bajo 70: <b>" + gl7.filter(function (r) { return r.v < REF.hipo; }).length + "</b></span></div>" : "";
    out.innerHTML = (pa.length ? '<span class="a-lbl">Presión arterial</span>' + resPA + lista("pa", pa) : "") +
      (gl.length ? '<span class="a-lbl" style="display:block;margin-top:14px">Glicemia capilar</span>' + resGL + lista("gl", gl) : "");
    out.style.cssText = "display:flex;flex-direction:column;gap:10px";
  }
})();
