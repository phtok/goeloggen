// GTV Subscriber Counter – Cloudflare Worker
//
// Routen:
//   GET  /data              → { entries: [...] }  (Dashboard-Datenquelle)
//   POST /webhook?token=SEC → Uscreen-Webhook-Empfänger
//   POST /entry             → Manueller Eintrag (Authorization: Bearer ADMIN_SECRET)
//
// KV-Binding: EVENTS_KV
// Secrets (via `wrangler secret put`):
//   WEBHOOK_SECRET   – Token für die Uscreen-Webhook-URL (?token=...)
//   ADMIN_SECRET     – Bearer-Token für den /entry-Endpunkt

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method === "GET" && (path === "/data" || path === "/")) {
      return handleGetData(env, cors);
    }

    if (request.method === "POST" && path === "/webhook") {
      return handleWebhook(request, env, url, cors);
    }

    if (request.method === "POST" && path === "/entry") {
      return handleManualEntry(request, env, cors);
    }

    return json({ error: "Not found" }, 404, cors);
  }
};

// ─── GET /data ────────────────────────────────────────────────────────────────

async function handleGetData(env, cors) {
  const raw = await env.EVENTS_KV.get("entries");
  const entries = raw ? JSON.parse(raw) : [];
  return json({ entries }, 200, cors);
}

// ─── POST /webhook ────────────────────────────────────────────────────────────
// Unterstützte Uscreen-Events:
//   subscription_assigned  → action "neu"
//   subscription_canceled  → action "bestandskündigung"
//   access_canceled        → action "bestandskündigung"

async function handleWebhook(request, env, url, cors) {
  const token = url.searchParams.get("token") || "";
  const expectedToken = String(env.WEBHOOK_SECRET || "").trim();
  if (expectedToken && token !== expectedToken) {
    return json({ error: "Unauthorized" }, 401, cors);
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400, cors);
  }

  const event = String(payload.event || "").toLowerCase();

  const EVENT_ACTION_MAP = {
    subscription_assigned: "neu",
    subscription_canceled: "bestandskündigung",
    access_canceled: "bestandskündigung",
  };

  if (!EVENT_ACTION_MAP[event]) {
    // Unbekanntes Event quittieren ohne zu speichern
    return json({ ok: true, skipped: true, event }, 200, cors);
  }

  // Uscreen verwendet je nach Event unterschiedliche Feldnamen
  const name = String(payload.user_name || payload.name || "Unbekannt").trim();
  const email = String(payload.user_email || payload.email || "").trim().toLowerCase();
  const type = String(payload.subscription_title || payload.offer_title || "").trim();

  if (!email) {
    return json({ error: "Missing email in payload" }, 400, cors);
  }

  const now = new Date();
  const date = now.toLocaleDateString("sv-SE", { timeZone: "Europe/Zurich" });
  const time = now.toLocaleTimeString("de-CH", {
    timeZone: "Europe/Zurich",
    hour: "2-digit",
    minute: "2-digit",
  });

  const entry = {
    date,
    time,
    name,
    email,
    type,
    action: EVENT_ACTION_MAP[event],
    lang: guessLang(email),
  };

  await appendEntry(env, entry);
  return json({ ok: true, entry }, 200, cors);
}

// ─── POST /entry ──────────────────────────────────────────────────────────────

async function handleManualEntry(request, env, cors) {
  const adminSecret = String(env.ADMIN_SECRET || "").trim();
  if (adminSecret) {
    const auth = request.headers.get("authorization") || "";
    const token = auth.replace(/^Bearer\s+/i, "").trim();
    if (token !== adminSecret) {
      return json({ error: "Unauthorized" }, 401, cors);
    }
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400, cors);
  }

  const email = String(payload.email || "").trim().toLowerCase();
  const date = String(payload.date || "").slice(0, 10);
  if (!email || !date) {
    return json({ error: "Pflichtfelder: date, email" }, 400, cors);
  }

  const entry = {
    date,
    time: String(payload.time || "").slice(0, 5),
    name: String(payload.name || "").trim(),
    email,
    type: String(payload.type || "").trim(),
    action: String(payload.action || "neu").trim(),
    lang: String(payload.lang || guessLang(email)).trim(),
  };

  await appendEntry(env, entry);
  return json({ ok: true, entry }, 200, cors);
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function appendEntry(env, entry) {
  const raw = await env.EVENTS_KV.get("entries");
  const entries = raw ? JSON.parse(raw) : [];
  entries.push(entry);
  await env.EVENTS_KV.put("entries", JSON.stringify(entries));
}

function guessLang(email = "") {
  const domain = (email.split("@")[1] || "").toLowerCase();
  if (/\.(de|ch|at)$|gmx\.|web\.de|bluewin|active\.ch/.test(domain)) return "de";
  if (/\.nl$/.test(domain)) return "nl";
  if (/\.fr$/.test(domain)) return "fr";
  if (/\.no$/.test(domain)) return "no";
  if (/\.se$/.test(domain)) return "sv";
  if (/\.jp$/.test(domain)) return "ja";
  if (/\.lv$/.test(domain)) return "lv";
  if (/\.(gr|com\.gr)$/.test(domain)) return "el";
  if (/btinternet|\.co\.uk$/.test(domain)) return "en";
  return "en";
}

function corsHeaders(request, env) {
  const requestOrigin = request.headers.get("origin") || "";
  const allowed = String(env.ALLOWED_ORIGINS || "*")
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
    "access-control-allow-headers": "content-type,authorization",
    "access-control-max-age": "86400",
    vary: "origin",
  };
}

function json(payload, status, headers) {
  const out = new Headers(headers || {});
  out.set("content-type", "application/json; charset=utf-8");
  return new Response(JSON.stringify(payload), { status, headers: out });
}
