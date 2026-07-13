// =============================================================================
// Werkzeug-Auftrag-Worker · Absende-Weg (a) der Werkzeug-Schmiede
// -----------------------------------------------------------------------------
// Nimmt einen POST der Schmiede (apps/schmiede/) entgegen und legt daraus ein
// GitHub-Issue in phtok/goeloggen an – so landet ein Werkzeug-Wunsch direkt in
// der bestehenden Bau-Schleife, OHNE dass die absendende Person ein GitHub-Konto
// braucht. Das Token wohnt als Secret im Worker (nie im Repo, nie im Browser).
//
// Deploy + Secret: siehe README.md in diesem Ordner.
// Muster/Stil bewusst wie workers/logo-usage/logo-usage-worker.js.
// =============================================================================

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    if (url.pathname === "/health") {
      return json({ ok: true, service: "werkzeug-auftrag" }, 200, cors);
    }

    // Ein einziger Zweck: einen Auftrag annehmen. / und /auftrag sind gleichwertig.
    if (url.pathname === "/" || url.pathname === "/auftrag") {
      if (request.method !== "POST") {
        return json({ error: "Method not allowed" }, 405, cors);
      }
      return auftragAnlegen(request, env, cors);
    }

    return json({ error: "Not found" }, 404, cors);
  }
};

async function auftragAnlegen(request, env, cors) {
  const token = String(env.GITHUB_TOKEN || "").trim();
  if (!token) {
    return json({ error: "GITHUB_TOKEN is not configured" }, 500, cors);
  }
  const repo = cleanString(env.REPO, 140) || "phtok/goeloggen";

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ error: "Invalid JSON payload" }, 400, cors);
  }

  const auftrag = cleanString(payload.auftrag, 20000);
  if (auftrag.length < 20) {
    return json({ error: "Auftrag fehlt oder ist zu kurz" }, 400, cors);
  }
  const titel = cleanString(payload.titel, 120) || "ohne Namen";

  // Optionale Labels (env.LABEL, kommagetrennt). Standard: werkzeug-wunsch –
  // darauf hört die Bau-Schleife. Existiert das Label nicht, wird es beim
  // ersten Mal ohne Label erneut versucht (siehe unten), statt zu scheitern.
  const labels = String(env.LABEL || "werkzeug-wunsch")
    .split(",").map((v) => v.trim()).filter(Boolean);

  const issue = {
    title: "Werkzeug-Wunsch: " + titel,
    body: auftrag + "\n\n<sub>Eingegangen über die Werkzeug-Schmiede (apps/schmiede/).</sub>",
    labels
  };

  let res = await erstelleIssue(repo, token, issue);
  // 422 = meist ein noch nicht angelegtes Label. Einmal ohne Label wiederholen.
  if (res.status === 422 && labels.length) {
    res = await erstelleIssue(repo, token, { title: issue.title, body: issue.body });
  }

  if (!res.ok) {
    return json({ error: "GitHub lehnte den Auftrag ab", status: res.status }, 502, cors);
  }
  const data = await res.json();
  return json({ ok: true, url: data.html_url, number: data.number }, 201, cors);
}

function erstelleIssue(repo, token, issue) {
  return fetch("https://api.github.com/repos/" + repo + "/issues", {
    method: "POST",
    headers: {
      "authorization": "Bearer " + token,
      "accept": "application/vnd.github+json",
      "content-type": "application/json",
      // GitHub verlangt einen User-Agent, sonst 403.
      "user-agent": "goetheanum-werkzeug-schmiede"
    },
    body: JSON.stringify(issue)
  });
}

// --- Helfer (Stil wie logo-usage-worker.js) ---------------------------------

function corsHeaders(request, env) {
  const requestOrigin = request.headers.get("origin") || "";
  const allowed = String(
    env.ALLOWED_ORIGINS ||
    "https://phtok.github.io,https://werkzeuge.goetheanum.ch,https://tools.goetheanum.ch,https://grafik.goetheanum.ch,null"
  ).split(",").map((v) => v.trim()).filter(Boolean);

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

function json(payload, status, headers) {
  const out = new Headers(headers || {});
  out.set("content-type", "application/json; charset=utf-8");
  out.set("cache-control", "no-store");
  return new Response(JSON.stringify(payload), { status, headers: out });
}

function cleanString(value, maxLen) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value).trim().slice(0, maxLen);
}
