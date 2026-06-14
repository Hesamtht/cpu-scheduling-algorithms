/* ============================================================================
   CPU Scheduler Lab — shared client helpers
   ========================================================================== */
(function () {
  "use strict";

  const PALETTE = [
    "var(--p0)", "var(--p1)", "var(--p2)", "var(--p3)",
    "var(--p4)", "var(--p5)", "var(--p6)", "var(--p7)",
  ];
  const HEX = ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#14b8a6", "#f43f5e"];

  let colorMap = {};
  function resetColors() { colorMap = {}; }
  function colorFor(name) {
    if (!(name in colorMap)) {
      colorMap[name] = Object.keys(colorMap).length % PALETTE.length;
    }
    return PALETTE[colorMap[name]];
  }
  function hexFor(name) {
    if (!(name in colorMap)) {
      colorMap[name] = Object.keys(colorMap).length % PALETTE.length;
    }
    return HEX[colorMap[name]];
  }

  /* ----------------------------------------------------- animated Gantt */
  function renderGantt(container, gantt) {
    container.innerHTML = "";
    if (!gantt || !gantt.length) return;
    resetColors();

    // assign colors first (skip idle) so the legend + bars agree
    const procNames = [];
    gantt.forEach(function (s) {
      if (s.name !== "idle" && procNames.indexOf(String(s.name)) === -1) {
        procNames.push(String(s.name));
        colorFor(s.name);
      }
    });

    const total = gantt[gantt.length - 1].end;
    const wrap = document.createElement("div");
    wrap.className = "gantt";

    // legend
    const legend = document.createElement("div");
    legend.className = "gantt__legend";
    procNames.forEach(function (n) {
      const leg = document.createElement("span");
      leg.className = "leg";
      leg.innerHTML = '<span class="dot" style="color:' + colorFor(n) + ';background:' + colorFor(n) + '"></span>P' + n;
      legend.appendChild(leg);
    });
    wrap.appendChild(legend);

    // track
    const track = document.createElement("div");
    track.className = "gantt__track";
    gantt.forEach(function (seg, i) {
      const bar = document.createElement("div");
      const idle = seg.name === "idle";
      bar.className = "gantt__bar" + (idle ? " is-idle" : "");
      bar.style.flex = (seg.end - seg.start) + " 0 0";
      bar.style.setProperty("--c", idle ? "transparent" : colorFor(seg.name));
      bar.style.setProperty("--d", (i * 55) + "ms");
      const label = idle ? "" : "P" + seg.name;
      bar.innerHTML = '<span>' + label + '</span>';
      bar.title = (idle ? "Idle" : "P" + seg.name) + "  [" + seg.start + " → " + seg.end + "]";
      track.appendChild(bar);
    });
    wrap.appendChild(track);

    // axis ticks at each unique boundary
    const axis = document.createElement("div");
    axis.className = "gantt__axis";
    const marks = [0];
    gantt.forEach(function (s) { if (marks.indexOf(s.end) === -1) marks.push(s.end); });
    marks.forEach(function (m) {
      const t = document.createElement("span");
      t.className = "gantt__tick";
      t.style.left = (m / total * 100) + "%";
      t.textContent = m;
      axis.appendChild(t);
    });
    wrap.appendChild(axis);
    container.appendChild(wrap);
  }

  /* ------------------------------------------------------ count-up stats */
  function animateNumber(el, to, decimals) {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { el.textContent = to.toFixed(decimals); return; }
    const dur = 650;
    let start = null;
    function step(ts) {
      if (start === null) start = ts;
      const p = Math.min((ts - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (to * eased).toFixed(decimals);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = to.toFixed(decimals);
    }
    requestAnimationFrame(step);
    // Fallback: timers still fire when rAF is throttled (background/headless tabs)
    setTimeout(function () { el.textContent = to.toFixed(decimals); }, dur + 120);
  }

  function renderStats(container, items) {
    container.innerHTML = "";
    const grid = document.createElement("div");
    grid.className = "stats";
    items.forEach(function (it) {
      const tile = document.createElement("div");
      tile.className = "stat";
      if (it.accent) tile.style.setProperty("--stat-accent", it.accent);
      tile.innerHTML =
        '<div class="stat__label">' + it.label + '</div>' +
        '<div class="stat__value"><span class="num">0</span>' +
        (it.unit ? '<span class="stat__unit">' + it.unit + '</span>' : '') + '</div>';
      grid.appendChild(tile);
      const numEl = tile.querySelector(".num");
      const dec = it.decimals == null ? 2 : it.decimals;
      animateNumber(numEl, Number(it.value), dec);
    });
    container.appendChild(grid);
  }

  /* -------------------------------------------------------- results table */
  function renderResultTable(container, rows) {
    const cols = [
      ["name", "Process"],
      ["arrival_time", "Arrival"],
      ["burst_time", "Burst"],
      ["completion_time", "Completion"],
      ["turn_around_time", "Turnaround"],
      ["waiting_time", "Waiting"],
      ["response_time", "Response"],
    ];
    const present = cols.filter(function (c) { return rows[0] && c[0] in rows[0]; });
    let html = '<div class="table-wrap"><table class="data"><thead><tr>';
    present.forEach(function (c) { html += "<th>" + c[1] + "</th>"; });
    html += "</tr></thead><tbody>";
    rows.forEach(function (r) {
      html += "<tr>";
      present.forEach(function (c) {
        if (c[0] === "name") {
          html += '<td><span class="pname"><span class="dot" style="color:' + colorFor(r.name) +
                  ';background:' + colorFor(r.name) + '"></span>P' + r.name + "</span></td>";
        } else {
          html += "<td>" + r[c[0]] + "</td>";
        }
      });
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    container.innerHTML = html;
  }

  /* -------------------------------------------------------------- helpers */
  function fmt(n) { return (Math.round(Number(n) * 100) / 100); }

  function highlightNav() {
    const path = window.location.pathname;
    document.querySelectorAll(".nav__link").forEach(function (a) {
      const href = a.getAttribute("href");
      if (href === path || (href !== "/" && path.indexOf(href) === 0)) a.classList.add("is-active");
      else if (href === "/" && path === "/") a.classList.add("is-active");
    });
  }

  /* ------------------------------------------------------------ theming */
  function setTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("cpuviz-theme", t); } catch (e) {}
    document.dispatchEvent(new CustomEvent("themechange", { detail: t }));
  }
  function initTheme() {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      const cur = document.documentElement.getAttribute("data-theme") || "light";
      setTheme(cur === "dark" ? "light" : "dark");
    });
  }
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  document.addEventListener("DOMContentLoaded", function () {
    highlightNav();
    initTheme();
  });

  window.CPUViz = {
    colorFor: colorFor,
    hexFor: hexFor,
    resetColors: resetColors,
    renderGantt: renderGantt,
    renderStats: renderStats,
    renderResultTable: renderResultTable,
    animateNumber: animateNumber,
    setTheme: setTheme,
    cssVar: cssVar,
    fmt: fmt,
  };
})();
