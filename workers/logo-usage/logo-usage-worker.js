import { dashboardHtml } from "./dashboard-html.js";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (url.pathname === "/health") {
      return json({ ok: true, service: "logo-usage" }, 200, cors);
    }

    if (url.pathname === "/collect") {
      if (request.method !== "POST") {
        return json({ error: "Method not allowed" }, 405, cors);
      }
      return collectEvent(request, env, cors);
    }

    if (url.pathname === "/dashboard") {
      if (request.method !== "GET") {
        return json({ error: "Method not allowed" }, 405, cors);
      }
      return html(dashboardHtml(url.origin), 200);
    }

    if (url.pathname === "/summary") {
      if (request.method !== "GET") {
        return json({ error: "Method not allowed" }, 405, cors);
      }
      return usageSummary(url, env, cors);
    }

    return json({ error: "Not found" }, 404, cors);
  }
};

async function collectEvent(request, env, cors) {
  if (!env.DB) {
    return json({ error: "D1 binding DB is missing" }, 500, cors);
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ error: "Invalid JSON payload" }, 400, cors);
  }

  const eventType = cleanToken(payload.eventType, 40);
  if (!["pageview", "export", "ui_change"].includes(eventType)) {
    return json({ error: "Unsupported event type" }, 400, cors);
  }

  const now = new Date();
  const date = now.toISOString().slice(0, 10);
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const ua = request.headers.get("user-agent") || "";
  const salt = String(env.USAGE_HASH_SALT || "").trim();
  if (!salt) {
    return json({ error: "USAGE_HASH_SALT is not configured" }, 500, cors);
  }
  const sessionHash = await sha256Hex(salt + "|session|" + cleanString(payload.sessionId, 120));
  const visitorDayHash = await sha256Hex(salt + "|visitor-day|" + date + "|" + ip + "|" + ua);
  const referrerHost = hostFromUrl(cleanString(payload.referrer, 500));

  const device = classifyDevice(payload.viewport, ua);
  const country = cleanToken(request.cf && request.cf.country ? request.cf.country : "unknown", 24);
  const colo = cleanToken(request.cf && request.cf.colo ? request.cf.colo : "unknown", 24);
  const cfRay = cleanString(request.headers.get("cf-ray") || "", 80);
  const exportFormat = eventType === "export" ? cleanToken(payload.exportFormat, 24) : "";

  await env.DB.prepare(
    `INSERT INTO logo_usage_events (
      occurred_at, event_date, event_type, path, referrer_host, country, colo,
      device, viewport_width, viewport_height, ui_lang, org, category, layout,
      logo_lang, color_mode, scale_value, advanced_open, custom_text_length,
      export_format, session_hash, visitor_day_hash, cf_ray
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      now.toISOString(),
      date,
      eventType,
      cleanPath(payload.path),
      referrerHost,
      country,
      colo,
      device,
      clampInt(payload.viewport && payload.viewport.width, 0, 10000),
      clampInt(payload.viewport && payload.viewport.height, 0, 10000),
      cleanToken(payload.uiLang, 12),
      cleanToken(payload.logo && payload.logo.org, 80),
      cleanToken(payload.logo && payload.logo.category, 80),
      cleanToken(payload.logo && payload.logo.layout, 80),
      cleanToken(payload.logo && payload.logo.lang, 12),
      cleanToken(payload.logo && payload.logo.mode, 40),
      cleanNumber(payload.logo && payload.logo.scale),
      payload.logo && payload.logo.advancedOpen ? 1 : 0,
      clampInt(payload.logo && payload.logo.customTextLength, 0, 2000),
      exportFormat,
      sessionHash,
      visitorDayHash,
      cfRay
    )
    .run();

  return json({ ok: true }, 202, cors);
}

async function usageSummary(url, env, cors) {
  if (!env.DB) {
    return json({ error: "D1 binding DB is missing" }, 500, cors);
  }

  const today = new Date().toISOString().slice(0, 10);
  const from = normalizeDate(url.searchParams.get("from")) || daysAgo(90);
  const to = normalizeDate(url.searchParams.get("to")) || today;

  const totals = await env.DB.prepare(
    `SELECT
      COUNT(*) AS events,
      COALESCE(SUM(CASE WHEN event_type = 'pageview' THEN 1 ELSE 0 END), 0) AS pageviews,
      COALESCE(SUM(CASE WHEN event_type = 'export' THEN 1 ELSE 0 END), 0) AS exports,
      COALESCE(SUM(CASE WHEN event_type = 'ui_change' THEN 1 ELSE 0 END), 0) AS ui_changes,
      COALESCE(SUM(CASE WHEN custom_text_length > 0 THEN 1 ELSE 0 END), 0) AS custom_text_events,
      COALESCE(SUM(CASE WHEN event_type = 'export' AND custom_text_length > 0 THEN 1 ELSE 0 END), 0) AS custom_text_exports,
      COUNT(DISTINCT visitor_day_hash) AS visitor_days,
      COUNT(DISTINCT session_hash) AS sessions
    FROM logo_usage_events
    WHERE event_date BETWEEN ? AND ?`
  )
    .bind(from, to)
    .first();

  const daily = await all(
    env,
    `SELECT event_date, event_type, COUNT(*) AS count
     FROM logo_usage_events
     WHERE event_date BETWEEN ? AND ?
     GROUP BY event_date, event_type
     ORDER BY event_date, event_type`,
    from,
    to
  );

  const dailyTotals = await all(
    env,
    `SELECT
       event_date,
       COUNT(*) AS events,
       COALESCE(SUM(CASE WHEN event_type = 'pageview' THEN 1 ELSE 0 END), 0) AS pageviews,
       COALESCE(SUM(CASE WHEN event_type = 'export' THEN 1 ELSE 0 END), 0) AS exports,
       COALESCE(SUM(CASE WHEN event_type = 'ui_change' THEN 1 ELSE 0 END), 0) AS ui_changes,
       COUNT(DISTINCT visitor_day_hash) AS visitor_days,
       COUNT(DISTINCT session_hash) AS sessions
     FROM logo_usage_events
     WHERE event_date BETWEEN ? AND ?
     GROUP BY event_date
     ORDER BY event_date`,
    from,
    to
  );

  const byEventType = await grouped(env, "event_type", from, to, "1 = 1");
  const byFormat = await grouped(env, "export_format", from, to, "event_type = 'export'");
  const byOrg = await grouped(env, "org", from, to, "event_type = 'export'");
  const byCategory = await grouped(env, "category", from, to, "event_type = 'export'");
  const byLayout = await grouped(env, "layout", from, to, "event_type = 'export'");
  const byMode = await grouped(env, "color_mode", from, to, "event_type = 'export'");
  const byLanguage = await grouped(env, "logo_lang", from, to, "event_type = 'export'");
  const byScale = await groupedExpression(
    env,
    "CASE WHEN scale_value = 0 THEN '' ELSE printf('%.1f', scale_value) END",
    from,
    to,
    "event_type = 'export'"
  );
  const byAdvanced = await groupedExpression(
    env,
    "CASE WHEN advanced_open = 1 THEN 'advanced_open' ELSE 'standard' END",
    from,
    to,
    "event_type = 'export'"
  );
  const byDevice = await grouped(env, "device", from, to, "1 = 1");
  const byUiLang = await grouped(env, "ui_lang", from, to, "1 = 1");
  const selectedByOrg = await grouped(env, "org", from, to, "event_type IN ('ui_change', 'export')");
  const selectedByCategory = await grouped(env, "category", from, to, "event_type IN ('ui_change', 'export')");
  const selectedByLayout = await grouped(env, "layout", from, to, "event_type IN ('ui_change', 'export')");
  const selectedByMode = await grouped(env, "color_mode", from, to, "event_type IN ('ui_change', 'export')");
  const selectedByLanguage = await grouped(env, "logo_lang", from, to, "event_type IN ('ui_change', 'export')");
  const selectedByAdvanced = await groupedExpression(
    env,
    "CASE WHEN advanced_open = 1 THEN 'advanced_open' ELSE 'standard' END",
    from,
    to,
    "event_type IN ('ui_change', 'export')"
  );
  const selectedByCustomText = await groupedExpression(
    env,
    "CASE WHEN custom_text_length > 0 THEN 'custom_text' ELSE 'auto_text' END",
    from,
    to,
    "event_type IN ('ui_change', 'export')"
  );
  const byCountry = await grouped(env, "country", from, to, "1 = 1");
  const byReferrer = await grouped(env, "referrer_host", from, to, "1 = 1");
  const byPath = await grouped(env, "path", from, to, "1 = 1");
  const byViewport = await groupedExpression(
    env,
    `CASE
       WHEN viewport_width = 0 THEN ''
       WHEN viewport_width < 700 THEN '<700'
       WHEN viewport_width < 1024 THEN '700-1023'
       WHEN viewport_width < 1440 THEN '1024-1439'
       ELSE '1440+'
     END`,
    from,
    to,
    "1 = 1"
  );
  const byHourUtc = await groupedExpression(
    env,
    "substr(occurred_at, 12, 2)",
    from,
    to,
    "1 = 1",
    24
  );
  const advancedTotals = await env.DB.prepare(
    `SELECT
      COUNT(*) AS events,
      COALESCE(SUM(CASE WHEN event_type = 'export' THEN 1 ELSE 0 END), 0) AS exports,
      COALESCE(SUM(CASE WHEN event_type = 'ui_change' THEN 1 ELSE 0 END), 0) AS ui_changes,
      COALESCE(SUM(CASE WHEN custom_text_length > 0 THEN 1 ELSE 0 END), 0) AS custom_text_events,
      COALESCE(SUM(CASE WHEN event_type = 'export' AND custom_text_length > 0 THEN 1 ELSE 0 END), 0) AS custom_text_exports,
      COUNT(DISTINCT session_hash) AS sessions
    FROM logo_usage_events
    WHERE event_date BETWEEN ? AND ? AND advanced_open = 1`
  )
    .bind(from, to)
    .first();
  const advancedByFormat = await grouped(env, "export_format", from, to, "advanced_open = 1 AND event_type = 'export'");
  const advancedByOrg = await grouped(env, "org", from, to, "advanced_open = 1 AND event_type IN ('ui_change', 'export')");
  const advancedByCategory = await grouped(env, "category", from, to, "advanced_open = 1 AND event_type IN ('ui_change', 'export')");
  const advancedByLayout = await grouped(env, "layout", from, to, "advanced_open = 1 AND event_type IN ('ui_change', 'export')");
  const advancedByMode = await grouped(env, "color_mode", from, to, "advanced_open = 1 AND event_type IN ('ui_change', 'export')");
  const advancedByLanguage = await grouped(env, "logo_lang", from, to, "advanced_open = 1 AND event_type IN ('ui_change', 'export')");
  const advancedByCustomText = await groupedExpression(
    env,
    "CASE WHEN custom_text_length > 0 THEN 'custom_text' ELSE 'auto_text' END",
    from,
    to,
    "advanced_open = 1 AND event_type IN ('ui_change', 'export')"
  );
  const recent = await all(
    env,
    `SELECT occurred_at, event_type, path, referrer_host, country, device, org, category,
            layout, logo_lang, color_mode, export_format
     FROM logo_usage_events
     WHERE event_date BETWEEN ? AND ?
     ORDER BY occurred_at DESC
     LIMIT 100`,
    from,
    to
  );

  return json(
    {
      ok: true,
      range: { from, to },
      totals,
      daily,
      dailyTotals,
      engagement: {
        byEventType,
        byDevice,
        byUiLang,
        byPath,
        byViewport,
        byHourUtc
      },
      selections: {
        byOrg: selectedByOrg,
        byCategory: selectedByCategory,
        byLayout: selectedByLayout,
        byMode: selectedByMode,
        byLanguage: selectedByLanguage,
        byAdvanced: selectedByAdvanced,
        byCustomText: selectedByCustomText
      },
      exports: {
        byFormat,
        byOrg,
        byCategory,
        byLayout,
        byMode,
        byLanguage,
        byScale,
        byAdvanced
      },
      audience: {
        byCountry,
        byReferrer
      },
      advanced: {
        totals: advancedTotals,
        byFormat: advancedByFormat,
        byOrg: advancedByOrg,
        byCategory: advancedByCategory,
        byLayout: advancedByLayout,
        byMode: advancedByMode,
        byLanguage: advancedByLanguage,
        byCustomText: advancedByCustomText
      },
      recent
    },
    200,
    cors
  );
}

async function grouped(env, field, from, to, extraWhere) {
  return all(
    env,
    `SELECT ${field} AS key, COUNT(*) AS count
     FROM logo_usage_events
     WHERE event_date BETWEEN ? AND ? AND ${extraWhere} AND ${field} != ''
     GROUP BY ${field}
     ORDER BY count DESC, key
     LIMIT 50`,
    from,
    to
  );
}

async function groupedExpression(env, expression, from, to, extraWhere, limit) {
  return all(
    env,
    `SELECT ${expression} AS key, COUNT(*) AS count
     FROM logo_usage_events
     WHERE event_date BETWEEN ? AND ? AND ${extraWhere}
     GROUP BY key
     HAVING key != ''
     ORDER BY count DESC, key
     LIMIT ${clampInt(limit || 50, 1, 100)}`,
    from,
    to
  );
}

async function all(env, sql, ...params) {
  const result = await env.DB.prepare(sql).bind(...params).all();
  return result.results || [];
}

function corsHeaders(request, env) {
  const requestOrigin = request.headers.get("origin") || "";
  const allowed = String(env.ALLOWED_ORIGINS || "https://phtok.github.io,https://grafik.goetheanum.ch,null")
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);

  let allowOrigin = "*";
  if (allowed.length && allowed[0] !== "*") {
    allowOrigin = allowed.includes(requestOrigin) ? requestOrigin : allowed[0];
  }

  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "authorization,content-type",
    "access-control-max-age": "86400",
    vary: "origin"
  };
}

function json(payload, status, headers) {
  const out = new Headers(headers || {});
  out.set("content-type", "application/json; charset=utf-8");
  out.set("cache-control", "no-store");
  return new Response(JSON.stringify(payload), { status, headers: out });
}

function html(body, status) {
  const headers = new Headers();
  headers.set("content-type", "text/html; charset=utf-8");
  headers.set("cache-control", "no-store");
  headers.set("x-robots-tag", "noindex, nofollow");
  headers.set("referrer-policy", "no-referrer");
  return new Response(body, { status, headers });
}

function cleanPath(value) {
  const text = cleanString(value, 500);
  if (!text) {
    return "";
  }
  try {
    const url = new URL(text, "https://phtok.github.io");
    return (url.pathname || "").slice(0, 240);
  } catch {
    return text.split("?")[0].slice(0, 240);
  }
}

function hostFromUrl(value) {
  if (!value) {
    return "";
  }
  try {
    return new URL(value).hostname.slice(0, 120);
  } catch {
    return "";
  }
}

function cleanString(value, maxLen) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value).trim().slice(0, maxLen);
}

function cleanToken(value, maxLen) {
  return cleanString(value, maxLen).replace(/[^a-zA-Z0-9_.:/@-]/g, "").slice(0, maxLen);
}

function cleanNumber(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) {
    return 0;
  }
  return Math.round(n * 1000) / 1000;
}

function clampInt(value, min, max) {
  const n = Math.round(Number(value));
  if (!Number.isFinite(n)) {
    return 0;
  }
  return Math.max(min, Math.min(max, n));
}

function classifyDevice(viewport, ua) {
  const width = clampInt(viewport && viewport.width, 0, 10000);
  const agent = String(ua || "").toLowerCase();
  if (width && width < 700) {
    return "mobile";
  }
  if (width && width < 1024) {
    return "tablet";
  }
  if (/mobile|iphone|android/.test(agent) && !/ipad|tablet/.test(agent)) {
    return "mobile";
  }
  if (/ipad|tablet/.test(agent)) {
    return "tablet";
  }
  return "desktop";
}

function normalizeDate(value) {
  const text = String(value || "").trim();
  return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : "";
}

function daysAgo(days) {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() - days);
  return date.toISOString().slice(0, 10);
}

async function sha256Hex(text) {
  const bytes = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
