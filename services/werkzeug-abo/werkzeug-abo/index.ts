// =============================================================================
// werkzeug-abo · Supabase Edge Function
// Das Update-Abo der Werkzeuge: wer mag, wählt die persönlich relevanten
// Werkzeuge und bekommt eine Mail, wenn dort etwas neu ist oder besser
// funktioniert (z. B. eine neue Schrift-Fassung, die eine Neuinstallation
// lohnt). Leere Auswahl = alle Werkzeuge.
//
// Vier Wege über ?aktion= :
//   anmelden    POST {email, auswahl?: string[], website?}  → Double-Opt-in-Mail
//               (Wieder-Anmelden mit neuer Auswahl aktualisiert nur die Auswahl,
//                ohne zweite Mail — Antwort immer gleich, kein Enumerieren.)
//   bestaetigen GET  ?t=<token>                             → Status aktiv
//   ende        GET  ?t=<token>                             → Status beendet (1 Klick)
//   versand     POST ?key=<versand_key>
//               {betreff, inhalt_html, werkzeuge?: string[]|"alle", test?: email}
//               → an alle Aktiven, deren Auswahl die Werkzeuge berührt
//                 (leere Auswahl = alles abonniert); test = nur an diese Adresse.
//
// Versand über Resend (API-Key in werkzeugabo_config, nie im Repo).
// Grundsätze wie beim Seelenkalender: Honeypot «website», Zweckbindung,
// Ein-Klick-Abmeldung, List-Unsubscribe-Header, kein Nutzer-Enumerieren.
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };
const FUNKTION_URL = `${SB}/functions/v1/werkzeug-abo`;

const EMAIL_RE = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
const SLUG_RE = /^[a-z0-9-]{1,50}$/;

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function tokenNeu(): string {
  const b = new Uint8Array(24); crypto.getRandomValues(b);
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function config(): Promise<Record<string, string>> {
  const r = await fetch(`${SB}/rest/v1/werkzeugabo_config?select=key,value`, { headers: H });
  const rows = await r.json();
  const c: Record<string, string> = {};
  for (const row of rows) c[row.key] = row.value;
  return c;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function mailHtml(inhalt: string, fussHtml: string): string {
  return `<!doctype html><html lang="de"><body style="margin:0;padding:0;background:#faf8f4">
  <div style="max-width:560px;margin:0 auto;padding:32px 20px;font-family:Georgia,'Times New Roman',serif;color:#23272b;font-size:17px;line-height:1.65">
  ${inhalt}
  <hr style="border:none;border-top:1px solid #d9d4c9;margin:32px 0 16px">
  <p style="font-size:13px;color:#6b7177;line-height:1.6">${fussHtml}</p>
  </div></body></html>`;
}

async function resendBatch(cfg: Record<string, string>, mails: unknown[]): Promise<number> {
  let fehler = 0;
  for (let i = 0; i < mails.length; i += 100) {
    const teil = mails.slice(i, i + 100);
    const r = await fetch("https://api.resend.com/emails/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${cfg.resend_api_key}` },
      body: JSON.stringify(teil),
    });
    if (!r.ok) { fehler += teil.length; console.error("resend", r.status, await r.text()); }
    if (i + 100 < mails.length) await new Promise((res) => setTimeout(res, 600));
  }
  return fehler;
}

// --- Aktionen ----------------------------------------------------------------
async function anmelden(req: Request, cfg: Record<string, string>): Promise<Response> {
  const ok = new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { return ok; }
  const email = String(body.email ?? "").trim().toLowerCase();
  const honeypot = String(body.website ?? "");
  if (honeypot !== "" || !EMAIL_RE.test(email) || email.length > 200) return ok; // still, kein Enumerieren
  const roh = Array.isArray(body.auswahl) ? body.auswahl : [];
  const auswahl = roh.filter((s) => typeof s === "string" && SLUG_RE.test(s)).slice(0, 100);
  const hash = await sha256Hex(cfg.hash_salt + email);

  const vr = await fetch(`${SB}/rest/v1/werkzeugabo_abo?email_hash=eq.${hash}&select=status,token`, { headers: H });
  const rows: { status: string; token: string }[] = vr.ok ? await vr.json() : [];

  if (rows[0]?.status === "aktiv") {
    // schon dabei — nur die Auswahl übernehmen, keine zweite Mail
    await fetch(`${SB}/rest/v1/werkzeugabo_abo?email_hash=eq.${hash}`, {
      method: "PATCH", headers: H, body: JSON.stringify({ auswahl }),
    });
    return ok;
  }

  const token = tokenNeu();
  if (rows.length) {
    await fetch(`${SB}/rest/v1/werkzeugabo_abo?email_hash=eq.${hash}`, {
      method: "PATCH", headers: H,
      body: JSON.stringify({ auswahl, status: "angemeldet", token, beendet_am: null }),
    });
  } else {
    const ins = await fetch(`${SB}/rest/v1/werkzeugabo_abo`, {
      method: "POST", headers: H,
      body: JSON.stringify([{ email, email_hash: hash, auswahl, status: "angemeldet", token }]),
    });
    if (!ins.ok) { console.error("insert", ins.status, await ins.text()); return ok; }
  }

  const bestaetigen = `${FUNKTION_URL}?aktion=bestaetigen&t=${token}`;
  const anzahl = auswahl.length;
  const was = anzahl === 0 ? "alle Werkzeuge" : (anzahl === 1 ? "ein ausgewähltes Werkzeug" : `${anzahl} ausgewählte Werkzeuge`);
  const inhalt = `
    <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">Werkzeuge – Das Goetheanum</p>
    <p style="font-size:20px;margin:0 0 16px"><strong>Nur noch ein Schritt.</strong></p>
    <p>Damit dich Neuerungen der Goetheanum-Werkzeuge erreichen (${was}), bestätige bitte deine Anmeldung:</p>
    <p style="margin:24px 0"><a href="${bestaetigen}" style="background:#0061a9;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;display:inline-block">Anmeldung bestätigen</a></p>
    <p>Kein Wunsch von dir? Dann lass diese Nachricht einfach unbeantwortet — es geschieht nichts weiter.</p>`;
  const fuss = `Du erhältst diese Nachricht, weil diese Adresse auf werkzeuge.goetheanum.ch/abo eingetragen wurde.`;
  const fehler = await resendBatch(cfg, [{
    from: cfg.absender, to: [email],
    subject: "Bitte bestätigen: das Werkzeug-Abo",
    html: mailHtml(inhalt, fuss),
  }]);
  if (fehler) console.error("bestaetigungs-mail fehlgeschlagen");
  return ok;
}

async function statusPerToken(t: string, neu: "aktiv" | "beendet", cfg: Record<string, string>): Promise<Response> {
  const ziel = cfg.seite_url || "https://werkzeuge.goetheanum.ch/abo.html";
  if (!/^[0-9a-f]{48}$/.test(t)) return Response.redirect(ziel + "#fehler", 303);
  const patch: Record<string, unknown> = { status: neu };
  if (neu === "aktiv") patch.bestaetigt_am = new Date().toISOString();
  else patch.beendet_am = new Date().toISOString();
  const r = await fetch(`${SB}/rest/v1/werkzeugabo_abo?token=eq.${t}`, {
    method: "PATCH", headers: { ...H, Prefer: "return=representation" }, body: JSON.stringify(patch),
  });
  const rows = r.ok ? await r.json() : [];
  const anker = rows.length ? (neu === "aktiv" ? "#bestaetigt" : "#beendet") : "#fehler";
  return Response.redirect(ziel + anker, 303);
}

async function versand(req: Request, url: URL, cfg: Record<string, string>): Promise<Response> {
  if (!cfg.versand_key || url.searchParams.get("key") !== cfg.versand_key) {
    return new Response("nein", { status: 403 });
  }
  if (!cfg.resend_api_key) return new Response(JSON.stringify({ ok: false, grund: "resend_api_key fehlt" }), { status: 200 });

  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { /* leer */ }
  const betreff = String(body.betreff ?? "").trim();
  const inhaltHtml = String(body.inhalt_html ?? "").trim();
  if (!betreff || !inhaltHtml) {
    return new Response(JSON.stringify({ ok: false, grund: "betreff und inhalt_html noetig" }), { status: 200 });
  }
  const roh = Array.isArray(body.werkzeuge) ? body.werkzeuge : "alle";
  const werkzeuge = roh === "alle" ? "alle" : (roh as unknown[]).filter((s) => typeof s === "string" && SLUG_RE.test(s as string)) as string[];
  const test = typeof body.test === "string" && EMAIL_RE.test(body.test) ? body.test : null;

  const ar = await fetch(`${SB}/rest/v1/werkzeugabo_abo?status=eq.aktiv&select=email,token,auswahl`, { headers: H });
  const alle: { email: string; token: string; auswahl: string[] }[] = await ar.json();
  const passt = (a: { auswahl: string[] }) =>
    werkzeuge === "alle" || !Array.isArray(a.auswahl) || a.auswahl.length === 0 ||
    (werkzeuge as string[]).some((w) => a.auswahl.includes(w));
  const abos = test ? [{ email: test, token: "test".padEnd(48, "0"), auswahl: [] }] : alle.filter(passt);

  const mails = abos.map((a) => {
    const ende = `${FUNKTION_URL}?aktion=ende&t=${a.token}`;
    const seite = cfg.seite_url || "https://werkzeuge.goetheanum.ch/abo.html";
    const inhalt = `
      <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">Werkzeuge – Das Goetheanum</p>
      ${inhaltHtml}`;
    const fuss = `Neuerungen der Goetheanum-Werkzeuge, nach deiner Auswahl.
      <a href="${seite}" style="color:#6b7177">Auswahl ändern</a> ·
      <a href="${ende}" style="color:#6b7177">Abmelden mit einem Klick</a> — ohne Rückfrage, ohne Umweg.`;
    return {
      from: cfg.absender, to: [a.email],
      subject: betreff,
      html: mailHtml(inhalt, fuss),
      headers: { "List-Unsubscribe": `<${ende}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
    };
  });

  const fehler = abos.length ? await resendBatch(cfg, mails) : 0;
  if (!test) {
    await fetch(`${SB}/rest/v1/werkzeugabo_versand`, {
      method: "POST", headers: H,
      body: JSON.stringify([{ betreff, werkzeuge: werkzeuge === "alle" ? [] : werkzeuge, empfaenger: abos.length - fehler, fehler }]),
    });
  }
  return new Response(JSON.stringify({ ok: true, test: !!test, empfaenger: abos.length, fehler }), { status: 200 });
}

// --- Router --------------------------------------------------------------------
Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  const aktion = url.searchParams.get("aktion") ?? "";
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type" } });
  }
  const cfg = await config();
  try {
    if (aktion === "anmelden" && req.method === "POST") return await anmelden(req, cfg);
    if (aktion === "bestaetigen") return await statusPerToken(url.searchParams.get("t") ?? "", "aktiv", cfg);
    if (aktion === "ende") return await statusPerToken(url.searchParams.get("t") ?? "", "beendet", cfg);
    if (aktion === "versand" && req.method === "POST") return await versand(req, url, cfg);
  } catch (e) {
    console.error("werkzeug-abo", aktion, e);
    return new Response("fehler", { status: 500 });
  }
  return new Response("unbekannte aktion", { status: 404 });
});
