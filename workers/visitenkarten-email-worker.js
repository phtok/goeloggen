export default {
  async fetch(request, env, ctx) {
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: cors
      });
    }

    if (request.method !== "POST") {
      return json({ error: "Method not allowed" }, 405, cors);
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return json({ error: "Invalid JSON payload" }, 400, cors);
    }

    const validation = validatePayload(payload, env);
    if (!validation.ok) {
      return json({ error: validation.error }, 400, cors);
    }

    const ip = request.headers.get("CF-Connecting-IP") || request.headers.get("x-forwarded-for") || "unknown";
    const rl = checkRateLimit(ip, env);
    if (!rl.ok) {
      return json({ error: "Too many requests. Please wait a few minutes." }, 429, cors);
    }

    const requestId = crypto.randomUUID();
    const recipientEmail = payload.recipientEmail.trim().toLowerCase();
    const forcedTarget = String(env.FORCE_TO_EMAIL || "").trim().toLowerCase();
    const deliveryRecipient = forcedTarget || recipientEmail;
    const ownerForwardMode = Boolean(forcedTarget && forcedTarget !== recipientEmail);
    const exportKind = payload.exportKind;
    const attachment = payload.attachment;

    const alertEmail = String(env.ALERT_EMAIL || "philipp.tok@goetheanum.ch").trim();
    const appUrl = String(env.APP_URL || "https://grafik.goetheanum.ch/visitenkarten").trim();

    const subject = ownerForwardMode
      ? "Visitenkarten-Export (Weiterleitung): " + kindLabel(exportKind) + " -> " + recipientEmail
      : "Visitenkarten-Export: " + kindLabel(exportKind);
    const warningMailto =
      "mailto:" +
      encodeURIComponent(alertEmail) +
      "?subject=" +
      encodeURIComponent("Ungewollter Visitenkarten-Export") +
      "&body=" +
      encodeURIComponent(
        "Ich habe den Visitenkarten-Export nicht angefordert.\\n\\n" +
          "Empfänger: " + recipientEmail + "\\n" +
          "Format: " + kindLabel(exportKind) + "\\n" +
          "Request-ID: " + requestId + "\\n"
      );

    const html =
      '<div style="font-family:Arial,sans-serif;color:#1f2933;line-height:1.45">' +
      "<p>Hier ist Ihre angeforderte Datei aus dem Goetheanum-Visitenkarten-Tool.</p>" +
      "<p><strong>Format:</strong> " + escapeHtml(kindLabel(exportKind)) + "</p>" +
      (ownerForwardMode ? "<p><strong>Zieladresse:</strong> " + escapeHtml(recipientEmail) + "</p>" : "") +
      "<p><strong>Request-ID:</strong> " + escapeHtml(requestId) + "</p>" +
      '<p>Falls Sie diese Datei nicht angefordert haben, melden Sie dies bitte sofort:<br />' +
      '<a href="' + warningMailto + '">Missbrauch melden</a></p>' +
      '<p style="color:#52606d;font-size:12px">Tool: <a href="' + escapeHtml(appUrl) + '">' + escapeHtml(appUrl) + "</a></p>" +
      "</div>";

    const text =
      "Hier ist Ihre angeforderte Datei aus dem Goetheanum-Visitenkarten-Tool.\\n\\n" +
      "Format: " + kindLabel(exportKind) + "\\n" +
      (ownerForwardMode ? "Zieladresse: " + recipientEmail + "\\n" : "") +
      "Request-ID: " + requestId + "\\n\\n" +
      "Falls Sie diese Datei nicht angefordert haben, melden Sie dies bitte sofort: " + warningMailto + "\\n" +
      "Tool: " + appUrl + "\\n";

    try {
      const delivery = await sendViaResend({
        env,
        recipientEmail: deliveryRecipient,
        alertEmail,
        subject,
        html,
        text,
        attachment,
        requestId
      });

      return json(
        {
          ok: true,
          requestId,
          deliveryId: delivery.id || null,
          deliveryMode: ownerForwardMode ? "owner_forward" : "direct",
          notice: ownerForwardMode
            ? "Temporärer Versandmodus: Anfrage wurde an die Grafik-Administration weitergeleitet."
            : null
        },
        200,
        cors
      );
    } catch (err) {
      return json(
        {
          error: err && err.message ? err.message : "Mail delivery failed"
        },
        502,
        cors
      );
    }
  }
};

const RATE_LIMIT = new Map();

function json(payload, status, headers) {
  const body = JSON.stringify(payload);
  const out = new Headers(headers || {});
  out.set("content-type", "application/json; charset=utf-8");
  return new Response(body, { status, headers: out });
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
    "access-control-allow-methods": "POST,OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "origin"
  };
}

function validatePayload(payload, env) {
  if (!payload || typeof payload !== "object") {
    return { ok: false, error: "Invalid request payload" };
  }

  const recipientEmail = String(payload.recipientEmail || "").trim().toLowerCase();
  if (!/^[a-z0-9._%+-]+@goetheanum\.ch$/i.test(recipientEmail)) {
    return { ok: false, error: "Recipient must be @goetheanum.ch" };
  }

  const kind = String(payload.exportKind || "").trim();
  if (!["pdf", "svg", "png", "sheet_pdf"].includes(kind)) {
    return { ok: false, error: "Unsupported export format" };
  }

  const attachment = payload.attachment;
  if (!attachment || typeof attachment !== "object") {
    return { ok: false, error: "Attachment is required" };
  }

  const fileName = String(attachment.fileName || "").trim();
  const mimeType = String(attachment.mimeType || "").trim().toLowerCase();
  const contentBase64 = String(attachment.contentBase64 || "").trim();
  const sizeBytes = Number(attachment.sizeBytes || 0);

  if (!fileName || fileName.length > 180) {
    return { ok: false, error: "Invalid attachment filename" };
  }

  const allowedMime = new Set(["application/pdf", "image/svg+xml", "image/png"]);
  if (!allowedMime.has(mimeType)) {
    return { ok: false, error: "Invalid attachment MIME type" };
  }

  if (!/^[A-Za-z0-9+/=]+$/.test(contentBase64)) {
    return { ok: false, error: "Attachment content is not base64" };
  }

  const estimatedBytes = estimateBase64Bytes(contentBase64);
  const effectiveBytes = sizeBytes > 0 ? sizeBytes : estimatedBytes;
  const maxBytes = Number(env.MAX_ATTACHMENT_BYTES || 14 * 1024 * 1024);
  if (effectiveBytes <= 0 || effectiveBytes > maxBytes) {
    return { ok: false, error: "Attachment too large" };
  }

  return { ok: true };
}

function estimateBase64Bytes(contentBase64) {
  const len = contentBase64.length;
  if (!len) {
    return 0;
  }
  let padding = 0;
  if (contentBase64.endsWith("==")) {
    padding = 2;
  } else if (contentBase64.endsWith("=")) {
    padding = 1;
  }
  return Math.floor((len * 3) / 4) - padding;
}

function checkRateLimit(ip, env) {
  const now = Date.now();
  const windowMs = Number(env.RATE_LIMIT_WINDOW_SEC || 900) * 1000;
  const maxRequests = Number(env.RATE_LIMIT_MAX || 12);

  const existing = RATE_LIMIT.get(ip) || [];
  const recent = existing.filter((ts) => now - ts < windowMs);

  if (recent.length >= maxRequests) {
    RATE_LIMIT.set(ip, recent);
    return { ok: false };
  }

  recent.push(now);
  RATE_LIMIT.set(ip, recent);
  return { ok: true };
}

function kindLabel(kind) {
  if (kind === "sheet_pdf") {
    return "Druckbogen (PDF)";
  }
  if (kind === "pdf") {
    return "PDF";
  }
  if (kind === "svg") {
    return "SVG";
  }
  if (kind === "png") {
    return "PNG";
  }
  return kind;
}

async function sendViaResend({ env, recipientEmail, alertEmail, subject, html, text, attachment, requestId }) {
  if (String(env.DRY_RUN || "0") === "1") {
    return { id: "dry-run-" + requestId };
  }

  const apiKey = String(env.RESEND_API_KEY || "").trim();
  if (!apiKey) {
    throw new Error("RESEND_API_KEY missing in worker environment");
  }

  const from = String(env.FROM_EMAIL || "Goetheanum Grafik <grafik@goetheanum.ch>").trim();

  const payload = {
    from,
    to: [recipientEmail],
    subject,
    html,
    text,
    attachments: [
      {
        filename: attachment.fileName,
        content: attachment.contentBase64,
        type: attachment.mimeType
      }
    ]
  };

  if (alertEmail && alertEmail.toLowerCase() !== recipientEmail.toLowerCase()) {
    payload.bcc = [alertEmail];
  }

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
  try {
    body = raw ? JSON.parse(raw) : {};
  } catch {
    body = { raw };
  }

  if (!response.ok) {
    throw new Error((body && body.message) || (body && body.error) || ("Resend error " + response.status));
  }

  return body;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
