const app = document.getElementById("memberApp");
const pageSlug = document.body.dataset.memberSlug || new URLSearchParams(window.location.search).get("slug") || "";

init();

async function init() {
  const [people, questions, events, initiatives] = await Promise.all([
    fetchPeople(),
    fetchQuestions(),
    fetchEvents(),
    fetchInitiatives()
  ]);

  if (!people.length) {
    app.innerHTML = `<section class="card"><h2>Keine Mitgliedsdaten</h2></section>`;
    return;
  }

  const member = people.find((p) => (p.slug || slugify(p.name || "")) === pageSlug) || people[0];
  const memberName = member.name || "";

  const relatedQuestions = questions.filter((q) =>
    (q.authors || []).some((author) => normalize(author) === normalize(memberName))
  );

  const relatedEvents = events.filter((event) =>
    (event.hosts || []).some((host) => normalize(host) === normalize(memberName))
  );

  const relatedInitiatives = initiatives.filter((initiative) =>
    (initiative.hosts || []).some((host) => normalize(host) === normalize(memberName))
  );

  const portrait = member.portraitUrl
    ? `<img class="member-avatar-large" src="${escapeHtml(member.portraitUrl)}" alt="${escapeHtml(memberName)}" />`
    : `<div class="member-avatar-large member-avatar-fallback">${escapeHtml(initials(memberName))}</div>`;
  const links = normalizeLinks(member.links);
  const linksBlock = links.length
    ? `<p class="muted">${links
        .map((link) => {
          const href = toProfileHref(link);
          return `<a class="member-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(link)}</a>`;
        })
        .join(" · ")}</p>`
    : "";

  app.innerHTML = `
    <section class="card">
      <div class="member-header">
        ${portrait}
        <div>
          <h2>${escapeHtml(memberName)}</h2>
          <p class="muted">${escapeHtml(member.role || "")}</p>
          ${linksBlock}
        </div>
      </div>
      <p>${escapeHtml(member.bio || "")}</p>
    </section>

    ${relatedQuestions.length
      ? `<section class="card"><h2>Fragen von ${escapeHtml(memberName)}</h2><div class="list">${relatedQuestions
          .map(renderQuestion)
          .join("")}</div></section>`
      : ""}

    ${relatedInitiatives.length
      ? `<section class="card"><h2>Initiativen mit ${escapeHtml(memberName)}</h2><div class="list">${relatedInitiatives
          .map(renderInitiative)
          .join("")}</div></section>`
      : ""}

    ${relatedEvents.length
      ? `<section class="card"><h2>Veranstaltungen mit ${escapeHtml(memberName)}</h2><div class="list">${relatedEvents
          .map(renderEvent)
          .join("")}</div></section>`
      : ""}
  `;
}

function renderQuestion(q) {
  const date = q.createdAt ? new Date(q.createdAt).toLocaleDateString("de-DE") : "";
  const location = q.location ? ` · ${escapeHtml(q.location)}` : "";
  return `<article class="card"><h3>${escapeHtml(q.text || "")}</h3><p class="muted">${escapeHtml(date)}${location}</p></article>`;
}

function renderInitiative(initiative) {
  const detailHref = initiative.id ? `/initiatives/${escapeHtml(initiative.id)}.html` : "/initiatives.html";
  const link = initiative.sourceUrl
    ? `<p><a class="member-link" href="${escapeHtml(initiative.sourceUrl)}" target="_blank" rel="noopener noreferrer">Quelle</a></p>`
    : "";
  const image = initiative.imageUrl
    ? `<img class="initiative-thumb" src="${escapeHtml(initiative.imageUrl)}" alt="${escapeHtml(initiative.title || "")}" loading="lazy" />`
    : "";
  return `<article class="card">${image}<h3><a class="member-link" href="${detailHref}">${escapeHtml(initiative.title || "")}</a></h3><p class="muted">${escapeHtml(initiative.description || "")}</p><p><a class="member-link" href="${detailHref}">Mehr</a></p>${link}</article>`;
}

function renderEvent(event) {
  const date = event.date ? new Date(event.date).toLocaleDateString("de-DE") : "";
  const location = event.location ? ` - ${escapeHtml(event.location)}` : "";
  const image = event.imageUrl
    ? `<img class="calendar-image" src="${escapeHtml(event.imageUrl)}" alt="${escapeHtml(event.title || "")}" loading="lazy" />`
    : "";
  return `<article class="card"><h3>${escapeHtml(event.title || "")}</h3><p class="muted">${escapeHtml(date)}${location}</p>${image}<p>${escapeHtml(event.description || "")}</p></article>`;
}

async function fetchPeople() {
  try {
    const res = await fetch("/data/people.json");
    if (!res.ok) throw new Error("people");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    return [];
  }
}

async function fetchQuestions() {
  try {
    const res = await fetch("/api/questions");
    if (!res.ok) throw new Error("questions api");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("/data/questions.json");
      if (!fallback.ok) throw new Error("questions file");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

async function fetchEvents() {
  try {
    const res = await fetch("/api/events");
    if (!res.ok) throw new Error("events api");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("/data/events.json");
      if (!fallback.ok) throw new Error("events file");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

async function fetchInitiatives() {
  try {
    const res = await fetch("/api/initiatives");
    if (!res.ok) throw new Error("initiatives api");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("/data/initiatives.json");
      if (!fallback.ok) throw new Error("initiatives file");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

function normalize(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function normalizeLinks(input) {
  if (Array.isArray(input)) return input.map((v) => String(v).trim()).filter(Boolean);
  if (typeof input === "string") {
    return input
      .split(/\r?\n|,/)
      .map((v) => v.trim())
      .filter(Boolean);
  }
  return [];
}

function toProfileHref(value) {
  const raw = String(value || "").trim();
  if (!raw) return "#";
  if (/^https?:\/\//i.test(raw) || /^mailto:/i.test(raw)) return raw;
  return `https://${raw}`;
}

function slugify(value) {
  return normalize(value).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function initials(name) {
  return String(name)
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function escapeHtml(str) {
  return toGuillemets(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function toGuillemets(value) {
  let text = String(value || "");
  text = text.replace(/[„“«]/g, "‹").replace(/[”»]/g, "›");
  text = text.replace(/"([^"\n]+)"/g, "‹$1›");
  text = text.replace(/‚/g, "‹").replace(/[‘’]/g, "›");
  return text;
}
