// =============================================================================
// ingest-uscreen · Supabase Edge Function
// Nimmt Uscreen-Webhooks (goetheanum.tv) entgegen und schreibt sie in
// public.sommer2026_signups. Loggt jeden Payload PII-redigiert in
// public.sommer2026_ingest_raw (nur Service-Role liest ihn) – so lässt sich das
// Mapping am ersten echten Event verfeinern.
//
// Auth: ?key=<webhook_secret> (liegt in public.sommer2026_config). Kein JWT.
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

// PII (E-Mail, Name, Telefon, Adresse, IP) vor dem Loggen entfernen.
function redact(o: any): any {
  if (Array.isArray(o)) return o.map(redact);
  if (o && typeof o === "object") {
    const r: any = {};
    for (const k of Object.keys(o)) r[k] = /(email|name|phone|address|\bip\b)/i.test(k) ? "***" : redact(o[k]);
    return r;
  }
  return o;
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

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("ok", { status: 200 });

  // Secret prüfen (Query ?key= oder Header x-webhook-key)
  const u = new URL(req.url);
  const key = u.searchParams.get("key") || req.headers.get("x-webhook-key") || "";
  const cfgRows = await fetch(`${SB}/rest/v1/sommer2026_config?key=in.(webhook_secret,aktion_coupon,aktion_plan)&select=key,value`, { headers: H })
    .then((r) => r.json()).catch(() => []);
  const cfg: Record<string, string> = {};
  if (Array.isArray(cfgRows)) for (const r of cfgRows) cfg[r.key] = r.value;
  const secret = cfg["webhook_secret"] || null;
  if (!secret || key !== secret) return new Response("unauthorized", { status: 401 });
  // Aktions-Filter: nur zählen, was zur Sommer-Aktion gehört. Solange weder
  // aktion_coupon noch aktion_plan gesetzt ist, läuft die Function im Log-Modus.
  const aktionCoupon = (cfg["aktion_coupon"] || "").toLowerCase();
  const aktionPlan = (cfg["aktion_plan"] || "").toLowerCase();
  const filterConfigured = !!(aktionCoupon || aktionPlan);

  let body: any = {};
  try { body = await req.json(); } catch { /* leerer Body */ }

  const event = (pick(body, ["event", "type", "event_type"]) || "").toString();
  const data = body.data && typeof body.data === "object" ? body.data : body;
  await log(event, true, "empfangen", body);

  const ext = pick(data, ["subscription_id", "subscription.id", "transaction_id", "id", "user_id", "user.id"]);
  if (ext === undefined) {
    return new Response(JSON.stringify({ ok: true, skipped: "kein subscription_id" }),
      { status: 200, headers: { "Content-Type": "application/json" } });
  }

  const title = (pick(data, ["subscription_title", "plan_title", "plan_name", "subscription.title", "product_title"]) || "").toString();

  // Log-Modus: ohne Aktions-Filter wird geloggt, aber nichts gezählt.
  if (!filterConfigured) {
    return new Response(JSON.stringify({ ok: true, mode: "log" }),
      { status: 200, headers: { "Content-Type": "application/json" } });
  }
  const coupon = (pick(data, ["coupon_code", "coupon", "discount_code", "code"]) || "").toString().toLowerCase();
  const matchesAktion = (aktionCoupon && coupon.includes(aktionCoupon)) || (aktionPlan && title.toLowerCase().includes(aktionPlan));
  if (!matchesAktion) {
    return new Response(JSON.stringify({ ok: true, skipped: "nicht Aktion" }),
      { status: 200, headers: { "Content-Type": "application/json" } });
  }

  const { sprache, intervall, tarif } = mapPlan(title);
  const kanal = mapKanal(pick(data, ["utm_source", "source", "custom_fields.utm_source", "referral_source", "user_fields.0.value", "user_field_1"]));
  const when = pick(data, ["created_at", "subscribed_at", "started_at", "date"]) || new Date().toISOString();

  const e = event.toLowerCase();
  let status = "neu";
  if (/(cancel|refund|expire|churn|delet)/.test(e)) status = "gekuendigt";       // verlässt vor/bei Umwandlung
  else if (/(renew|payment|charge|paid|convert)/.test(e)) status = "bleibt";     // erste Abbuchung = umgewandelt

  const row = {
    signed_up_at: when, produkt: "gtv", sprache, format: "stream",
    tarif, intervall, status, kanal, source: "uscreen", ext_id: String(ext),
  };

  const res = await fetch(`${SB}/rest/v1/sommer2026_signups?on_conflict=source,ext_id`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    await log(event, false, `upsert ${res.status} ${(await res.text()).slice(0, 300)}`, row);
    return new Response(JSON.stringify({ ok: false }), { status: 200, headers: { "Content-Type": "application/json" } });
  }
  return new Response(JSON.stringify({ ok: true, status, sprache, tarif, intervall, kanal }),
    { status: 200, headers: { "Content-Type": "application/json" } });
});
