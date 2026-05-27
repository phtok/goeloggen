export function dashboardHtml(workerOrigin) {
  return `<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Logo Generator Statistik</title>
  <style>
    :root {
      --bg: #f5f6f4;
      --ink: #2f3944;
      --muted: #697684;
      --line: #d8dedf;
      --panel: #ffffff;
      --dark: #37404c;
      --gold: #ebb565;
      --blue: #2e6fa3;
      --green: #648f77;
      --red: #bb6a62;
      --shadow: 0 10px 24px rgba(34, 42, 50, .08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0 0 auto 0;
      height: 6px;
      background: var(--gold);
      z-index: 10;
    }
    a { color: inherit; }
    button, input {
      font: inherit;
    }
    .wrap {
      width: min(1280px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 36px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 18px;
      margin-bottom: 16px;
    }
    .eyebrow {
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      color: var(--dark);
      font-size: clamp(28px, 4vw, 46px);
      line-height: 1;
      font-weight: 750;
      letter-spacing: 0;
    }
    .toplink {
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      text-decoration: none;
      color: var(--dark);
      box-shadow: 0 2px 8px rgba(34, 42, 50, .04);
      white-space: nowrap;
    }
    .controls {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 10px;
      padding: 12px;
      margin-bottom: 14px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    label {
      display: grid;
      gap: 4px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    input[type="date"] {
      width: 156px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 9px;
      color: var(--ink);
      background: #fff;
    }
    button, .json-link {
      min-height: 36px;
      border: 1px solid var(--dark);
      border-radius: 6px;
      padding: 8px 12px;
      background: var(--dark);
      color: #fff;
      cursor: pointer;
      text-decoration: none;
    }
    .json-link {
      background: #fff;
      color: var(--dark);
      border-color: var(--line);
    }
    .status {
      min-height: 22px;
      color: var(--muted);
      margin: 4px 0 12px;
    }
    .kpis {
      display: grid;
      grid-template-columns: repeat(6, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .kpi, .panel, .chart-panel, .table-panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .kpi {
      padding: 12px;
      min-width: 0;
    }
    .kpi .label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .05em;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .kpi .value {
      margin-top: 6px;
      font-size: 28px;
      line-height: 1;
      color: var(--dark);
      font-weight: 760;
    }
    .kpi .sub {
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
    }
    .chart-panel {
      padding: 14px;
      margin-bottom: 12px;
      overflow: hidden;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 16px;
      line-height: 1.2;
      color: var(--dark);
    }
    .chart {
      width: 100%;
      min-height: 260px;
      overflow: hidden;
    }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .legend span::before {
      content: "";
      display: inline-block;
      width: 9px;
      height: 9px;
      margin-right: 5px;
      border-radius: 50%;
      background: var(--c);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      align-items: start;
    }
    .panel {
      padding: 14px;
      min-width: 0;
    }
    .bars {
      display: grid;
      gap: 9px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: minmax(92px, 1fr) minmax(80px, 2fr) 52px;
      gap: 8px;
      align-items: center;
      min-width: 0;
    }
    .bar-key {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--ink);
    }
    .bar-track {
      height: 11px;
      border-radius: 999px;
      background: #e9edec;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      min-width: 2px;
      border-radius: inherit;
      background: var(--blue);
    }
    .bar-value {
      text-align: right;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }
    .empty {
      color: var(--muted);
      padding: 8px 0;
    }
    .hour-grid {
      display: grid;
      grid-template-columns: repeat(24, minmax(12px, 1fr));
      gap: 3px;
      align-items: end;
      min-height: 124px;
      padding-top: 4px;
    }
    .hour {
      display: grid;
      grid-template-rows: 1fr auto;
      gap: 5px;
      min-width: 0;
      height: 120px;
      color: var(--muted);
      font-size: 10px;
      text-align: center;
    }
    .hour span {
      align-self: end;
      min-height: 2px;
      background: var(--green);
      border-radius: 4px 4px 0 0;
    }
    .table-panel {
      padding: 14px;
      margin-top: 12px;
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 840px;
    }
    th, td {
      padding: 8px 7px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .05em;
      font-weight: 650;
    }
    td {
      color: var(--ink);
      max-width: 220px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    @media (max-width: 1050px) {
      .kpis { grid-template-columns: repeat(3, minmax(130px, 1fr)); }
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 720px) {
      .wrap { width: min(100% - 20px, 1280px); padding-top: 22px; }
      header { align-items: start; flex-direction: column; }
      .kpis, .grid { grid-template-columns: 1fr; }
      .bar-row { grid-template-columns: minmax(80px, 1fr) minmax(80px, 1.4fr) 46px; }
      input[type="date"] { width: 100%; }
      label { flex: 1 1 140px; }
      .chart { min-height: 220px; }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <header>
      <div>
        <p class="eyebrow">Goetheanum Logo Generator</p>
        <h1>Nutzungsstatistik</h1>
      </div>
      <a class="toplink" href="https://phtok.github.io/goeloggen/apps/logo-generator/" rel="noopener noreferrer">Generator oeffnen</a>
    </header>

    <section class="controls" aria-label="Zeitraum">
      <label>Von <input id="from" type="date"></label>
      <label>Bis <input id="to" type="date"></label>
      <button id="reload" type="button">Aktualisieren</button>
      <a id="jsonLink" class="json-link" href="#" target="_blank" rel="noopener noreferrer">JSON</a>
    </section>

    <div id="status" class="status">Lade Daten...</div>
    <section id="kpis" class="kpis"></section>

    <section class="chart-panel">
      <h2>Tagesverlauf</h2>
      <div id="dailyChart" class="chart"></div>
      <div class="legend">
        <span style="--c: var(--blue)">Pageviews</span>
        <span style="--c: var(--green)">Sessions</span>
        <span style="--c: var(--gold)">Exports</span>
      </div>
    </section>

    <section class="grid">
      <article class="panel"><h2>Event-Mix</h2><div id="eventType" class="bars"></div></article>
      <article class="panel"><h2>Abgefragte Sektionen</h2><div id="selectedOrg" class="bars"></div></article>
      <article class="panel"><h2>Abgefragte Bereiche</h2><div id="selectedCategory" class="bars"></div></article>
      <article class="panel"><h2>Benutzte Layouts</h2><div id="selectedLayout" class="bars"></div></article>
      <article class="panel"><h2>Benutzte Farbmodi</h2><div id="selectedMode" class="bars"></div></article>
      <article class="panel"><h2>Eigener Text</h2><div id="customText" class="bars"></div></article>
      <article class="panel"><h2>Exportformate</h2><div id="format" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Sektionen</h2><div id="org" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Bereiche</h2><div id="category" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Layouts</h2><div id="layout" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Farbmodi</h2><div id="mode" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Sprachen</h2><div id="language" class="bars"></div></article>
      <article class="panel"><h2>Exportierte Skalierung</h2><div id="scale" class="bars"></div></article>
      <article class="panel"><h2>Versteckte Optionen</h2><div id="advanced" class="bars"></div></article>
      <article class="panel"><h2>Versteckt: Nutzung</h2><div id="advancedUsage" class="bars"></div></article>
      <article class="panel"><h2>Versteckt: Bereiche</h2><div id="advancedCategory" class="bars"></div></article>
      <article class="panel"><h2>Versteckt: Formate</h2><div id="advancedFormat" class="bars"></div></article>
      <article class="panel"><h2>Versteckt: Farbmodi</h2><div id="advancedMode" class="bars"></div></article>
      <article class="panel"><h2>Versteckt: Eigener Text</h2><div id="advancedCustomText" class="bars"></div></article>
      <article class="panel"><h2>Geraete</h2><div id="device" class="bars"></div></article>
      <article class="panel"><h2>Viewport-Breite</h2><div id="viewport" class="bars"></div></article>
      <article class="panel"><h2>UI-Sprache</h2><div id="uiLang" class="bars"></div></article>
      <article class="panel"><h2>Laender</h2><div id="country" class="bars"></div></article>
      <article class="panel"><h2>Referrer</h2><div id="referrer" class="bars"></div></article>
      <article class="panel"><h2>Pfade</h2><div id="path" class="bars"></div></article>
      <article class="panel"><h2>Uhrzeit UTC</h2><div id="hours" class="hour-grid"></div></article>
    </section>

    <section class="table-panel">
      <h2>Letzte Ereignisse</h2>
      <div id="recent"></div>
    </section>
  </main>

  <script>
    var API_BASE = ${JSON.stringify(workerOrigin)};
    var COLORS = { pageviews: "#2e6fa3", sessions: "#648f77", exports: "#ebb565" };

    function byId(id) { return document.getElementById(id); }
    function esc(value) {
      return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
      });
    }
    function num(value) {
      return Number(value || 0);
    }
    function fmt(value) {
      return num(value).toLocaleString("de-CH");
    }
    function percent(part, total) {
      return total ? Math.round((num(part) / num(total)) * 1000) / 10 + "%" : "0%";
    }
    function todayIso() {
      return new Date().toISOString().slice(0, 10);
    }
    function daysAgoIso(days) {
      var date = new Date();
      date.setUTCDate(date.getUTCDate() - days);
      return date.toISOString().slice(0, 10);
    }
    function queryUrl() {
      var from = byId("from").value || daysAgoIso(89);
      var to = byId("to").value || todayIso();
      return API_BASE + "/summary?from=" + encodeURIComponent(from) + "&to=" + encodeURIComponent(to);
    }
    function setDefaults() {
      byId("from").value = daysAgoIso(89);
      byId("to").value = todayIso();
    }
    async function load() {
      byId("status").textContent = "Lade Daten...";
      byId("jsonLink").href = queryUrl();
      try {
        var response = await fetch(queryUrl(), { headers: { "accept": "application/json" } });
        if (!response.ok) {
          throw new Error("HTTP " + response.status);
        }
        var data = await response.json();
        render(data);
      } catch (err) {
        byId("status").textContent = "Konnte Statistik nicht laden: " + err.message;
      }
    }
    function kpi(label, value, sub) {
      return '<article class="kpi"><div class="label">' + esc(label) + '</div><div class="value">' + esc(value) + '</div><div class="sub">' + esc(sub || "") + '</div></article>';
    }
    function renderKpis(data) {
      var t = data.totals || {};
      var a = data.advanced && data.advanced.totals ? data.advanced.totals : {};
      var conversion = percent(t.exports, t.sessions);
      byId("kpis").innerHTML = [
        kpi("Pageviews", fmt(t.pageviews), fmt(t.visitor_days) + " Visitor-Tage"),
        kpi("Sessions", fmt(t.sessions), conversion + " Export/Sessions"),
        kpi("Exports", fmt(t.exports), fmt(t.custom_text_exports) + " mit eigenem Text"),
        kpi("UI-Aenderungen", fmt(t.ui_changes), fmt(t.events) + " Events gesamt"),
        kpi("Versteckte Optionen", fmt(a.sessions || 0) + " Sessions", fmt(a.exports || 0) + " Exports, " + fmt(a.custom_text_events || 0) + " eigene Texte"),
        kpi("Export-Rate", conversion, "Exports pro Session"),
        kpi("Zeitraum", data.range.from + " - " + data.range.to, "UTC-Datenbasis")
      ].join("");
    }
    function renderBars(id, rows, options) {
      var target = byId(id);
      rows = Array.isArray(rows) ? rows.slice(0, options && options.limit ? options.limit : 12) : [];
      if (!rows.length) {
        target.innerHTML = '<div class="empty">Noch keine Daten.</div>';
        return;
      }
      var max = rows.reduce(function (m, row) { return Math.max(m, num(row.count)); }, 0) || 1;
      target.innerHTML = rows.map(function (row) {
        var label = options && options.label ? options.label(row.key) : row.key;
        var width = Math.max(2, Math.round((num(row.count) / max) * 100));
        return '<div class="bar-row" title="' + esc(label) + '">' +
          '<div class="bar-key">' + esc(label) + '</div>' +
          '<div class="bar-track"><div class="bar-fill" style="width:' + width + '%"></div></div>' +
          '<div class="bar-value">' + fmt(row.count) + '</div>' +
        '</div>';
      }).join("");
    }
    function renderHours(rows) {
      var byHour = {};
      (rows || []).forEach(function (row) { byHour[String(row.key).padStart(2, "0")] = num(row.count); });
      var max = Object.keys(byHour).reduce(function (m, key) { return Math.max(m, byHour[key]); }, 0) || 1;
      var out = "";
      for (var h = 0; h < 24; h += 1) {
        var key = String(h).padStart(2, "0");
        var height = Math.max(2, Math.round((num(byHour[key]) / max) * 96));
        out += '<div class="hour" title="' + key + ':00 UTC - ' + fmt(byHour[key]) + ' Events">' +
          '<span style="height:' + height + 'px"></span><b>' + key + '</b></div>';
      }
      byId("hours").innerHTML = out;
    }
    function chartPoints(rows, key, width, height, pad, max) {
      if (!rows.length) { return ""; }
      return rows.map(function (row, index) {
        var x = pad + (rows.length === 1 ? 0 : (index / (rows.length - 1)) * (width - pad * 2));
        var y = height - pad - (num(row[key]) / max) * (height - pad * 2);
        return Math.round(x * 10) / 10 + "," + Math.round(y * 10) / 10;
      }).join(" ");
    }
    function renderDailyChart(rows) {
      rows = Array.isArray(rows) ? rows : [];
      if (!rows.length) {
        byId("dailyChart").innerHTML = '<div class="empty">Noch keine Tagesdaten.</div>';
        return;
      }
      var width = 960;
      var height = 260;
      var pad = 30;
      var max = rows.reduce(function (m, row) {
        return Math.max(m, num(row.pageviews), num(row.sessions), num(row.exports));
      }, 0) || 1;
      var last = rows[rows.length - 1];
      var first = rows[0];
      var grid = "";
      for (var i = 0; i <= 4; i += 1) {
        var y = pad + i * ((height - pad * 2) / 4);
        grid += '<line x1="' + pad + '" y1="' + y + '" x2="' + (width - pad) + '" y2="' + y + '" stroke="#d8dedf" stroke-width="1"/>';
      }
      byId("dailyChart").innerHTML =
        '<svg viewBox="0 0 ' + width + ' ' + height + '" width="100%" height="260" role="img" aria-label="Tagesverlauf">' +
          grid +
          '<polyline fill="none" stroke="' + COLORS.pageviews + '" stroke-width="3" points="' + chartPoints(rows, "pageviews", width, height, pad, max) + '"/>' +
          '<polyline fill="none" stroke="' + COLORS.sessions + '" stroke-width="3" points="' + chartPoints(rows, "sessions", width, height, pad, max) + '"/>' +
          '<polyline fill="none" stroke="' + COLORS.exports + '" stroke-width="3" points="' + chartPoints(rows, "exports", width, height, pad, max) + '"/>' +
          '<text x="' + pad + '" y="' + (height - 8) + '" fill="#697684" font-size="12">' + esc(first.event_date) + '</text>' +
          '<text x="' + (width - pad) + '" y="' + (height - 8) + '" fill="#697684" font-size="12" text-anchor="end">' + esc(last.event_date) + '</text>' +
          '<text x="' + pad + '" y="18" fill="#697684" font-size="12">max ' + fmt(max) + '</text>' +
        '</svg>';
    }
    function renderRecent(rows) {
      rows = Array.isArray(rows) ? rows : [];
      if (!rows.length) {
        byId("recent").innerHTML = '<div class="empty">Noch keine Ereignisse.</div>';
        return;
      }
      byId("recent").innerHTML = '<table><thead><tr>' +
        '<th>Zeit UTC</th><th>Typ</th><th>Format</th><th>Org</th><th>Kategorie</th><th>Layout</th><th>Modus</th><th>Geraet</th><th>Land</th><th>Referrer</th>' +
        '</tr></thead><tbody>' + rows.slice(0, 40).map(function (row) {
          return '<tr><td>' + esc(row.occurred_at) + '</td><td>' + esc(row.event_type) + '</td><td>' + esc(row.export_format) +
            '</td><td>' + esc(row.org) + '</td><td>' + esc(row.category) + '</td><td>' + esc(row.layout) +
            '</td><td>' + esc(row.color_mode) + '</td><td>' + esc(row.device) + '</td><td>' + esc(row.country) +
            '</td><td>' + esc(row.referrer_host) + '</td></tr>';
        }).join("") + '</tbody></table>';
    }
    function render(data) {
      renderKpis(data);
      renderDailyChart(data.dailyTotals || []);
      renderBars("eventType", data.engagement && data.engagement.byEventType);
      renderBars("selectedOrg", data.selections && data.selections.byOrg, { limit: 12 });
      renderBars("selectedCategory", data.selections && data.selections.byCategory, { limit: 12 });
      renderBars("selectedLayout", data.selections && data.selections.byLayout, { limit: 12 });
      renderBars("selectedMode", data.selections && data.selections.byMode);
      renderBars("customText", data.selections && data.selections.byCustomText, { label: function (key) { return key === "custom_text" ? "Eigener Text" : "Automatisch/kein eigener Text"; } });
      renderBars("format", data.exports && data.exports.byFormat);
      renderBars("org", data.exports && data.exports.byOrg, { limit: 10 });
      renderBars("category", data.exports && data.exports.byCategory, { limit: 10 });
      renderBars("layout", data.exports && data.exports.byLayout);
      renderBars("mode", data.exports && data.exports.byMode);
      renderBars("language", data.exports && data.exports.byLanguage);
      renderBars("scale", data.exports && data.exports.byScale);
      renderBars("advanced", data.exports && data.exports.byAdvanced, { label: function (key) { return key === "advanced_open" ? "Erweiterte Optionen offen" : "Standard"; } });
      var at = data.advanced && data.advanced.totals ? data.advanced.totals : {};
      renderBars("advancedUsage", [
        { key: "Sessions", count: at.sessions || 0 },
        { key: "Interaktionen", count: at.ui_changes || 0 },
        { key: "Exports", count: at.exports || 0 },
        { key: "Eigener Text", count: at.custom_text_events || 0 }
      ]);
      renderBars("advancedCategory", data.advanced && data.advanced.byCategory, { limit: 12 });
      renderBars("advancedFormat", data.advanced && data.advanced.byFormat);
      renderBars("advancedMode", data.advanced && data.advanced.byMode);
      renderBars("advancedCustomText", data.advanced && data.advanced.byCustomText, { label: function (key) { return key === "custom_text" ? "Eigener Text" : "Automatisch/kein eigener Text"; } });
      renderBars("device", data.engagement && data.engagement.byDevice);
      renderBars("viewport", data.engagement && data.engagement.byViewport);
      renderBars("uiLang", data.engagement && data.engagement.byUiLang);
      renderBars("country", data.audience && data.audience.byCountry);
      renderBars("referrer", data.audience && data.audience.byReferrer, { limit: 10 });
      renderBars("path", data.engagement && data.engagement.byPath, { limit: 10 });
      renderHours(data.engagement && data.engagement.byHourUtc);
      renderRecent(data.recent);
      byId("status").textContent = "Aktualisiert: " + new Date().toLocaleString("de-CH");
    }
    byId("reload").addEventListener("click", load);
    ["from", "to"].forEach(function (id) { byId(id).addEventListener("change", load); });
    setDefaults();
    load();
  </script>
</body>
</html>`;
}
