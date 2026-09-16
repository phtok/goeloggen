// =============================================================================
// lead-fang · Supabase Edge Function (Grenzgänger-Fang-Strecke)
// Charta: docs/grenzgaenger/charta.md · Vorbild: services/seelenkalender/
// Vier Wege über ?aktion= :
//   anmelden    POST {email, griff, sprache?, milieu?, produkt?, utm?, website?}
//               → Double-Opt-in-Mail (nur für AKTIVE Griffe)
//   bestaetigen GET  ?t=<token>            → Status aktiv, Rücksprung zur Landing
//   ende        GET  ?t=<token>            → Status beendet (1 Klick, ohne Rückfrage)
//   wellen      GET/POST ?key=<versand_key> (pg_cron täglich)
//               → fällige Wellen: aktiv ∧ w1 null → w1 · w1+4d → w2 · w2+5d → w3
//
// Die Wellen-Mails sind die Versand-Artefakte der Mail-Fabrik
// (services/mailing-grenzgaenger/ → apps/grenzgaenger-mails/mails/ auf GitHub
// Pages); %UNSUBSCRIBELINK% wird je Lead durch den ende-Link ersetzt.
// Grundsätze: kein Nutzer-Enumerieren (Antwort immer gleich), Honeypot-Feld
// «website», Zweckbindung (E-Mail nur für den Versand), höchstens drei Wellen,
// Ein-Klick-Abmeldung, List-Unsubscribe-Header.
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };
const FUNKTION_URL = `${SB}/functions/v1/lead-fang`;

const EMAIL_RE = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
const GRIFF_RE = /^g[0-9]{3}$/;

type Griff = {
  id: string; titel: string; zielkreis: string; landing_url: string; aktiv: boolean;
  bestaetigung_betreff: Record<string, string>;
  bestaetigung_text: Record<string, string>;
  wellen_betreff: Record<string, Record<string, string>>;
};

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function tokenNeu(): string {
  const b = new Uint8Array(24); crypto.getRandomValues(b);
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function config(): Promise<Record<string, string>> {
  const r = await fetch(`${SB}/rest/v1/marketing_config?select=key,value`, { headers: H });
  const rows = await r.json();
  const c: Record<string, string> = {};
  for (const row of rows) c[row.key] = row.value;
  return c;
}

async function griffLaden(id: string): Promise<Griff | null> {
  if (!GRIFF_RE.test(id)) return null;
  const r = await fetch(`${SB}/rest/v1/marketing_griffe?id=eq.${id}&select=*`, { headers: H });
  const rows = r.ok ? await r.json() : [];
  return rows[0] ?? null;
}

// --- Mail-Bausteine (Bestätigungs-Brief: schlicht, textnah) -------------------
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function mailHtml(lang: string, inhalt: string, fussHtml: string): string {
  return `<!doctype html><html lang="${lang}"><body style="margin:0;padding:0;background:#faf8f4">
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
  const griff = await griffLaden(String(body.griff ?? ""));
  if (!griff || !griff.aktiv) return ok; // unbekannt/inaktiv: gleiche Antwort
  const sprache = body.sprache === "en" ? "en" : "de";
  const produkt = ["wos", "gtv", "beide"].includes(String(body.produkt)) ? String(body.produkt) : "beide";
  const milieu = typeof body.milieu === "string" ? body.milieu.slice(0, 80) : null;
  const hash = await sha256Hex(cfg.hash_salt + email);
  const token = tokenNeu();
  const herkunft = (body.utm && typeof body.utm === "object") ? body.utm : null;

  // Upsert über (email_hash, griff_id); Wiederanmeldung nach Abmeldung erlaubt.
  const up = await fetch(`${SB}/rest/v1/marketing_leads?on_conflict=email_hash,griff_id`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=representation" },
    body: JSON.stringify([{
      email, email_hash: hash, griff_id: griff.id, sprache, milieu, produkt,
      status: "angemeldet", token, herkunft, beendet_am: null,
    }]),
  });
  if (!up.ok) { console.error("upsert", up.status, await up.text()); return ok; }
  const row = (await up.json())[0];
  if (row?.status === "aktiv") return ok; // schon dabei — keine zweite Mail

  const bestaetigen = `${FUNKTION_URL}?aktion=bestaetigen&t=${row?.token ?? token}`;
  const knopf = sprache === "en" ? "Confirm sign-up" : "Anmeldung bestätigen";
  const schluss = sprache === "en"
    ? "Not your request? Then simply ignore this message — nothing further happens."
    : "Kein Wunsch von Ihnen? Dann lassen Sie diese Nachricht einfach unbeantwortet — es geschieht nichts weiter.";
  const fuss = sprache === "en"
    ? `You are receiving this message because this address was entered on ${esc(griff.landing_url)}.`
    : `Sie erhalten diese Nachricht, weil diese Adresse auf ${esc(griff.landing_url)} eingetragen wurde.`;
  const inhalt = `
    <p style="color:#8a6728;font-size:14px;letter-spacing:.04em;margin:0 0 8px">${esc(griff.titel)} – Das Goetheanum</p>
    <p style="font-size:20px;margin:0 0 16px"><strong>${sprache === "en" ? "One more step." : "Nur noch ein Schritt."}</strong></p>
    <p>${esc(griff.bestaetigung_text[sprache] ?? griff.bestaetigung_text.de)}</p>
    <p style="margin:24px 0"><a href="${bestaetigen}" style="background:#0061a9;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;display:inline-block">${knopf}</a></p>
    <p>${schluss}</p>`;
  const fehler = await resendBatch(cfg, [{
    from: cfg.absender, to: [email],
    subject: griff.bestaetigung_betreff[sprache] ?? griff.bestaetigung_betreff.de,
    html: mailHtml(sprache, inhalt, fuss),
  }]);
  if (fehler) console.error("bestaetigungs-mail fehlgeschlagen", griff.id);
  return ok;
}

async function statusPerToken(t: string, neu: "aktiv" | "beendet"): Promise<Response> {
  const fallback = "https://werkzeuge.goetheanum.ch/";
  if (!/^[0-9a-f]{48}$/.test(t)) return Response.redirect(fallback + "#fehler", 303);
  const patch: Record<string, unknown> = { status: neu };
  if (neu === "aktiv") patch.bestaetigt_am = new Date().toISOString();
  else patch.beendet_am = new Date().toISOString();
  const r = await fetch(`${SB}/rest/v1/marketing_leads?token=eq.${t}`, {
    method: "PATCH", headers: { ...H, Prefer: "return=representation" }, body: JSON.stringify(patch),
  });
  const rows = r.ok ? await r.json() : [];
  if (!rows.length) return Response.redirect(fallback + "#fehler", 303);
  const griff = await griffLaden(rows[0].griff_id);
  const ziel = griff?.landing_url || fallback;
  return Response.redirect(ziel + (neu === "aktiv" ? "#bestaetigt" : "#beendet"), 303);
}

async function wellen(url: URL, cfg: Record<string, string>): Promise<Response> {
  if (!cfg.versand_key || url.searchParams.get("key") !== cfg.versand_key) {
    return new Response("nein", { status: 403 });
  }
  if (!cfg.resend_api_key) return new Response(JSON.stringify({ ok: false, grund: "resend_api_key fehlt" }), { status: 200 });

  const gr = await fetch(`${SB}/rest/v1/marketing_griffe?aktiv=eq.true&select=*`, { headers: H });
  const griffe: Griff[] = await gr.json();
  const w2Tage = Number(cfg.w2_nach_tagen || "4");
  const w3Tage = Number(cfg.w3_nach_tagen || "5");
  const vor = (tage: number) => new Date(Date.now() - tage * 24 * 3600 * 1000).toISOString();
  const bericht: Record<string, unknown>[] = [];
  const htmlCache: Record<string, string | null> = {};

  async function mailVorlage(zielkreis: string, welle: number, sprache: string): Promise<string | null> {
    const name = `mail_${zielkreis}_w${welle}_${sprache}.html`;
    if (name in htmlCache) return htmlCache[name];
    const r = await fetch(`${cfg.mails_base_url}/${name}`);
    htmlCache[name] = r.ok ? await r.text() : null;
    if (!r.ok) console.error("vorlage fehlt", name, r.status);
    return htmlCache[name];
  }

  for (const griff of griffe) {
    // Fällige Wellen: aktiv ∧ w1 null → w1 · w1 älter als 4 Tage → w2 · w2 älter als 5 Tage → w3
    const faellig: Record<number, string> = {
      1: `status=eq.aktiv&w1_am=is.null`,
      2: `status=eq.aktiv&w1_am=lt.${vor(w2Tage)}&w2_am=is.null`,
      3: `status=eq.aktiv&w2_am=lt.${vor(w3Tage)}&w3_am=is.null`,
    };
    for (const welle of [1, 2, 3]) {
      const lr = await fetch(
        `${SB}/rest/v1/marketing_leads?griff_id=eq.${griff.id}&${faellig[welle]}&select=id,email,token,sprache`,
        { headers: H },
      );
      const leads: { id: number; email: string; token: string; sprache: string }[] = await lr.json();
      if (!leads.length) continue;

      // Stempeln VOR dem Senden — doppeltes Feuern des Crons sendet nie doppelt.
      const ids = leads.map((l) => l.id).join(",");
      const st = await fetch(`${SB}/rest/v1/marketing_leads?id=in.(${ids})`, {
        method: "PATCH", headers: H,
        body: JSON.stringify({ [`w${welle}_am`]: new Date().toISOString() }),
      });
      if (!st.ok) { console.error("stempeln", griff.id, welle, await st.text()); continue; }

      const mails: unknown[] = [];
      let ohneVorlage = 0;
      for (const lead of leads) {
        const vorlage = await mailVorlage(griff.zielkreis, welle, lead.sprache);
        if (!vorlage) { ohneVorlage++; continue; }
        const ende = `${FUNKTION_URL}?aktion=ende&t=${lead.token}`;
        mails.push({
          from: cfg.absender, to: [lead.email],
          subject: griff.wellen_betreff?.[`w${welle}`]?.[lead.sprache]
            ?? griff.wellen_betreff?.[`w${welle}`]?.de ?? griff.titel,
          html: vorlage.replaceAll("%UNSUBSCRIBELINK%", ende),
          headers: { "List-Unsubscribe": `<${ende}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
        });
      }
      const fehler = (mails.length ? await resendBatch(cfg, mails) : 0) + ohneVorlage;
      await fetch(`${SB}/rest/v1/marketing_versand`, {
        method: "POST", headers: H,
        body: JSON.stringify([{ griff_id: griff.id, welle, empfaenger: leads.length - fehler, fehler }]),
      });
      bericht.push({ griff: griff.id, welle, empfaenger: leads.length, fehler });
    }
  }
  return new Response(JSON.stringify({ ok: true, laeufe: bericht }), { status: 200 });
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
    if (aktion === "bestaetigen") return await statusPerToken(url.searchParams.get("t") ?? "", "aktiv");
    if (aktion === "ende") return await statusPerToken(url.searchParams.get("t") ?? "", "beendet");
    if (aktion === "wellen") return await wellen(url, cfg);
  } catch (e) {
    console.error("lead-fang", aktion, e);
    return new Response("fehler", { status: 500 });
  }
  return new Response("unbekannte aktion", { status: 404 });
});
