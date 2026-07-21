// =============================================================================
// sortierer-commit · Supabase Edge Function — der Sortierer speichert direkt
// -----------------------------------------------------------------------------
// Nimmt vom Sortierer die drei Reihenfolgen (schublade/karten/karussell) und
// schreibt AUSSCHLIESSLICH das Feld «reihenfolge» in die tools.json auf GitHub —
// per Contents-API, mit dem aktuellen Stand als Basis (kein Stale-Clobber).
// Alles andere in der Datei bleibt byte-genau. Ein GitHub-Token liegt server-
// seitig, nie im Browser. Ein Passwort sperrt den Zugang; die Wirkfläche ist
// bewusst winzig (nur Menü-Reihenfolge, per Git jederzeit rückholbar).
//
// Konfiguration liegt NICHT in Env-Secrets, sondern in der Tabelle
// public.sortierer_config (nur Service-Role, RLS ohne Policies) — Hausmuster
// wie seelenkalender_config. Schlüssel (Spalte key → value):
//   sortierer_secret  frei gewähltes, langes Passwort (App-Passwort)
//   github_token      Fine-grained PAT, nur dieses Repo, Contents: Read+Write
//   github_repo       "phtok/goeloggen" (Vorgabe, wenn leer)
//   github_branch     "main" (Vorgabe, wenn leer)
// Die Funktion liest sie mit der automatisch injizierten Service-Role-Rolle
// (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY) — es sind KEINE eigenen Env-Secrets
// mehr zu setzen. Quelle im Repo: services/kistenpflege/sortierer-commit/index.ts
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB_URL = Deno.env.get("SUPABASE_URL") || "";
const SVC    = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const PATH   = "tools.json";

// Config aus public.sortierer_config lesen (nur Service-Role kommt an die Tabelle).
async function loadConfig(): Promise<Record<string, string>> {
  if (!SB_URL || !SVC) return {};
  const res = await fetch(`${SB_URL}/rest/v1/sortierer_config?select=key,value`, {
    headers: { apikey: SVC, Authorization: `Bearer ${SVC}` },
  });
  if (!res.ok) return {};
  const rows = await res.json().catch(() => []) as Array<{ key: string; value: string }>;
  const cfg: Record<string, string> = {};
  for (const r of rows) cfg[r.key] = r.value;
  return cfg;
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type, x-sortierer-secret",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

// UTF-8-sichere Base64-Umwandlung (atob/btoa sind Latin-1).
function b64ToText(b64: string): string {
  const bin = atob(b64.replace(/\n/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}
function textToB64(t: string): string {
  const bytes = new TextEncoder().encode(t);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

const arr = (a: string[]) => "[" + a.map((s) => JSON.stringify(s)).join(", ") + "]";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json(405, { error: "Nur POST." });

  const cfg = await loadConfig();
  const TOKEN  = cfg.github_token || "";
  const SECRET = cfg.sortierer_secret || "";
  const REPO   = cfg.github_repo || "phtok/goeloggen";
  const BRANCH = cfg.github_branch || "main";
  if (!TOKEN || !SECRET) return json(500, { error: "Funktion nicht konfiguriert (sortierer_config: github_token / sortierer_secret fehlen)." });

  // Passwort-Sperre.
  if ((req.headers.get("x-sortierer-secret") || "") !== SECRET) {
    return json(401, { error: "Passwort falsch." });
  }

  const body = await req.json().catch(() => null);
  const r = body && body.reihenfolge;
  const ok3 = r && ["schublade", "karten", "karussell"].every(
    (k) => Array.isArray(r[k]) && r[k].every((s: unknown) => typeof s === "string"),
  );
  if (!ok3) return json(400, { error: "reihenfolge (schublade/karten/karussell als Slug-Listen) fehlt." });

  const gh = {
    Authorization: `Bearer ${TOKEN}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "sortierer-commit",
    "X-GitHub-Api-Version": "2022-11-28",
  };

  // Aktuellen Stand holen (Text + sha).
  const getRes = await fetch(
    `https://api.github.com/repos/${REPO}/contents/${encodeURIComponent(PATH)}?ref=${BRANCH}`,
    { headers: gh },
  );
  if (!getRes.ok) return json(502, { error: "tools.json bei GitHub nicht lesbar.", status: getRes.status });
  const cur = await getRes.json();
  const text = b64ToText(cur.content || "");

  // Nur bekannte Slugs zulassen (kein Fremd-String in die Datei).
  let known: Set<string>;
  try {
    const parsed = JSON.parse(text);
    known = new Set((parsed.tools || []).map((t: { slug?: string }) => t.slug).filter(Boolean));
    known.add("empfehlungen"); // Karussell-Extra ohne eigenes Werkzeug
  } catch {
    return json(500, { error: "tools.json (aktuell) ist kein gültiges JSON." });
  }
  const clean = (a: string[]) => a.filter((s) => known.has(s));
  const neu = { schublade: clean(r.schublade), karten: clean(r.karten), karussell: clean(r.karussell) };

  // Ausgeblendete je Fläche (optional, rückwärtskompatibel). Nur bekannte Slugs.
  const a = r.aus && typeof r.aus === "object" ? r.aus : {};
  const cleanAus = (x: unknown) => Array.isArray(x) ? clean(x.filter((s) => typeof s === "string") as string[]) : [];
  const aus = { schublade: cleanAus(a.schublade), karussell: cleanAus(a.karussell), karten: cleanAus(a.karten) };

  // $hinweis aus dem Ist-Stand bewahren.
  const hm = text.match(/"\$hinweis":\s*("(?:[^"\\]|\\.)*")/);
  const hinweis = hm ? hm[1] : JSON.stringify("Vom Sortierer gepflegte Reihenfolgen (Slugs). Startseite und Schublade lesen sie; fehlt ein Eintrag, gilt die eingebaute Vorgabe. aus = je Fläche ausgeblendet (bleibt per Direktlink und in der Intern-Ansicht erreichbar). Verlauf = Git.");
  const block =
    '"reihenfolge": {\n' +
    '    "$hinweis": ' + hinweis + ',\n' +
    '    "schublade": ' + arr(neu.schublade) + ',\n' +
    '    "karten": ' + arr(neu.karten) + ',\n' +
    '    "karussell": ' + arr(neu.karussell) + ',\n' +
    '    "aus": { "schublade": ' + arr(aus.schublade) + ', "karussell": ' + arr(aus.karussell) + ', "karten": ' + arr(aus.karten) + " }\n" +
    "  }";

  // Nur den reihenfolge-Block ersetzen (Rest byte-genau).
  const re = /"reihenfolge"\s*:\s*\{[\s\S]*?\n {2}\}/;
  const next = re.test(text)
    ? text.replace(re, block)
    : text.replace(/\n\}\s*$/, ",\n  " + block + "\n}");

  if (next === text) return json(200, { ok: true, unchanged: true });
  try { JSON.parse(next); } catch { return json(500, { error: "Ergebnis wäre ungültiges JSON – nichts geschrieben." }); }

  // Committen.
  const putRes = await fetch(`https://api.github.com/repos/${REPO}/contents/${encodeURIComponent(PATH)}`, {
    method: "PUT",
    headers: gh,
    body: JSON.stringify({
      message: "Sortierer: Reihenfolge aktualisiert",
      content: textToB64(next),
      sha: cur.sha,
      branch: BRANCH,
    }),
  });
  if (!putRes.ok) {
    return json(502, { error: "Schreiben bei GitHub fehlgeschlagen.", status: putRes.status, detail: (await putRes.text()).slice(0, 300) });
  }
  const put = await putRes.json();
  return json(200, { ok: true, commit: put.commit && put.commit.sha });
});
