/**
 * Goetheanum – Wöchentlicher Beitrags-Agent
 *
 * Cron-Trigger:
 *   Donnerstag 09:00 UTC → Beitragende für nächste Woche aus KV lesen,
 *                           Einladungstext formulieren, in KV zwischenspeichern.
 *   Montag     07:00 UTC → Gespeicherte Einladung per Resend-API verschicken.
 *
 * HTTP-Admin-Endpunkt (Bearer-geschützt):
 *   GET  /schedule              → Zeitplan-Einträge der nächsten 8 Wochen anzeigen
 *   POST /schedule              → Eintrag anlegen/überschreiben
 *   DELETE /schedule?week=YYYY-WW → Eintrag löschen
 *   GET  /pending               → Aktuell vorbereitete Einladung anzeigen
 *   POST /send-now              → Einladung sofort versenden (Test)
 */

export default {
  // ── Cron-Handler ──────────────────────────────────────────────────────────
  async scheduled(event, env, ctx) {
    const now = new Date(event.scheduledTime);
    const dow = now.getUTCDay(); // 0=So … 4=Do … 1=Mo

    if (dow === 4) {
      // Donnerstag: Einladung vorbereiten
      await prepareInvitation(env, now);
    } else if (dow === 1) {
      // Montag: Einladung versenden
      await sendPendingInvitation(env, now);
    }
  },

  // ── HTTP-Handler (Admin) ───────────────────────────────────────────────────
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // Admin-Auth prüfen
    const adminToken = String(env.ADMIN_TOKEN || "").trim();
    if (adminToken) {
      const auth = request.headers.get("Authorization") || "";
      if (auth !== "Bearer " + adminToken) {
        return json({ error: "Unauthorized" }, 401);
      }
    }

    const path = url.pathname.replace(/\/$/, "") || "/";

    // GET /schedule
    if (request.method === "GET" && path === "/schedule") {
      return handleGetSchedule(env);
    }

    // POST /schedule
    if (request.method === "POST" && path === "/schedule") {
      return handlePostSchedule(request, env);
    }

    // DELETE /schedule
    if (request.method === "DELETE" && path === "/schedule") {
      const week = url.searchParams.get("week");
      if (!week) return json({ error: "Parameter 'week' fehlt (Format: YYYY-WW)" }, 400);
      await env.SCHEDULE_KV.delete("week_" + week);
      return json({ ok: true, deleted: week });
    }

    // GET /pending
    if (request.method === "GET" && path === "/pending") {
      const pending = await env.SCHEDULE_KV.get("pending_invitation", "json");
      if (!pending) return json({ ok: false, message: "Keine vorbereitete Einladung vorhanden" });
      return json({ ok: true, pending });
    }

    // POST /send-now  (sofortiger Test-Versand)
    if (request.method === "POST" && path === "/send-now") {
      const result = await sendPendingInvitation(env, new Date());
      return json(result);
    }

    // POST /prepare-now  (Vorbereitung manuell auslösen)
    if (request.method === "POST" && path === "/prepare-now") {
      const result = await prepareInvitation(env, new Date());
      return json(result);
    }

    return json({ error: "Not found" }, 404);
  }
};

// ── Kernlogik: Einladung vorbereiten (Donnerstag) ────────────────────────────

async function prepareInvitation(env, now) {
  const nextMonday = getNextMonday(now);
  const weekKey = isoWeekKey(nextMonday);
  const entry = await env.SCHEDULE_KV.get("week_" + weekKey, "json");

  const adminEmail = String(env.ADMIN_EMAIL || "").trim();

  if (!entry) {
    // Kein Eintrag → Erinnerung an Admin schicken
    if (adminEmail) {
      const weekLabel = formatWeekLabel(nextMonday);
      await sendEmail(env, {
        to: [adminEmail],
        subject: "Beitragende für " + weekLabel + " noch nicht eingetragen",
        html: reminderHtml(weekLabel, weekKey),
        text: reminderText(weekLabel, weekKey)
      });
    }
    return { ok: false, message: "Kein Eintrag für " + weekKey + " – Erinnerung versendet" };
  }

  const { subject, html, text } = composeInvitation(entry, nextMonday);

  await env.SCHEDULE_KV.put("pending_invitation", JSON.stringify({
    weekKey,
    subject,
    html,
    text,
    preparedAt: now.toISOString()
  }));

  return { ok: true, message: "Einladung für " + weekKey + " vorbereitet", subject };
}

// ── Kernlogik: Einladung versenden (Montag) ──────────────────────────────────

async function sendPendingInvitation(env, now) {
  const pending = await env.SCHEDULE_KV.get("pending_invitation", "json");

  if (!pending) {
    return { ok: false, message: "Keine vorbereitete Einladung in KV" };
  }

  const recipients = parseRecipients(env.RECIPIENTS);
  if (!recipients.length) {
    return { ok: false, message: "Keine Empfänger konfiguriert (RECIPIENTS)" };
  }

  try {
    await sendEmail(env, {
      to: recipients,
      subject: pending.subject,
      html: pending.html,
      text: pending.text
    });

    // Nach Versand löschen
    await env.SCHEDULE_KV.delete("pending_invitation");

    return { ok: true, message: "Einladung versendet an " + recipients.join(", ") };
  } catch (err) {
    return { ok: false, message: "Versand fehlgeschlagen: " + err.message };
  }
}

// ── Admin-Handler ────────────────────────────────────────────────────────────

async function handleGetSchedule(env) {
  const entries = [];
  const now = new Date();

  for (let i = 0; i < 8; i++) {
    const date = new Date(now);
    date.setUTCDate(date.getUTCDate() + i * 7);
    const monday = getNextMonday(date);
    const key = isoWeekKey(monday);
    const entry = await env.SCHEDULE_KV.get("week_" + key, "json");
    entries.push({ week: key, date: monday.toISOString().slice(0, 10), entry: entry || null });
  }

  return json({ ok: true, schedule: entries });
}

async function handlePostSchedule(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Ungültiges JSON" }, 400);
  }

  const { week, contributors, topic, note } = body;

  if (!week || !/^\d{4}-\d{2}$/.test(week)) {
    return json({ error: "Feld 'week' fehlt oder falsches Format (erwartet: YYYY-WW)" }, 400);
  }
  if (!contributors || !Array.isArray(contributors) || !contributors.length) {
    return json({ error: "Feld 'contributors' fehlt (Array von Namen)" }, 400);
  }

  const entry = {
    contributors: contributors.map((c) => String(c).trim()).filter(Boolean),
    topic: topic ? String(topic).trim() : "",
    note: note ? String(note).trim() : "",
    updatedAt: new Date().toISOString()
  };

  await env.SCHEDULE_KV.put("week_" + week, JSON.stringify(entry));
  return json({ ok: true, week, entry });
}

// ── E-Mail-Komposition ────────────────────────────────────────────────────────

function composeInvitation(entry, monday) {
  const dateLabel = formatDate(monday);
  const names = formatNames(entry.contributors);
  const topic = entry.topic || "";
  const note = entry.note || "";

  const subject = "Einladung Montagmorgen " + dateLabel;

  const topicLine = topic ? "<p><strong>Thema:</strong> " + escapeHtml(topic) + "</p>" : "";
  const noteLine = note ? "<p>" + escapeHtml(note) + "</p>" : "";
  const topicText = topic ? "Thema: " + topic + "\n" : "";
  const noteText = note ? note + "\n" : "";

  const html =
    '<div style="font-family:Georgia,serif;color:#1f2933;line-height:1.6;max-width:600px">' +
    '<p>Liebe Gemeinschaft,</p>' +
    '<p>am kommenden <strong>Montag, ' + escapeHtml(dateLabel) + '</strong>, ' +
    'wird <strong>' + escapeHtml(names) + '</strong> einen Beitrag gestalten.</p>' +
    topicLine +
    noteLine +
    '<p>Herzliche Einladung!</p>' +
    '<p style="color:#52606d;font-size:13px;margin-top:2em">Goetheanum</p>' +
    '</div>';

  const text =
    "Liebe Gemeinschaft,\n\n" +
    "am kommenden Montag, " + dateLabel + ", " +
    "wird " + names + " einen Beitrag gestalten.\n\n" +
    topicText +
    noteText +
    "\nHerzliche Einladung!\n\nGoetheanum\n";

  return { subject, html, text };
}

function reminderHtml(weekLabel, weekKey) {
  return (
    '<div style="font-family:Arial,sans-serif;color:#1f2937;line-height:1.5">' +
    '<p>Hinweis: Für <strong>' + escapeHtml(weekLabel) + '</strong> sind noch keine ' +
    'Beitragenden im Zeitplan eingetragen.</p>' +
    '<p>Bitte über die Admin-API einen Eintrag anlegen:</p>' +
    '<pre style="background:#f3f4f6;padding:12px;border-radius:4px">' +
    'POST /schedule\n' +
    '{\n' +
    '  "week": "' + escapeHtml(weekKey) + '",\n' +
    '  "contributors": ["Vorname Nachname"],\n' +
    '  "topic": "Optionales Thema"\n' +
    '}</pre>' +
    '</div>'
  );
}

function reminderText(weekLabel, weekKey) {
  return (
    "Hinweis: Für " + weekLabel + " sind noch keine Beitragenden im Zeitplan eingetragen.\n\n" +
    "Bitte über die Admin-API einen Eintrag anlegen:\n\n" +
    'POST /schedule\n{"week":"' + weekKey + '","contributors":["Vorname Nachname"]}\n'
  );
}

// ── E-Mail-Versand (Resend) ───────────────────────────────────────────────────

async function sendEmail(env, { to, subject, html, text }) {
  if (String(env.DRY_RUN || "0") === "1") {
    console.log("[DRY RUN] E-Mail würde gesendet:", subject, "→", to.join(", "));
    return { id: "dry-run" };
  }

  const apiKey = String(env.RESEND_API_KEY || "").trim();
  if (!apiKey) throw new Error("RESEND_API_KEY nicht gesetzt");

  const from = String(env.FROM_EMAIL || "Goetheanum <info@goetheanum.ch>").trim();
  const replyTo = String(env.REPLY_TO_EMAIL || "").trim();

  const payload = { from, to, subject, html, text };
  if (replyTo) payload.reply_to = replyTo;

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + apiKey,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const raw = await response.text();
  let body = {};
  try { body = raw ? JSON.parse(raw) : {}; } catch { body = { raw }; }

  if (!response.ok) {
    throw new Error((body && body.message) || ("Resend-Fehler " + response.status));
  }

  return body;
}

// ── Datums-Hilfsfunktionen ────────────────────────────────────────────────────

/** Nächsten Montag ab einem Datum berechnen (oder den gleichen Tag, falls Mo) */
function getNextMonday(from) {
  const d = new Date(from);
  d.setUTCHours(0, 0, 0, 0);
  const dow = d.getUTCDay();
  const daysUntilMonday = dow === 0 ? 1 : (8 - dow) % 7 || 7;
  d.setUTCDate(d.getUTCDate() + daysUntilMonday);
  return d;
}

/** ISO-Wochenschlüssel: "YYYY-WW" */
function isoWeekKey(date) {
  const d = new Date(date);
  d.setUTCHours(0, 0, 0, 0);
  // ISO-Woche: Donnerstag bestimmt die Woche
  d.setUTCDate(d.getUTCDate() + 3 - ((d.getUTCDay() + 6) % 7));
  const week1 = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  const weekNum = 1 + Math.round(((d - week1) / 86400000 - 3 + ((week1.getUTCDay() + 6) % 7)) / 7);
  const year = d.getUTCFullYear();
  return year + "-" + String(weekNum).padStart(2, "0");
}

const WEEKDAYS_DE = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
const MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Dezember"];

function formatDate(date) {
  return WEEKDAYS_DE[date.getUTCDay()] + ", " +
    date.getUTCDate() + ". " +
    MONTHS_DE[date.getUTCMonth()] + " " +
    date.getUTCFullYear();
}

function formatWeekLabel(monday) {
  return "Woche " + isoWeekKey(monday) + " (ab " + formatDate(monday) + ")";
}

function formatNames(arr) {
  if (!arr || !arr.length) return "N.N.";
  if (arr.length === 1) return arr[0];
  return arr.slice(0, -1).join(", ") + " und " + arr[arr.length - 1];
}

// ── Sonstige Hilfsfunktionen ─────────────────────────────────────────────────

function parseRecipients(raw) {
  if (!raw) return [];
  return String(raw).split(",").map((s) => s.trim()).filter(Boolean);
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders() }
  });
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type"
  };
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
