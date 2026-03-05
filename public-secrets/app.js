const STORAGE_KEY = "public-secrets-interactions-v2";
const LEGACY_STORAGE_KEY = "public-secrets-interactions-v1";
const FIRST_QUESTION_KEY = "public-secrets-last-first-question-v1";

const DEFAULT_QUESTIONS = [
  {
    id: "q-001",
    text: "Wer möchte sprechen?",
    authors: ["Philipp Tok"],
    createdAt: "2026-03-01T10:00:00Z"
  }
];

let state = {
  questions: [],
  events: [],
  initiatives: [],
  people: [],
  comments: [],
  interactions: loadInteractionsState(),
  questionOrder: [],
  currentIndex: 0,
  currentRating: 0,
  view: "question",
  questionStep: "intro",
  questionListSort: "popular",
  questionsControlsOpen: false,
  menuEnabled: false,
  activeAuthor: "",
  shuffledPeople: [],
  expandedQuestionDetails: {},
  expandedQuestionComments: {},
  expandedQuestionCompose: {}
};

const app = document.getElementById("app");
const mainHeader = document.getElementById("mainHeader");
const siteFooter = document.getElementById("siteFooter");

document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-view]");
  if (nav) {
    state.view = nav.dataset.view;
    if (state.view !== "author") state.activeAuthor = "";
    render();
    return;
  }

  const actionEl = event.target.closest("[data-action]");
  if (!actionEl) return;

  if (state.view === "question") {
    handleQuestionAction(actionEl.dataset.action, actionEl.dataset.rating, actionEl.dataset.id);
    return;
  }

  if (state.view === "questions" || state.view === "author") {
    if (actionEl.dataset.action === "sort-questions") {
      if (state.view !== "questions") return;
      state.questionListSort = actionEl.dataset.sort || "popular";
      renderQuestionsView();
      return;
    }
    if (actionEl.dataset.action === "toggle-list-controls") {
      state.questionsControlsOpen = !state.questionsControlsOpen;
      renderQuestionsView();
      return;
    }
    if (actionEl.dataset.action === "filter-author") {
      const author = String(actionEl.dataset.author || "").trim();
      if (!author) return;
      state.activeAuthor = author;
      state.view = "author";
      renderAuthorView();
      return;
    }
    if (actionEl.dataset.action === "clear-author-filter") {
      state.activeAuthor = "";
      state.view = "questions";
      renderQuestionsView();
      return;
    }
    if (actionEl.dataset.action === "toggle-question-detail") {
      const id = String(actionEl.dataset.id || "");
      if (!id) return;
      state.expandedQuestionDetails[id] = !state.expandedQuestionDetails[id];
      render();
      return;
    }
    if (actionEl.dataset.action === "toggle-comments") {
      const id = String(actionEl.dataset.id || "");
      if (!id) return;
      state.expandedQuestionComments[id] = !state.expandedQuestionComments[id];
      render();
      return;
    }
    if (actionEl.dataset.action === "toggle-list-heart") {
      const id = String(actionEl.dataset.id || "");
      if (!id) return;
      const interaction = getInteraction(id);
      const nextRating = Number(interaction.rating || 0) > 0 ? 0 : 1;
      saveInteraction(id, nextRating, interaction.comment || "", interaction.name || "");
      render();
      return;
    }
    if (actionEl.dataset.action === "toggle-comment-compose") {
      const id = String(actionEl.dataset.id || "");
      if (!id) return;
      state.expandedQuestionCompose[id] = !state.expandedQuestionCompose[id];
      render();
      return;
    }
    if (actionEl.dataset.action === "save-list-comment") {
      const id = String(actionEl.dataset.id || "");
      if (!id) return;
      const textInput = app.querySelector(`textarea[data-comment-text-for="${escapeHtml(id)}"]`);
      const nameInput = app.querySelector(`input[data-comment-name-for="${escapeHtml(id)}"]`);
      const comment = textInput ? textInput.value.trim() : "";
      const name = nameInput ? nameInput.value.trim() : "";
      const interaction = getInteraction(id);
      saveInteraction(id, Number(interaction.rating || 0), comment, name);
      render();
      return;
    }
    if (actionEl.dataset.action === "submit-reply") {
      handleQuestionAction("submit-reply", "", actionEl.dataset.id);
      return;
    }
  }
});

init();

async function init() {
  const initialView = getInitialViewFromUrl();
  if (initialView) {
    state.view = initialView;
    if (initialView !== "question") state.menuEnabled = true;
  }

  try {
    state.questions = await fetchQuestions();
    state.events = await fetchEvents();
    state.initiatives = await fetchInitiatives();
    state.people = await fetchPeople();
    state.comments = await fetchComments();
  } catch {
    state.questions = DEFAULT_QUESTIONS;
    state.events = [];
    state.initiatives = [];
    state.people = [];
    state.comments = [];
  }
  mergeLocalInteractionsIntoComments();
  buildQuestionOrder({ resetIndex: true });
  render();
}

async function fetchQuestions() {
  try {
    const res = await fetch("/api/questions");
    if (!res.ok) throw new Error("API unavailable");
    const rows = await res.json();
    if (Array.isArray(rows) && rows.length > 0) return rows;
  } catch {}

  try {
    const fallback = await fetch("data/questions.json");
    if (!fallback.ok) throw new Error("Questions file unavailable");
    const rows = await fallback.json();
    if (Array.isArray(rows) && rows.length > 0) return rows;
  } catch {}

  return DEFAULT_QUESTIONS;
}

async function fetchEvents() {
  try {
    const res = await fetch("/api/events");
    if (!res.ok) throw new Error("API unavailable");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("data/events.json");
      if (!fallback.ok) throw new Error("Events file unavailable");
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
    if (!res.ok) throw new Error("API unavailable");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("data/initiatives.json");
      if (!fallback.ok) throw new Error("Initiatives file unavailable");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

async function fetchPeople() {
  try {
    const res = await fetch("/api/people");
    if (!res.ok) throw new Error("People API unavailable");
    const rows = await res.json();
    if (Array.isArray(rows)) return rows;
  } catch {
    try {
      const fallback = await fetch("data/people.json");
      if (!fallback.ok) throw new Error("People file unavailable");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

async function fetchComments() {
  try {
    const res = await fetch("/api/comments");
    if (!res.ok) throw new Error("Comments API unavailable");
    const rows = await res.json();
    return Array.isArray(rows) ? rows : [];
  } catch {
    try {
      const fallback = await fetch("data/comments.json");
      if (!fallback.ok) throw new Error("Comments file unavailable");
      const rows = await fallback.json();
      return Array.isArray(rows) ? rows : [];
    } catch {
      return [];
    }
  }
}

function render() {
  updateShellVisibility();
  updateTopNavActive();
  if (!state.questions.length) return renderSimplePage("Keine Fragen", "Es sind noch keine Fragen eingetragen.");
  if (state.view === "question") return renderQuestionView();
  if (state.view === "questions") return renderQuestionsView();
  if (state.view === "author") return renderAuthorView();
  if (state.view === "people") return renderPeopleView();
  if (state.view === "initiatives") return renderInitiativesView();
  if (state.view === "calendar") return renderCalendarView();
  return renderQuestionView();
}

function handleQuestionAction(action, ratingRaw, idRaw) {
  if (action === "reveal-rating") {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("ps:question-opened"));
    }
    if (!state.menuEnabled) {
      state.menuEnabled = true;
      updateShellVisibility();
    }
    state.questionStep = "comment";
    renderQuestionView();
    return;
  }

  if (action === "show-own-question") {
    state.questionStep = "own-question";
    renderQuestionView();
    return;
  }

  if (action === "back-to-comment") {
    state.questionStep = "comment";
    renderQuestionView();
    return;
  }

  if (action === "next") {
    nextQuestion();
    return;
  }

  if (action === "prev") {
    previousQuestion();
    return;
  }

  if (action === "submit") {
    const question = currentQuestion();
    if (!question) return;
    const existing = getInteraction(question.id);
    const nameInput = app.querySelector("#commentNameInput");
    const name = nameInput ? nameInput.value.trim() : "";
    const commentInput = app.querySelector("#commentInput");
    const comment = commentInput ? commentInput.value.trim() : "";
    saveInteraction(question.id, Number(existing.rating || 0), comment, name);
    renderQuestionView();
    return;
  }

  if (action === "submit-own-question") {
    const textInput = app.querySelector("#ownQuestionText");
    const authorInput = app.querySelector("#ownQuestionAuthor");
    const dateInput = app.querySelector("#ownQuestionDate");
    const locationInput = app.querySelector("#ownQuestionLocation");
    const text = textInput ? textInput.value.trim() : "";
    if (!text) {
      if (typeof window !== "undefined" && window.alert) window.alert("Bitte zuerst eine Frage eingeben.");
      return;
    }
    const payload = {
      text,
      author: authorInput ? authorInput.value.trim() : "",
      createdAt: dateInput && dateInput.value ? `${dateInput.value}T12:00:00.000Z` : "",
      location: locationInput ? locationInput.value.trim() : ""
    };
    submitPublicQuestion(payload).then((ok) => {
      if (!ok) return;
      nextQuestion();
    });
    return;
  }

  if (action === "submit-reply") {
    const commentId = String(idRaw || ratingRaw || "");
    if (!commentId) return;
    const textInput = app.querySelector(`textarea[data-reply-text-for="${escapeHtml(commentId)}"]`);
    const nameInput = app.querySelector(`input[data-reply-name-for="${escapeHtml(commentId)}"]`);
    const text = textInput ? textInput.value.trim() : "";
    const name = nameInput ? nameInput.value.trim() : "";
    if (!text) return;
    submitReply(commentId, text, name);
    if (textInput) textInput.value = "";
  }
}

function renderQuestionView() {
  const question = currentQuestion();
  if (!question) return renderSimplePage("Keine Fragen", "Es sind noch keine Fragen eingetragen.");

  const interaction = getInteraction(question.id);
  const effectiveName = interaction.name || "";
  const effectiveComment = interaction.comment || "";

  const commentBlock = state.questionStep === "comment"
    ? `<section class="flow-step answer-step"><textarea id="commentInput" class="answer-input" rows="4" placeholder="Deine Antwort">${escapeHtml(effectiveComment)}</textarea><input id="commentNameInput" class="answer-name-input" type="text" placeholder="Dein Name" value="${escapeHtml(effectiveName)}" /><div class="actions quiet-actions"><button class="quiet-btn quiet-btn-primary" data-action="submit" type="button">Speichern</button><button class="quiet-btn" data-action="next" type="button">Nächste Frage</button><button class="quiet-btn" data-action="show-own-question" type="button">Eigene Frage</button></div></section>`
    : "";

  const ownQuestionBlock = state.questionStep === "own-question"
    ? `<section class="flow-step"><p class="flow-label">Eigene Frage formulieren</p><textarea id="ownQuestionText" rows="3" placeholder="Frage"></textarea><input id="ownQuestionAuthor" type="text" placeholder="Autorin" /><input id="ownQuestionDate" type="date" /><input id="ownQuestionLocation" type="text" placeholder="Ort" /><div class="actions quiet-actions"><button class="quiet-btn quiet-btn-primary" data-action="submit-own-question" type="button">Frage senden & weiter</button><button class="quiet-btn" data-action="back-to-comment" type="button">Zurück</button></div></section>`
    : "";

  app.innerHTML = `
    <section class="question-flow" aria-live="polite">
      <div class="question-nav-line">
        <button class="question-edge-nav" type="button" data-action="prev" aria-label="Vorherige Frage">‹</button>
        <h1 class="question-title" data-action="reveal-rating" title="Frage öffnen">${escapeHtml(question.text)}</h1>
        <button class="question-edge-nav" type="button" data-action="next" aria-label="Nächste Frage">›</button>
      </div>
      ${commentBlock}
      ${ownQuestionBlock}
    </section>
  `;
}

function renderQuestionsView() {
  const sort = state.questionListSort;
  const rows = buildSortedQuestionRows(sort, state.questions);
  const controls = state.questionsControlsOpen
    ? `<div class="sort-strip centered-sort-strip" role="group" aria-label="Sortierung">
        <button class="sort-btn ${sort === "popular" ? "active" : ""}" type="button" data-action="sort-questions" data-sort="popular">Beliebt</button>
        <button class="sort-btn ${sort === "chronology" ? "active" : ""}" type="button" data-action="sort-questions" data-sort="chronology">Chronik</button>
        <button class="sort-btn ${sort === "interactions" ? "active" : ""}" type="button" data-action="sort-questions" data-sort="interactions">Aktiv</button>
      </div>`
    : "";
  app.innerHTML = `
    <section>
      <div class="questions-control-heart-wrap"><button class="questions-control-heart ${state.questionsControlsOpen ? "active" : ""}" type="button" data-action="toggle-list-controls" aria-label="Sortierung anzeigen">♥</button></div>
      ${controls}
      ${renderQuestionRows(rows, { showAuthorLinks: true })}
    </section>
  `;
}

function renderAuthorView() {
  const author = String(state.activeAuthor || "").trim();
  if (!author) {
    state.view = "questions";
    renderQuestionsView();
    return;
  }
  const filtered = state.questions.filter((q) =>
    (q.authors || []).some((a) => normalizeName(a) === normalizeName(author))
  );
  const rows = buildSortedQuestionRows(state.questionListSort, filtered);
  app.innerHTML = `
    <section>
      <div class="row-between">
        <h2>Fragen von ${escapeHtml(author)}</h2>
        <button class="sort-btn" type="button" data-action="clear-author-filter">Zur Fragenliste</button>
      </div>
      ${renderQuestionRows(rows, { showAuthorLinks: false })}
    </section>
  `;
}

function buildSortedQuestionRows(sort, questionsPool) {
  const pool = Array.isArray(questionsPool) ? questionsPool : [];
  const ids = new Set(pool.map((q) => String(q.id || "")));
  const statsRows = statsByQuestion().filter((row) => ids.has(String(row.question.id || "")));
  const statsById = new Map(statsRows.map((row) => [String(row.question.id || ""), row]));

  if (sort === "chronology") {
    return pool
      .slice()
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .map((q) => {
        const row = statsById.get(String(q.id || "")) || { votes: 0, comments: 0 };
        return { question: q, votes: row.votes, comments: row.comments };
      });
  }

  if (sort === "interactions") {
    return statsRows
      .slice()
      .sort((a, b) => b.votes + b.comments - (a.votes + a.comments))
      .map((row) => ({ question: row.question, votes: row.votes, comments: row.comments }));
  }

  return statsRows
    .slice()
    .sort((a, b) => b.votes - a.votes || b.comments - a.comments)
    .map((row) => ({ question: row.question, votes: row.votes, comments: row.comments }));
}

function renderQuestionRows(rows, options = {}) {
  const showAuthorLinks = options.showAuthorLinks !== false;
  const commentsByQuestion = getCommentsByQuestionMap();
  const markup = rows
    .map((row) => {
      const q = row.question || {};
      const qid = String(q.id || "");
      const detailOpen = Boolean(state.expandedQuestionDetails[qid]);
      const composeOpen = Boolean(state.expandedQuestionCompose[qid]);
      const answersOpen = Boolean(state.expandedQuestionComments[qid]);
      const commentRows = commentsByQuestion.get(qid) || [];
      const answerCount = countCommentEntries(commentRows);
      const interaction = getInteraction(qid);
      const userHeart = Number(interaction.rating || 0) > 0;
      const commentDraft = String(interaction.comment || "");
      const nameDraft = String(interaction.name || "");
      const dateText = formatShortDate(q.createdAt);
      const authorText = (q.authors || []).join(", ");
      const authorLine = showAuthorLinks
        ? (q.authors || [])
            .map(
              (author) =>
                `<button class="author-link" type="button" data-action="filter-author" data-author="${escapeHtml(author)}">${escapeHtml(author)}</button>`
            )
            .join(", ")
        : escapeHtml(authorText);
      const details = detailOpen
        ? `<div class="question-detail-line"><span>${dateText ? escapeHtml(dateText) : "Ohne Datum"}</span><span class="question-meta-sep">·</span><span>${authorLine || "Anonym"}</span><span class="question-meta-sep">·</span><button class="author-link question-heart-toggle ${userHeart ? "active" : ""}" type="button" data-action="toggle-list-heart" data-id="${escapeHtml(qid)}">${Number(row.votes || 0)} ♥</button><span class="question-meta-sep">·</span><button class="author-link question-compose-toggle" type="button" data-action="toggle-comment-compose" data-id="${escapeHtml(qid)}">Antworten${answerCount > 0 ? ` (${answerCount})` : ""}</button></div>`
        : "";
      const compose = detailOpen && composeOpen
        ? `<div class="list-comment-form answer-compose"><textarea class="answer-input" rows="3" data-comment-text-for="${escapeHtml(qid)}" placeholder="Deine Antwort">${escapeHtml(commentDraft)}</textarea><input class="answer-name-input" type="text" data-comment-name-for="${escapeHtml(qid)}" placeholder="Dein Name" value="${escapeHtml(nameDraft)}" /><div class="actions quiet-actions"><button class="quiet-btn quiet-btn-primary" type="button" data-action="save-list-comment" data-id="${escapeHtml(qid)}">Speichern</button><button class="quiet-btn" type="button" data-action="toggle-comments" data-id="${escapeHtml(qid)}">Antworten lesen</button></div></div>`
        : "";
      const answers = detailOpen && answersOpen && answerCount > 0
        ? `<div class="list answers-list">${commentRows
            .map((entry) => {
              const by = entry.name ? entry.name : "Anonym";
              const when = entry.updatedAt ? new Date(entry.updatedAt).toLocaleDateString("de-DE") : "";
              const text = String(entry.comment || "").trim();
              const replies = Array.isArray(entry.replies) ? entry.replies : [];
              const main = text ? `<p class="answer-text">${escapeHtml(text)}</p>` : "";
              const replyList = replies.length
                ? `<div class="list answers-list">${replies
                    .map((reply) => {
                      const rb = reply.name ? reply.name : "Anonym";
                      const rw = reply.createdAt ? new Date(reply.createdAt).toLocaleDateString("de-DE") : "";
                      return `<article class="card"><p class="answer-text">${escapeHtml(reply.text || "")}</p><p class="muted answer-by">${escapeHtml(rb)}${rw ? ` · ${escapeHtml(rw)}` : ""}</p></article>`;
                    })
                    .join("")}</div>`
                : "";
              if (!main && !replyList) return "";
              return `<article class="card">${main}<p class="muted answer-by">${escapeHtml(by)}${when ? ` · ${escapeHtml(when)}` : ""}</p>${replyList}</article>`;
            })
            .join("")}</div>`
        : "";
      return `<article class="card question-list-item"><h3><button class="question-open-btn" type="button" data-action="toggle-question-detail" data-id="${escapeHtml(qid)}">${escapeHtml(q.text || "")}</button></h3>${details}${compose}${answers}</article>`;
    })
    .join("");
  return `<div class="question-stack">${markup}</div>`;
}

function renderPeopleView() {
  if (!state.people.length) return renderSimplePage("Menschen", "Noch keine Ensemble-Mitglieder eingetragen.");
  if (!Array.isArray(state.shuffledPeople) || state.shuffledPeople.length !== state.people.length) {
    state.shuffledPeople = shuffleArray(state.people.slice());
  }
  app.innerHTML = `
    <section>
      <div class="list people-grid">
        ${state.shuffledPeople
          .map((person) => {
            const slug = person.slug || slugify(person.name || "");
            const image = person.portraitUrl
              ? `<img class="member-avatar-small" src="${escapeHtml(person.portraitUrl)}" alt="${escapeHtml(person.name || "")}" loading="lazy" />`
              : `<div class="member-avatar-small member-avatar-fallback">${escapeHtml(initials(person.name || ""))}</div>`;
            return `<article class="card member-card member-card-portrait">${image}<div class="member-card-content"><h3><a class="member-link" href="/members/${escapeHtml(slug)}.html">${escapeHtml(person.name || "")}</a></h3></div></article>`;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderInitiativesView() {
  if (!state.initiatives.length) return renderSimplePage("Initiativen", "Noch keine Initiativen eingetragen.");
  const grouped = new Map();
  for (let i = 0; i < state.initiatives.length; i += 1) {
    const item = state.initiatives[i];
    const category = String(item.category || "Initiativen");
    if (!grouped.has(category)) grouped.set(category, []);
    grouped.get(category).push(item);
  }
  const preferredOrder = ["Orte", "Initiativen"];
  const categories = Array.from(grouped.keys()).sort((a, b) => {
    const ai = preferredOrder.indexOf(a);
    const bi = preferredOrder.indexOf(b);
    if (ai >= 0 && bi >= 0) return ai - bi;
    if (ai >= 0) return -1;
    if (bi >= 0) return 1;
    return a.localeCompare(b, "de");
  });

  app.innerHTML = `
    <section>
      <h2>Initiativen</h2>
      ${categories
        .map((category) => {
          const items = grouped.get(category) || [];
          return `<section class="initiative-group"><h3 class="initiative-group-title">${escapeHtml(category)}</h3><div class="list initiatives-grid">${items
            .map((i) => {
              const href = initiativeHref(i);
              return `<article class="card"><h3><a class="member-link" href="${escapeHtml(href)}">${escapeHtml(i.title)}</a></h3><p class="muted">${escapeHtml(i.description || "")}</p><p><a class="member-link" href="${escapeHtml(href)}">Mehr</a></p></article>`;
            })
          .join("")}
          </div></section>`;
        })
        .join("")}
    </section>
  `;
}

function renderCalendarView() {
  if (!state.events.length) return renderSimplePage("Kalender", "Noch keine Veranstaltungen eingetragen.");
  const rows = state.events.slice().sort((a, b) => eventSortValue(b) - eventSortValue(a));
  let lastYear = "";
  let lastMonth = "";
  const blocks = [];
  for (let i = 0; i < rows.length; i += 1) {
    const event = rows[i];
    const parsed = parseEventDate(event.date);
    if (parsed && parsed.year !== lastYear) {
      lastYear = parsed.year;
      lastMonth = "";
      blocks.push(`<div class="calendar-year">${escapeHtml(parsed.year)}</div>`);
    }
    if (parsed && parsed.month !== lastMonth) {
      lastMonth = parsed.month;
      blocks.push(`<div class="calendar-month">${escapeHtml(parsed.month)}</div>`);
    }
    blocks.push(renderCalendarCard(event, parsed));
  }
  app.innerHTML = `
    <section>
      <h2>Kalender</h2>
      <div class="list calendar-list">
        ${blocks.join("")}
      </div>
    </section>
  `;
}

function renderCalendarCard(event, parsedDate) {
  const dateLabel = parsedDate ? parsedDate.full : String(event.date || "");
  const subtitle = [event.location || "", event.description || ""].filter(Boolean).join(" · ");
  const link = event.sourceUrl
    ? `<a class="calendar-link" target="_blank" rel="noopener noreferrer" href="${escapeHtml(event.sourceUrl)}">Zur Veranstaltung</a>`
    : "";
  return `<article class="card calendar-card"><p class="calendar-date">${escapeHtml(dateLabel)}</p><h3>${escapeHtml(event.title || "")}</h3><p class="calendar-subtitle">${escapeHtml(subtitle)}</p>${link}</article>`;
}

function parseEventDate(value) {
  const d = new Date(String(value || ""));
  if (Number.isNaN(d.getTime())) return null;
  const year = String(d.getFullYear());
  const month = capitalize(d.toLocaleDateString("de-DE", { month: "long" }));
  const full = d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "long", year: "numeric" });
  return { year, month, full };
}

function eventSortValue(event) {
  const ts = Date.parse(String(event && event.date ? event.date : ""));
  return Number.isFinite(ts) ? ts : Number.NEGATIVE_INFINITY;
}

function currentQuestion() {
  if (!state.questions.length) return null;
  if (!isQuestionOrderValid()) buildQuestionOrder({ resetIndex: false });
  if (!state.questionOrder.length) return state.questions[state.currentIndex % state.questions.length];
  const id = state.questionOrder[state.currentIndex % state.questionOrder.length];
  for (let i = 0; i < state.questions.length; i += 1) {
    if (String(state.questions[i].id || "") === String(id || "")) return state.questions[i];
  }
  return state.questions[state.currentIndex % state.questions.length];
}

function nextQuestion() {
  if (!state.questions.length) return;
  if (!isQuestionOrderValid()) buildQuestionOrder({ resetIndex: false });
  const total = state.questionOrder.length || state.questions.length;
  state.currentIndex = (state.currentIndex + 1) % total;
  state.currentRating = 0;
  state.questionStep = "intro";
  renderQuestionView();
}

function previousQuestion() {
  if (!state.questions.length) return;
  if (!isQuestionOrderValid()) buildQuestionOrder({ resetIndex: false });
  const total = state.questionOrder.length || state.questions.length;
  state.currentIndex = (state.currentIndex - 1 + total) % total;
  state.currentRating = 0;
  state.questionStep = "intro";
  renderQuestionView();
}

function saveInteraction(questionId, rating, comment, name) {
  const safeRating = Number(rating) > 0 ? 1 : 0;
  const saved = {
    questionId,
    rating: safeRating,
    name: String(name || ""),
    comment: String(comment || ""),
    updatedAt: new Date().toISOString(),
    browserId: state.interactions.browserId
  };
  state.interactions.responses[questionId] = saved;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.interactions));
  } catch {}
  upsertCommentInState(saved);
  persistComment(saved);
}

function getInteraction(questionId) {
  return state.interactions.responses[questionId] || { rating: 0, comment: "", name: "" };
}

function loadInteractionsState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        return {
          browserId: String(parsed.browserId || makeBrowserId()),
          responses: parsed.responses && typeof parsed.responses === "object" ? parsed.responses : {}
        };
      }
    }
  } catch {}

  const migrated = migrateLegacyInteractions();
  const fresh = { browserId: makeBrowserId(), responses: migrated };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh));
  } catch {}
  return fresh;
}

function migrateLegacyInteractions() {
  try {
    const raw = localStorage.getItem(LEGACY_STORAGE_KEY);
    const arr = JSON.parse(raw || "[]");
    if (!Array.isArray(arr)) return {};
    const byQuestion = {};
    for (let i = 0; i < arr.length; i += 1) {
      const row = arr[i] || {};
      const qid = String(row.questionId || "");
      if (!qid) continue;
      byQuestion[qid] = {
        questionId: qid,
        rating: Number(row.rating) > 0 ? 1 : 0,
        name: String(row.name || ""),
        comment: String(row.comment || ""),
        updatedAt: row.createdAt || new Date().toISOString()
      };
    }
    return byQuestion;
  } catch {
    return {};
  }
}

function makeBrowserId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return "browser-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function statsByQuestion() {
  const map = new Map();
  for (let i = 0; i < state.questions.length; i += 1) {
    const q = state.questions[i];
    map.set(q.id, { question: q, votes: 0, sum: 0, comments: 0 });
  }
  const comments = Array.isArray(state.comments) ? state.comments : [];
  for (let i = 0; i < comments.length; i += 1) {
    const row = comments[i];
    const target = map.get(row.questionId);
    if (!target) continue;
    if (Number(row.rating) > 0) {
      target.votes += 1;
      target.sum += 1;
    }
    if (row.comment) target.comments += 1;
    const replies = Array.isArray(row.replies) ? row.replies : [];
    target.comments += replies.length;
  }
  return Array.from(map.values());
}

function renderSimplePage(title, text) {
  app.innerHTML = `<section class="card"><h2>${escapeHtml(title)}</h2><p class="muted">${escapeHtml(text)}</p></section>`;
}

function updateShellVisibility() {
  if (mainHeader) mainHeader.classList.toggle("hidden", !state.menuEnabled);
  if (siteFooter) siteFooter.classList.toggle("hidden", !state.menuEnabled);
}

function updateTopNavActive() {
  const links = document.querySelectorAll(".top-nav-link[data-view]");
  const activeView = state.view === "author" ? "questions" : state.view;
  links.forEach((el) => {
    const target = String(el.dataset.view || "");
    el.classList.toggle("is-active", target === activeView);
  });
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

function initials(name) {
  return String(name)
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function shuffleArray(input) {
  const arr = Array.isArray(input) ? input.slice() : [];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
  }
  return arr;
}

function slugify(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function capitalize(value) {
  const text = String(value || "");
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function normalizeName(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function findPersonByAuthor(authorName) {
  const target = normalizeName(authorName);
  if (!target) return null;
  for (let i = 0; i < state.people.length; i += 1) {
    const person = state.people[i];
    if (normalizeName(person.name) === target) return person;
  }
  return null;
}

function initiativeHref(initiative) {
  const id = String(initiative && initiative.id ? initiative.id : "").trim();
  if (id) return `/initiatives/${encodeURIComponent(id)}.html`;
  return "/initiatives.html";
}

function getInitialViewFromUrl() {
  try {
    const params = new URLSearchParams(window.location.search);
    const view = String(params.get("view") || "").trim();
    if (view === "question" || view === "questions" || view === "people" || view === "initiatives" || view === "calendar") {
      return view;
    }
    return "";
  } catch {
    return "";
  }
}

function mergeLocalInteractionsIntoComments() {
  const responses = state.interactions && state.interactions.responses ? state.interactions.responses : {};
  const keys = Object.keys(responses);
  for (let i = 0; i < keys.length; i += 1) {
    const row = responses[keys[i]];
    if (!row || !row.questionId) continue;
    upsertCommentInState(row);
  }
}

function upsertCommentInState(entry) {
  const replies = Array.isArray(entry.replies)
    ? entry.replies
        .map((reply) => ({
          id: String(reply.id || ""),
          browserId: String(reply.browserId || "").trim(),
          name: String(reply.name || "").trim(),
          text: String(reply.text || "").trim(),
          createdAt: String(reply.createdAt || "")
        }))
        .filter((reply) => reply.text)
    : [];
  const normalized = {
    id: String(entry.id || ""),
    questionId: String(entry.questionId || "").trim(),
    browserId: String(entry.browserId || state.interactions.browserId || "").trim(),
    rating: Number(entry.rating) > 0 ? 1 : 0,
    name: String(entry.name || "").trim(),
    comment: String(entry.comment || "").trim(),
    updatedAt: String(entry.updatedAt || new Date().toISOString()),
    replies
  };
  if (!normalized.questionId || !normalized.browserId) return;

  const idx = state.comments.findIndex(
    (row) =>
      String(row.questionId || "") === normalized.questionId &&
      String(row.browserId || "") === normalized.browserId
  );
  if (idx < 0) {
    state.comments.push(normalized);
    return;
  }

  const prev = state.comments[idx];
  const prevTs = Date.parse(String(prev.updatedAt || ""));
  const nextTs = Date.parse(String(normalized.updatedAt || ""));
  if (!Number.isFinite(prevTs) || !Number.isFinite(nextTs) || nextTs >= prevTs) {
    state.comments[idx] = { ...prev, ...normalized, id: normalized.id || prev.id || "" };
  }
}

function isQuestionOrderValid() {
  if (!state.questions.length) return true;
  if (!Array.isArray(state.questionOrder) || state.questionOrder.length !== state.questions.length) return false;
  const idSet = new Set(state.questions.map((q) => String(q.id || "")));
  for (let i = 0; i < state.questionOrder.length; i += 1) {
    if (!idSet.has(String(state.questionOrder[i] || ""))) return false;
  }
  return true;
}

function buildQuestionOrder(options = {}) {
  const resetIndex = Boolean(options.resetIndex);
  if (!state.questions.length) {
    state.questionOrder = [];
    state.currentIndex = 0;
    return;
  }

  const weighted = computeQuestionWeights();
  const remaining = weighted.slice();
  const ordered = [];

  while (remaining.length) {
    const pickIndex = weightedPickIndex(remaining.map((row) => row.weight));
    const picked = remaining.splice(pickIndex, 1)[0];
    ordered.push(picked.id);
  }

  const lastFirst = readLastFirstQuestionId();
  if (ordered.length > 1 && lastFirst && ordered[0] === lastFirst) {
    const swapIndex = 1 + Math.floor(Math.random() * (ordered.length - 1));
    const tmp = ordered[0];
    ordered[0] = ordered[swapIndex];
    ordered[swapIndex] = tmp;
  }

  state.questionOrder = ordered;
  writeLastFirstQuestionId(ordered[0] || "");

  if (resetIndex) {
    state.currentIndex = 0;
  } else {
    const max = state.questionOrder.length || state.questions.length;
    state.currentIndex = ((state.currentIndex % max) + max) % max;
  }
}

function computeQuestionWeights() {
  const stats = statsByQuestion();
  const byId = new Map(stats.map((row) => [String(row.question.id || ""), row]));
  const popularityRaw = [];

  for (let i = 0; i < state.questions.length; i += 1) {
    const q = state.questions[i];
    const row = byId.get(String(q.id || "")) || { votes: 0, comments: 0, sum: 0 };
    const raw = Math.log1p(row.votes + row.comments * 1.25);
    popularityRaw.push(raw);
  }

  const maxPopularity = Math.max(1, ...popularityRaw);
  const out = [];
  for (let i = 0; i < state.questions.length; i += 1) {
    const q = state.questions[i];
    const recency = recencyScore(q.createdAt);
    const popularity = popularityRaw[i] / maxPopularity;
    const randomPart = Math.random();
    const weight = 0.45 * recency + 0.35 * popularity + 0.2 * randomPart;
    out.push({ id: String(q.id || ""), weight: Math.max(0.05, weight) });
  }
  return out;
}

function recencyScore(createdAt) {
  const ts = Date.parse(String(createdAt || ""));
  if (!Number.isFinite(ts)) return 0.35;
  const ageMs = Math.max(0, Date.now() - ts);
  const ageDays = ageMs / 86400000;
  return Math.exp(-ageDays / 60);
}

function weightedPickIndex(weights) {
  const safe = Array.isArray(weights) ? weights : [];
  let sum = 0;
  for (let i = 0; i < safe.length; i += 1) sum += Math.max(0, Number(safe[i]) || 0);
  if (sum <= 0) return Math.floor(Math.random() * Math.max(1, safe.length));

  let r = Math.random() * sum;
  for (let i = 0; i < safe.length; i += 1) {
    r -= Math.max(0, Number(safe[i]) || 0);
    if (r <= 0) return i;
  }
  return Math.max(0, safe.length - 1);
}

function readLastFirstQuestionId() {
  try {
    return String(localStorage.getItem(FIRST_QUESTION_KEY) || "");
  } catch {
    return "";
  }
}

function writeLastFirstQuestionId(id) {
  try {
    localStorage.setItem(FIRST_QUESTION_KEY, String(id || ""));
  } catch {}
}

function getCommentsByQuestionMap() {
  const byQuestion = new Map();
  const rows = Array.isArray(state.comments) ? state.comments : [];
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    const qid = String(row.questionId || "");
    if (!qid) continue;
    const hasComment = Boolean(String(row.comment || "").trim());
    const hasReplies = Array.isArray(row.replies) && row.replies.length > 0;
    if (!hasComment && !hasReplies) continue;
    if (!byQuestion.has(qid)) byQuestion.set(qid, []);
    byQuestion.get(qid).push(row);
  }
  const keys = Array.from(byQuestion.keys());
  for (let i = 0; i < keys.length; i += 1) {
    const qid = keys[i];
    byQuestion.get(qid).sort((a, b) => Date.parse(String(b.updatedAt || "")) - Date.parse(String(a.updatedAt || "")));
  }
  return byQuestion;
}

function countCommentEntries(rows) {
  const safeRows = Array.isArray(rows) ? rows : [];
  let total = 0;
  for (let i = 0; i < safeRows.length; i += 1) {
    const row = safeRows[i];
    if (String(row.comment || "").trim()) total += 1;
    const replies = Array.isArray(row.replies) ? row.replies : [];
    total += replies.length;
  }
  return total;
}

function formatShortDate(value) {
  if (!value) return "";
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("de-DE");
}

async function persistComment(entry) {
  const payload = {
    questionId: String(entry.questionId || ""),
    browserId: String(entry.browserId || state.interactions.browserId || ""),
    rating: Number(entry.rating) > 0 ? 1 : 0,
    name: String(entry.name || ""),
    comment: String(entry.comment || "")
  };
  try {
    const res = await fetch("/api/comments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) return;
    const saved = await res.json();
    upsertCommentInState(saved);
    if (state.view === "questions" || state.view === "author") render();
  } catch {}
}

async function submitReply(commentId, text, name) {
  const payload = {
    text: String(text || "").trim(),
    name: String(name || "").trim(),
    browserId: String(state.interactions.browserId || "")
  };
  if (!payload.text) return;
  try {
    const res = await fetch(`/api/comments/${encodeURIComponent(commentId)}/replies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) return;
    const updated = await res.json();
    upsertCommentInState(updated);
    if (state.view === "questions" || state.view === "author") render();
  } catch {}
}

async function submitPublicQuestion(input) {
  const payload = {
    text: String(input.text || "").trim(),
    author: String(input.author || "").trim(),
    createdAt: String(input.createdAt || "").trim(),
    location: String(input.location || "").trim()
  };
  if (!payload.text) return false;
  try {
    const res = await fetch("/api/public/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) return false;
    const saved = await res.json();
    state.questions.push(saved);
    buildQuestionOrder({ resetIndex: false });
    return true;
  } catch {
    return false;
  }
}
