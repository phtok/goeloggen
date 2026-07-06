// =============================================================================
// ingest-uscreen · Supabase Edge Function
// Nimmt Uscreen-Webhooks (goetheanum.tv) entgegen und schreibt die Sommer-Aktion
// nach public.sommer2026_signups. Jeder Payload wird PII-redigiert in
// public.sommer2026_ingest_raw geloggt (nur Service-Role liest ihn).
//
// Aktions-Isolierung: jede Neuanmeldung im Aktionszeitraum → status 'neu' (jeder
// Trial hinterlegt eine Karte, darum ist transaction_id KEIN Unterscheidungsmerkmal).
// Verlängerungen legen nichts an. Zahlungen setzen (noch) KEIN 'bleibt' – die
// Umwandlung wird erst nach der 3-Monats-Frist bestimmt. Kündigung → 'gekuendigt'.
// Optional schärfer via aktion_coupon / aktion_plan.
//
// Attribution: volles UTM-Tupel (source/medium/campaign/content) + Landingpage-Pfad
// + offene Selbstauskunft (E-Mail-redigiert) werden je Anmeldung mitgeschrieben; der
// grobe kanal-Bucket bleibt als Zusammenfassung.
//
// Entdopplung: dedup_key = <produkt>:<gesalzener E-Mail-Hash> (Person je Produkt,
// auch über Quellen hinweg), Fallback <source>:<ext_id>. Upsert/Update laufen
// über dedup_key – dieselbe Person zählt nie doppelt, auch bei mehreren Events.
//
// Scharf nur wenn sommer2026_config.aktion_aktiv = 'true'. Auth: ?key=<secret>.
// =============================================================================
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SB = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { "Content-Type": "application/json", apikey: KEY, Authorization: `Bearer ${KEY}` };

function pick(o: any, keys: string[]): any {
  for (const k of keys) {
    const v = k.split(".").reduce((a: any, p: string) => (a == null ? a : a[p]), o);
    if (v !== undefined && v !== null && v !== "") return v;
  }
  return undefined;
}

function redact(o: any): any {
  if (Array.isArray(o)) return o.map(redact);
  if (o && typeof o === "object") {
    const r: any = {};
    for (const k of Object.keys(o)) r[k] = /(email|name|phone|address|\bip\b)/i.test(k) ? "***" : redact(o[k]);
    return r;
  }
  return o;
}

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// E-Mail-artige Werte aus Freitext entfernen (Selbstauskunft ist qualitativ, nicht personenbezogen).
function scrubEmail(s: string): string {
  return s.replace(/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi, "***");
}

// Platzhalter-Werte (Feld-Default «none», leer, «n/a» …) NICHT als UTM werten.
function cleanUtm(v: any): string | null {
  if (v == null) return null;
  const s = String(v).trim();
  return (s === "" || /^(none|n\/?a|null|undefined|-)$/i.test(s)) ? null : s;
}

// Volles UTM-Tupel + Landingpage: direkte Felder, sonst aus einer eingebetteten URL nachziehen.
function utmFrom(data: any): { src: any; med: any; camp: any; cont: any; land: any } {
  const g = (k: string) => pick(data, [k, "custom_fields." + k, "utm." + k.replace("utm_", ""), "query." + k]);
  let src = g("utm_source"), med = g("utm_medium"), camp = g("utm_campaign"), cont = g("utm_content");
  let land = pick(data, ["landing_path", "landing_page", "page"]);
  const urlish = pick(data, ["landing_url", "page_url", "signup_url", "url", "referrer_url", "referrer"]);
  if (urlish) {
    try {
      const url = new URL(String(urlish));
      const q = url.searchParams;
      src = src || q.get("utm_source"); med = med || q.get("utm_medium");
      camp = camp || q.get("utm_campaign"); cont = cont || q.get("utm_content");
      if (!land) land = url.pathname;
    } catch { /* keine URL */ }
  }
  return { src, med, camp, cont, land };
}

function mapPlan(title: string) {
  const t = (title || "").toLowerCase();
  const sprache = /\b(en|eng|english|englisch)\b/.test(t) ? "en" : "de";
  const intervall = /(year|annual|annum|jahr|jähr|yearly)/.test(t) ? "jaehrlich"
    : /(month|monat|mensile|mensuel)/.test(t) ? "monatlich" : "monatlich";
  const tarif = /(reduc|ermäss|ermaess|student|conc)/.test(t) ? "ermaessigt" : "standard";
  return { sprache, intervall, tarif };
}

const KANAELE = ["newsletter", "mailer", "social", "popup", "website", "empfehlung", "andere"];
function mapKanal(v: any): string {
  const s = (v ?? "").toString().toLowerCase();
  if (!s) return "andere";
  if (KANAELE.includes(s)) return s;
  if (/(news|\bnl\b)/.test(s)) return "newsletter";
  if (/(mail|post|brief)/.test(s)) return "mailer";
  if (/(insta|face|\bfb\b|social|linkedin|youtube|twitter|tiktok)/.test(s)) return "social";
  if (/(popup|pop-up|overlay)/.test(s)) return "popup";
  if (/(web|site|direct|organic)/.test(s)) return "website";
  if (/(refer|empfehl|friend)/.test(s)) return "empfehlung";
  return "andere";
}

async function log(event: string, ok: boolean, note: string, payload: unknown) {
  await fetch(`${SB}/rest/v1/sommer2026_ingest_raw`, {
    method: "POST",
    headers: { ...H, Prefer: "return=minimal" },
    body: JSON.stringify({ source: "uscreen", event, ok, note, payload: redact(payload) }),
  }).catch(() => {});
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

async function patchStatus(dedupKey: string, status: string) {
  await fetch(`${SB}/rest/v1/sommer2026_signups?dedup_key=eq.${encodeURIComponent(dedupKey)}`, {
    method: "PATCH",
    headers: { ...H, Prefer: "return=minimal" },
    body: JSON.stringify({ status }),
  }).catch(() => {});
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("ok", { status: 200 });

  const u = new URL(req.url);
  const key = u.searchParams.get("key") || req.headers.get("x-webhook-key") || "";
  const cfgRows = await fetch(`${SB}/rest/v1/sommer2026_config?key=in.(webhook_secret,hash_salt,aktion_aktiv,aktion_start,aktion_coupon,aktion_plan)&select=key,value`, { headers: H })
    .then((r) => r.json()).catch(() => []);
  const cfg: Record<string, string> = {};
  if (Array.isArray(cfgRows)) for (const r of cfgRows) cfg[r.key] = r.value;
  const secret = cfg["webhook_secret"] || null;
  if (!secret || key !== secret) return new Response("unauthorized", { status: 401 });

  const armed = (cfg["aktion_aktiv"] || "").toLowerCase() === "true";
  const salt = cfg["hash_salt"] || "";
  const aktionStart = cfg["aktion_start"] || "";
  const aktionCoupon = (cfg["aktion_coupon"] || "").toLowerCase();
  const aktionPlan = (cfg["aktion_plan"] || "").toLowerCase();

  let body: any = {};
  try { body = await req.json(); } catch { /* leer */ }

  const event = (pick(body, ["event", "type", "event_type"]) || "").toString();
  const data = body.data && typeof body.data === "object" ? body.data : body;
  await log(event, true, "empfangen", body);

  if (!armed) return json({ ok: true, mode: "log" });

  const ext = String(pick(data, ["user_id", "user.id", "subscription_id", "transaction_id", "id"]) ?? "");
  if (!ext) return json({ ok: true, skipped: "kein user_id" });

  // Entdopplung: Person je Produkt über gesalzenen E-Mail-Hash (Fallback ext_id).
  const email = (pick(data, ["customer_email", "user_email", "email"]) || "").toString().toLowerCase();
  const person = email ? await sha256Hex(salt + email) : "";
  const dedupKey = person ? `gtv:${person}` : `uscreen:${ext}`;

  const title = (pick(data, ["subscription_title", "plan_title", "plan_name", "subscription.title", "product_title", "offer_title", "title"]) || "").toString();
  const e = event.toLowerCase();
  const isNew = /(assign|subscribed|created|trial|start)/.test(e);
  const isPay = /(order_paid|paid|recurring|renew|charge|payment|convert)/.test(e);
  const isCancel = /(cancel|refund|expire|churn|delet)/.test(e);

  if (isCancel) { await patchStatus(dedupKey, "gekuendigt"); return json({ ok: true, status: "gekuendigt" }); }
  // Jeder Trial hinterlegt eine Karte → Zahlung fällt sofort an. Darum setzt eine
  // Zahlung (noch) KEIN 'bleibt': die echte Umwandlung wird erst nach der
  // 3-Monats-Frist bestimmt (separater Schritt im Oktober).
  if (isPay && !isNew) return json({ ok: true, note: "Zahlung ignoriert (Umwandlung erst nach 3 Monaten)" });

  if (!isNew) return json({ ok: true, skipped: "event ignoriert" });

  // Aktion = jede Neuanmeldung im Aktionszeitraum (aktion_start begrenzt es zeitlich).
  // Optional schärfer über aktion_coupon / aktion_plan.
  const coupon = (pick(data, ["coupon_code", "coupon", "discount_code", "code"]) || "").toString().toLowerCase();
  let istAktion: boolean;
  if (aktionCoupon) istAktion = coupon.includes(aktionCoupon);
  else if (aktionPlan) istAktion = title.toLowerCase().includes(aktionPlan);
  else istAktion = true;
  if (!istAktion) return json({ ok: true, skipped: "nicht Aktion (Coupon/Plan)" });

  const { sprache, intervall, tarif } = mapPlan(title);
  const utmRaw = utmFrom(data);
  const src = cleanUtm(utmRaw.src), med = cleanUtm(utmRaw.med), camp = cleanUtm(utmRaw.camp), cont = cleanUtm(utmRaw.cont), land = utmRaw.land;
  // Offene Selbstauskunft «Wie sind Sie aufmerksam geworden?» (Custom User Field) – O-Ton, E-Mail-redigiert.
  const selbst0 = pick(data, ["referral_source", "how_heard", "how_did_you_hear", "custom_fields.how_did_you_hear", "user_field_1", "user_fields.0.value"]);
  const selbst = selbst0 ? scrubEmail(String(selbst0)).slice(0, 300) : null;
  const kanal = mapKanal(src || pick(data, ["source", "referral_source"]) || selbst0);
  const when = pick(data, ["created_at", "subscribed_at", "started_at", "date"]) || new Date().toISOString();

  // Aktions-Grenze: Anmeldungen vor dem Start (Nachmittag 3. Juli) zählen nicht.
  if (aktionStart && !isNaN(Date.parse(when)) && new Date(when) < new Date(aktionStart)) {
    return json({ ok: true, skipped: "vor Aktionsstart" });
  }

  const row = {
    signed_up_at: when, produkt: "gtv", sprache, format: "stream",
    tarif, intervall, status: "neu", kanal, source: "uscreen", ext_id: ext, dedup_key: dedupKey,
    kampagne: (camp ? String(camp) : "summer26_trial"),
    utm_source: src ? String(src) : null, utm_medium: med ? String(med) : null,
    utm_campaign: camp ? String(camp) : null, utm_content: cont ? String(cont) : null,
    landing_path: land ? String(land).slice(0, 200) : null, selbstauskunft: selbst,
  };
  const res = await fetch(`${SB}/rest/v1/sommer2026_signups?on_conflict=dedup_key`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    await log(event, false, `upsert ${res.status} ${(await res.text()).slice(0, 300)}`, row);
    return json({ ok: false }, 200);
  }
  return json({ ok: true, status: "neu", sprache, tarif, intervall, kanal });
});
