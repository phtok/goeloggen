#!/usr/bin/env node
const http = require("http");
const fs = require("fs/promises");
const path = require("path");
const crypto = require("crypto");

const HOST = process.env.HOST || "127.0.0.1";
const PORT = Number(process.env.PORT || 8787);
const ROOT = __dirname;
const DATA_DIR = path.join(ROOT, "data");
const QUESTIONS_FILE = path.join(DATA_DIR, "questions.json");
const EVENTS_FILE = path.join(DATA_DIR, "events.json");
const INITIATIVES_FILE = path.join(DATA_DIR, "initiatives.json");
const PEOPLE_FILE = path.join(DATA_DIR, "people.json");
const COMMENTS_FILE = path.join(DATA_DIR, "comments.json");
const TOKENS_FILE = path.join(DATA_DIR, "member_login_tokens.json");
const OUTBOX_FILE = path.join(DATA_DIR, "member_login_outbox.json");
const SESSION_TTL_MS = 1000 * 60 * 60 * 12;
const MEMBER_TOKEN_TTL_MS = 1000 * 60 * 15;
const COOKIE_NAME = "ps_session";

const sessions = new Map();
const editors = loadEditors();

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon"
};

start().catch((error) => {
  console.error("Startup failed:", error);
  process.exit(1);
});

async function start() {
  await ensureDataFiles();

  const server = http.createServer(async (req, res) => {
    try {
      await handleRequest(req, res);
    } catch (error) {
      console.error("Unhandled error:", error);
      sendJson(res, 500, { error: "Internal server error" });
    }
  });

  server.listen(PORT, HOST, () => {
    console.log(`Public Secrete server running on http://${HOST}:${PORT}`);
  });
}

async function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const pathname = normalizePath(url.pathname);

  if (pathname.startsWith("/api/")) {
    return handleApi(req, res, pathname, url);
  }

  return serveStatic(res, pathname);
}

async function handleApi(req, res, pathname, url) {
  if (req.method === "POST" && pathname === "/api/auth/login") {
    const body = await readJsonBody(req);
    const user = editors.find((entry) => entry.username === body.username && entry.password === body.password);
    if (!user) return sendJson(res, 401, { error: "Ungueltige Anmeldedaten" });

    const sid = createSession({ role: "editor", username: user.username });
    setSessionCookie(res, sid);
    return sendJson(res, 200, { username: user.username });
  }

  if (req.method === "POST" && pathname === "/api/auth/logout") {
    const sid = getSessionId(req);
    if (sid) sessions.delete(sid);
    clearSessionCookie(res);
    return sendJson(res, 200, { ok: true });
  }

  if (req.method === "GET" && pathname === "/api/auth/me") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    return sendJson(res, 200, { username: session.username });
  }

  if (req.method === "POST" && pathname === "/api/member/auth/request") {
    const body = await readJsonBody(req);
    const email = String(body.email || "").trim().toLowerCase();
    if (!email) return sendJson(res, 400, { error: "E-Mail fehlt" });

    const people = await readData(PEOPLE_FILE);
    const person = people.find((p) => String(p.email || "").trim().toLowerCase() === email);
    if (!person) return sendJson(res, 200, { ok: true });

    const token = crypto.randomBytes(24).toString("hex");
    const tokens = await readData(TOKENS_FILE);
    tokens.push({
      token,
      memberSlug: String(person.slug || ""),
      email,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + MEMBER_TOKEN_TTL_MS).toISOString(),
      usedAt: null
    });
    await writeData(TOKENS_FILE, tokens);

    const baseUrl = `http://${req.headers.host || `${HOST}:${PORT}`}`;
    const loginUrl = `${baseUrl}/member-login.html?token=${token}`;
    const delivery = await deliverMemberMagicLink(email, person, loginUrl);
    return sendJson(res, 200, {
      ok: true,
      delivery: delivery.mode,
      previewUrl: delivery.previewUrl || null
    });
  }

  if (req.method === "POST" && pathname === "/api/member/auth/verify") {
    const body = await readJsonBody(req);
    const tokenValue = String(body.token || "").trim();
    if (!tokenValue) return sendJson(res, 400, { error: "Token fehlt" });

    const tokens = await readData(TOKENS_FILE);
    const idx = tokens.findIndex((t) => t.token === tokenValue);
    if (idx < 0) return sendJson(res, 401, { error: "Token ungültig" });
    const row = tokens[idx];
    if (row.usedAt) return sendJson(res, 401, { error: "Token bereits verwendet" });
    if (Date.parse(row.expiresAt) < Date.now()) return sendJson(res, 401, { error: "Token abgelaufen" });

    const people = await readData(PEOPLE_FILE);
    const person = people.find((p) => String(p.slug || "") === String(row.memberSlug || ""));
    if (!person) return sendJson(res, 401, { error: "Mitglied nicht gefunden" });

    tokens[idx] = { ...row, usedAt: new Date().toISOString() };
    await writeData(TOKENS_FILE, tokens);

    const sid = createSession({
      role: "member",
      memberSlug: String(person.slug || ""),
      memberName: String(person.name || "")
    });
    setSessionCookie(res, sid);
    return sendJson(res, 200, { ok: true, memberSlug: person.slug, memberName: person.name });
  }

  if (req.method === "POST" && pathname === "/api/member/auth/logout") {
    const sid = getSessionId(req);
    if (sid) sessions.delete(sid);
    clearSessionCookie(res);
    return sendJson(res, 200, { ok: true });
  }

  if (req.method === "GET" && pathname === "/api/member/auth/me") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    return sendJson(res, 200, { memberSlug: session.memberSlug, memberName: session.memberName });
  }

  if (req.method === "GET" && pathname === "/api/questions") {
    const questions = await readData(QUESTIONS_FILE);
    return sendJson(res, 200, questions);
  }

  if (req.method === "GET" && pathname === "/api/people") {
    const people = await readData(PEOPLE_FILE);
    return sendJson(res, 200, people);
  }

  if (req.method === "GET" && pathname === "/api/events") {
    let events = await readData(EVENTS_FILE);
    const archived = url.searchParams.get("archived");
    if (archived === "true") events = events.filter((e) => Boolean(e.archived));
    if (archived === "false") events = events.filter((e) => !e.archived);
    return sendJson(res, 200, events);
  }

  if (req.method === "GET" && pathname === "/api/initiatives") {
    const initiatives = await readData(INITIATIVES_FILE);
    return sendJson(res, 200, initiatives);
  }

  if (req.method === "GET" && pathname === "/api/comments") {
    const comments = await readData(COMMENTS_FILE);
    const questionId = String(url.searchParams.get("questionId") || "").trim();
    const rows = comments
      .filter((row) => (questionId ? String(row.questionId || "") === questionId : true))
      .filter((row) => {
        const hasComment = String(row.comment || "").trim().length > 0;
        const hasReplies = Array.isArray(row.replies) && row.replies.length > 0;
        return hasComment || hasReplies || Number(row.rating) > 0;
      })
      .sort((a, b) => Date.parse(String(b.updatedAt || "")) - Date.parse(String(a.updatedAt || "")));
    return sendJson(res, 200, rows);
  }

  if (req.method === "POST" && pathname === "/api/comments") {
    const body = await readJsonBody(req);
    const questionId = String(body.questionId || "").trim();
    const browserId = String(body.browserId || "").trim();
    if (!questionId) return sendJson(res, 400, { error: "questionId fehlt" });
    if (!browserId) return sendJson(res, 400, { error: "browserId fehlt" });

    const comments = await readData(COMMENTS_FILE);
    const nextRow = normalizeCommentRow({
      id: makeId("cm"),
      questionId,
      browserId,
      rating: body.rating,
      name: body.name,
      comment: body.comment,
      updatedAt: new Date().toISOString()
    });
    const idx = comments.findIndex(
      (row) => String(row.questionId || "") === questionId && String(row.browserId || "") === browserId
    );
    if (idx >= 0) comments[idx] = { ...comments[idx], ...nextRow, id: comments[idx].id || nextRow.id };
    else comments.push(nextRow);
    await writeData(COMMENTS_FILE, comments);
    return sendJson(res, 200, idx >= 0 ? comments[idx] : nextRow);
  }

  if (req.method === "POST" && /^\/api\/comments\/[^/]+\/replies$/.test(pathname)) {
    const body = await readJsonBody(req);
    const match = pathname.match(/^\/api\/comments\/([^/]+)\/replies$/);
    const commentId = decodeURIComponent(match ? match[1] : "");
    if (!commentId) return sendJson(res, 400, { error: "commentId fehlt" });
    const text = String(body.text || "").trim();
    if (!text) return sendJson(res, 400, { error: "Antworttext fehlt" });

    const comments = await readData(COMMENTS_FILE);
    const idx = comments.findIndex((row) => String(row.id || "") === commentId);
    if (idx < 0) return sendJson(res, 404, { error: "Kommentar nicht gefunden" });

    const reply = normalizeReplyRow({
      id: makeId("rp"),
      browserId: String(body.browserId || "").trim(),
      name: body.name,
      text,
      createdAt: new Date().toISOString()
    });

    const current = normalizeCommentRow(comments[idx]);
    const replies = Array.isArray(current.replies) ? current.replies.slice() : [];
    replies.push(reply);

    const updated = normalizeCommentRow({
      ...current,
      replies,
      updatedAt: new Date().toISOString()
    });
    comments[idx] = updated;
    await writeData(COMMENTS_FILE, comments);
    return sendJson(res, 200, updated);
  }

  if (req.method === "GET" && pathname === "/api/member/profile") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const people = await readData(PEOPLE_FILE);
    const person = people.find((p) => String(p.slug || "") === String(session.memberSlug || ""));
    if (!person) return sendJson(res, 404, { error: "Mitglied nicht gefunden" });
    return sendJson(res, 200, person);
  }

  if (req.method === "PUT" && pathname === "/api/member/profile") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const people = await readData(PEOPLE_FILE);
    const idx = people.findIndex((p) => String(p.slug || "") === String(session.memberSlug || ""));
    if (idx < 0) return sendJson(res, 404, { error: "Mitglied nicht gefunden" });
    const current = people[idx];
    people[idx] = {
      ...current,
      role: body.role === undefined ? current.role || "" : String(body.role).trim(),
      bio: body.bio === undefined ? current.bio || "" : String(body.bio).trim(),
      bioShort: body.bioShort === undefined ? current.bioShort || "" : String(body.bioShort).trim(),
      portraitUrl: body.portraitUrl === undefined ? current.portraitUrl || "" : String(body.portraitUrl).trim(),
      links: body.links === undefined ? normalizeLinks(current.links || []) : normalizeLinks(body.links)
    };
    await writeData(PEOPLE_FILE, people);
    return sendJson(res, 200, people[idx]);
  }

  if (req.method === "GET" && pathname === "/api/member/questions") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const questions = await readData(QUESTIONS_FILE);
    const own = questions.filter((q) => includesMember(q.authors, session.memberName));
    return sendJson(res, 200, own);
  }

  if (req.method === "POST" && pathname === "/api/member/questions") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const authors = ensureMemberHost(normalizeAuthors(body.authors), session.memberName);
    const newItem = {
      id: makeId("q"),
      text: String(body.text || "").trim(),
      authors,
      createdAt: normalizeCreatedAt(body.createdAt),
      location: String(body.location || "").trim()
    };
    if (!newItem.text) return sendJson(res, 400, { error: "Fragetext fehlt" });
    const questions = await readData(QUESTIONS_FILE);
    questions.push(newItem);
    await writeData(QUESTIONS_FILE, questions);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/member/questions/") && req.method === "PUT") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const questions = await readData(QUESTIONS_FILE);
    const idx = questions.findIndex((q) => q.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Frage nicht gefunden" });
    if (!includesMember(questions[idx].authors, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const authors = ensureMemberHost(
      body.authors === undefined ? questions[idx].authors || [] : normalizeAuthors(body.authors),
      session.memberName
    );
    const updated = {
      ...questions[idx],
      text: body.text === undefined ? questions[idx].text : String(body.text).trim(),
      authors,
      createdAt: body.createdAt === undefined ? questions[idx].createdAt : normalizeCreatedAt(body.createdAt, questions[idx].createdAt),
      location: body.location === undefined ? questions[idx].location || "" : String(body.location).trim()
    };
    if (!updated.text) return sendJson(res, 400, { error: "Fragetext fehlt" });
    questions[idx] = updated;
    await writeData(QUESTIONS_FILE, questions);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/member/questions/") && req.method === "DELETE") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const questions = await readData(QUESTIONS_FILE);
    const row = questions.find((q) => q.id === id);
    if (!row) return sendJson(res, 404, { error: "Frage nicht gefunden" });
    if (!includesMember(row.authors, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const next = questions.filter((q) => q.id !== id);
    await writeData(QUESTIONS_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (req.method === "GET" && pathname === "/api/member/events") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const events = await readData(EVENTS_FILE);
    const own = events.filter((e) => includesMember(e.hosts, session.memberName));
    return sendJson(res, 200, own);
  }

  if (req.method === "POST" && pathname === "/api/member/events") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const hosts = ensureMemberHost(normalizeHosts(body.hosts), session.memberName);
    const newItem = {
      id: makeId("ev"),
      title: String(body.title || "").trim(),
      description: String(body.description || "").trim(),
      location: String(body.location || "").trim(),
      date: String(body.date || "").trim(),
      archived: Boolean(body.archived),
      hosts,
      sourceUrl: String(body.sourceUrl || "").trim()
    };
    if (!newItem.title || !newItem.date) return sendJson(res, 400, { error: "Titel und Datum sind Pflicht" });
    const events = await readData(EVENTS_FILE);
    events.push(newItem);
    await writeData(EVENTS_FILE, events);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/member/events/") && req.method === "PUT") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const events = await readData(EVENTS_FILE);
    const idx = events.findIndex((e) => e.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Termin nicht gefunden" });
    if (!includesMember(events[idx].hosts, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const hosts = ensureMemberHost(
      body.hosts === undefined ? events[idx].hosts || [] : normalizeHosts(body.hosts),
      session.memberName
    );
    const updated = {
      ...events[idx],
      title: body.title === undefined ? events[idx].title : String(body.title).trim(),
      description: body.description === undefined ? events[idx].description : String(body.description).trim(),
      location: body.location === undefined ? events[idx].location : String(body.location).trim(),
      date: body.date === undefined ? events[idx].date : String(body.date).trim(),
      archived: body.archived === undefined ? events[idx].archived : Boolean(body.archived),
      hosts,
      sourceUrl: body.sourceUrl === undefined ? events[idx].sourceUrl || "" : String(body.sourceUrl).trim()
    };
    if (!updated.title || !updated.date) return sendJson(res, 400, { error: "Titel und Datum sind Pflicht" });
    events[idx] = updated;
    await writeData(EVENTS_FILE, events);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/member/events/") && req.method === "DELETE") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const events = await readData(EVENTS_FILE);
    const row = events.find((e) => e.id === id);
    if (!row) return sendJson(res, 404, { error: "Termin nicht gefunden" });
    if (!includesMember(row.hosts, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const next = events.filter((e) => e.id !== id);
    await writeData(EVENTS_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (req.method === "GET" && pathname === "/api/member/initiatives") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const initiatives = await readData(INITIATIVES_FILE);
    const own = initiatives.filter((i) => includesMember(i.hosts, session.memberName));
    return sendJson(res, 200, own);
  }

  if (req.method === "POST" && pathname === "/api/member/initiatives") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const hosts = ensureMemberHost(normalizeHosts(body.hosts), session.memberName);
    const newItem = {
      id: makeId("in"),
      title: String(body.title || "").trim(),
      description: String(body.description || "").trim(),
      status: String(body.status || "aktiv").trim(),
      hosts,
      sourceUrl: String(body.sourceUrl || "").trim()
    };
    if (!newItem.title) return sendJson(res, 400, { error: "Titel ist Pflicht" });
    const initiatives = await readData(INITIATIVES_FILE);
    initiatives.push(newItem);
    await writeData(INITIATIVES_FILE, initiatives);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/member/initiatives/") && req.method === "PUT") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const initiatives = await readData(INITIATIVES_FILE);
    const idx = initiatives.findIndex((i) => i.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Initiative nicht gefunden" });
    if (!includesMember(initiatives[idx].hosts, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const hosts = ensureMemberHost(
      body.hosts === undefined ? initiatives[idx].hosts || [] : normalizeHosts(body.hosts),
      session.memberName
    );
    const updated = {
      ...initiatives[idx],
      title: body.title === undefined ? initiatives[idx].title : String(body.title).trim(),
      description: body.description === undefined ? initiatives[idx].description : String(body.description).trim(),
      status: body.status === undefined ? initiatives[idx].status : String(body.status).trim(),
      hosts,
      sourceUrl: body.sourceUrl === undefined ? initiatives[idx].sourceUrl || "" : String(body.sourceUrl).trim()
    };
    if (!updated.title) return sendJson(res, 400, { error: "Titel ist Pflicht" });
    initiatives[idx] = updated;
    await writeData(INITIATIVES_FILE, initiatives);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/member/initiatives/") && req.method === "DELETE") {
    const session = requireMemberSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const initiatives = await readData(INITIATIVES_FILE);
    const row = initiatives.find((i) => i.id === id);
    if (!row) return sendJson(res, 404, { error: "Initiative nicht gefunden" });
    if (!includesMember(row.hosts, session.memberName)) return sendJson(res, 403, { error: "Kein Zugriff" });
    const next = initiatives.filter((i) => i.id !== id);
    await writeData(INITIATIVES_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (pathname === "/api/questions" && req.method === "POST") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const newItem = {
      id: makeId("q"),
      text: String(body.text || "").trim(),
      authors: normalizeAuthors(body.authors),
      createdAt: normalizeCreatedAt(body.createdAt),
      location: String(body.location || "").trim()
    };
    if (!newItem.text) return sendJson(res, 400, { error: "Fragetext fehlt" });
    if (newItem.authors.length === 0) newItem.authors = ["Anonym"];

    const questions = await readData(QUESTIONS_FILE);
    questions.push(newItem);
    await writeData(QUESTIONS_FILE, questions);
    return sendJson(res, 201, newItem);
  }

  if (pathname === "/api/people" && req.method === "POST") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const name = String(body.name || "").trim();
    const role = String(body.role || "").trim();
    const bio = String(body.bio || "").trim();
    const bioShort = String(body.bioShort || "").trim();
    const portraitUrl = String(body.portraitUrl || "").trim();
    const links = normalizeLinks(body.links);
    const email = String(body.email || "").trim().toLowerCase();
    const slug = String(body.slug || slugify(name)).trim();
    if (!name) return sendJson(res, 400, { error: "Name ist Pflicht" });

    const people = await readData(PEOPLE_FILE);
    const candidate = slug || makeId("member");
    const uniqueSlug = makeUniqueSlug(candidate, people.map((p) => String(p.slug || "")));
    const newItem = { name, role, slug: uniqueSlug, email, bio, bioShort, portraitUrl, links };
    people.push(newItem);
    await writeData(PEOPLE_FILE, people);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/questions/") && req.method === "PUT") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const questions = await readData(QUESTIONS_FILE);
    const idx = questions.findIndex((q) => q.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Frage nicht gefunden" });

    const updated = {
      ...questions[idx],
      text: String(body.text ?? questions[idx].text).trim(),
      authors: body.authors === undefined ? questions[idx].authors : normalizeAuthors(body.authors),
      createdAt: body.createdAt === undefined ? questions[idx].createdAt : normalizeCreatedAt(body.createdAt, questions[idx].createdAt),
      location: body.location === undefined ? questions[idx].location || "" : String(body.location).trim()
    };
    if (!updated.text) return sendJson(res, 400, { error: "Fragetext fehlt" });
    if (!updated.authors.length) updated.authors = ["Anonym"];

    questions[idx] = updated;
    await writeData(QUESTIONS_FILE, questions);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/people/") && req.method === "PUT") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const people = await readData(PEOPLE_FILE);
    const idx = people.findIndex((p) => String(p.slug || "") === id);
    if (idx < 0) return sendJson(res, 404, { error: "Mitglied nicht gefunden" });

    const updated = {
      ...people[idx],
      name: body.name === undefined ? people[idx].name : String(body.name).trim(),
      role: body.role === undefined ? people[idx].role || "" : String(body.role).trim(),
      email: body.email === undefined ? people[idx].email || "" : String(body.email).trim().toLowerCase(),
      bio: body.bio === undefined ? people[idx].bio || "" : String(body.bio).trim(),
      bioShort: body.bioShort === undefined ? people[idx].bioShort || "" : String(body.bioShort).trim(),
      portraitUrl: body.portraitUrl === undefined ? people[idx].portraitUrl || "" : String(body.portraitUrl).trim(),
      links: body.links === undefined ? normalizeLinks(people[idx].links || []) : normalizeLinks(body.links)
    };
    if (!updated.name) return sendJson(res, 400, { error: "Name ist Pflicht" });

    if (body.slug !== undefined) {
      const requested = String(body.slug || "").trim() || slugify(updated.name);
      const others = people.filter((_, i) => i !== idx).map((p) => String(p.slug || ""));
      updated.slug = makeUniqueSlug(requested, others);
    }

    people[idx] = updated;
    await writeData(PEOPLE_FILE, people);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/questions/") && req.method === "DELETE") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const questions = await readData(QUESTIONS_FILE);
    const next = questions.filter((q) => q.id !== id);
    if (next.length === questions.length) return sendJson(res, 404, { error: "Frage nicht gefunden" });
    await writeData(QUESTIONS_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (pathname === "/api/public/questions" && req.method === "POST") {
    const body = await readJsonBody(req);
    const text = String(body.text || "").trim();
    if (!text) return sendJson(res, 400, { error: "Fragetext fehlt" });
    const author = String(body.author || "").trim();
    const createdAt = normalizeCreatedAt(body.createdAt);
    const location = String(body.location || "").trim();
    const newItem = {
      id: makeId("q"),
      text,
      authors: author ? [author] : ["Anonym"],
      createdAt,
      location
    };
    const questions = await readData(QUESTIONS_FILE);
    questions.push(newItem);
    await writeData(QUESTIONS_FILE, questions);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/people/") && req.method === "DELETE") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const people = await readData(PEOPLE_FILE);
    const next = people.filter((p) => String(p.slug || "") !== id);
    if (next.length === people.length) return sendJson(res, 404, { error: "Mitglied nicht gefunden" });
    await writeData(PEOPLE_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (pathname === "/api/events" && req.method === "POST") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const newItem = {
      id: makeId("ev"),
      title: String(body.title || "").trim(),
      description: String(body.description || "").trim(),
      location: String(body.location || "").trim(),
      date: String(body.date || "").trim(),
      archived: Boolean(body.archived),
      hosts: normalizeHosts(body.hosts),
      sourceUrl: String(body.sourceUrl || "").trim()
    };
    if (!newItem.title || !newItem.date) return sendJson(res, 400, { error: "Titel und Datum sind Pflicht" });

    const events = await readData(EVENTS_FILE);
    events.push(newItem);
    await writeData(EVENTS_FILE, events);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/events/") && req.method === "PUT") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const events = await readData(EVENTS_FILE);
    const idx = events.findIndex((e) => e.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Termin nicht gefunden" });

    const updated = {
      ...events[idx],
      title: body.title === undefined ? events[idx].title : String(body.title).trim(),
      description: body.description === undefined ? events[idx].description : String(body.description).trim(),
      location: body.location === undefined ? events[idx].location : String(body.location).trim(),
      date: body.date === undefined ? events[idx].date : String(body.date).trim(),
      archived: body.archived === undefined ? events[idx].archived : Boolean(body.archived),
      hosts: body.hosts === undefined ? events[idx].hosts || [] : normalizeHosts(body.hosts),
      sourceUrl: body.sourceUrl === undefined ? events[idx].sourceUrl || "" : String(body.sourceUrl).trim()
    };
    if (!updated.title || !updated.date) return sendJson(res, 400, { error: "Titel und Datum sind Pflicht" });

    events[idx] = updated;
    await writeData(EVENTS_FILE, events);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/events/") && req.method === "DELETE") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const events = await readData(EVENTS_FILE);
    const next = events.filter((e) => e.id !== id);
    if (next.length === events.length) return sendJson(res, 404, { error: "Termin nicht gefunden" });
    await writeData(EVENTS_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  if (pathname === "/api/initiatives" && req.method === "POST") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const body = await readJsonBody(req);
    const newItem = {
      id: makeId("in"),
      title: String(body.title || "").trim(),
      description: String(body.description || "").trim(),
      status: String(body.status || "aktiv").trim(),
      hosts: normalizeHosts(body.hosts),
      sourceUrl: String(body.sourceUrl || "").trim()
    };
    if (!newItem.title) return sendJson(res, 400, { error: "Titel ist Pflicht" });

    const initiatives = await readData(INITIATIVES_FILE);
    initiatives.push(newItem);
    await writeData(INITIATIVES_FILE, initiatives);
    return sendJson(res, 201, newItem);
  }

  if (pathname.startsWith("/api/initiatives/") && req.method === "PUT") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const body = await readJsonBody(req);
    const initiatives = await readData(INITIATIVES_FILE);
    const idx = initiatives.findIndex((i) => i.id === id);
    if (idx < 0) return sendJson(res, 404, { error: "Initiative nicht gefunden" });

    const updated = {
      ...initiatives[idx],
      title: body.title === undefined ? initiatives[idx].title : String(body.title).trim(),
      description: body.description === undefined ? initiatives[idx].description : String(body.description).trim(),
      status: body.status === undefined ? initiatives[idx].status : String(body.status).trim(),
      hosts: body.hosts === undefined ? initiatives[idx].hosts || [] : normalizeHosts(body.hosts),
      sourceUrl: body.sourceUrl === undefined ? initiatives[idx].sourceUrl || "" : String(body.sourceUrl).trim()
    };
    if (!updated.title) return sendJson(res, 400, { error: "Titel ist Pflicht" });

    initiatives[idx] = updated;
    await writeData(INITIATIVES_FILE, initiatives);
    return sendJson(res, 200, updated);
  }

  if (pathname.startsWith("/api/initiatives/") && req.method === "DELETE") {
    const session = requireEditorSession(req, res);
    if (!session) return;
    const id = pathname.split("/").pop();
    const initiatives = await readData(INITIATIVES_FILE);
    const next = initiatives.filter((i) => i.id !== id);
    if (next.length === initiatives.length) return sendJson(res, 404, { error: "Initiative nicht gefunden" });
    await writeData(INITIATIVES_FILE, next);
    return sendJson(res, 200, { ok: true });
  }

  sendJson(res, 404, { error: "Not found" });
}

function requireSession(req, res) {
  cleanupExpiredSessions();
  const sid = getSessionId(req);
  const session = sid ? sessions.get(sid) : null;
  if (!session) {
    sendJson(res, 401, { error: "Nicht eingeloggt" });
    return null;
  }
  return session;
}

function requireEditorSession(req, res) {
  const session = requireSession(req, res);
  if (!session) return null;
  if (session.role !== "editor") {
    sendJson(res, 403, { error: "Nur Redaktion erlaubt" });
    return null;
  }
  return session;
}

function requireMemberSession(req, res) {
  const session = requireSession(req, res);
  if (!session) return null;
  if (session.role !== "member") {
    sendJson(res, 403, { error: "Nur Mitglied erlaubt" });
    return null;
  }
  return session;
}

function createSession(payload) {
  const id = crypto.randomBytes(24).toString("hex");
  sessions.set(id, {
    ...payload,
    expiresAt: Date.now() + SESSION_TTL_MS
  });
  return id;
}

function cleanupExpiredSessions() {
  const now = Date.now();
  for (const [id, session] of sessions.entries()) {
    if (session.expiresAt <= now) sessions.delete(id);
  }
}

function setSessionCookie(res, sid) {
  res.setHeader("Set-Cookie", `${COOKIE_NAME}=${sid}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${Math.floor(SESSION_TTL_MS / 1000)}`);
}

function clearSessionCookie(res) {
  res.setHeader("Set-Cookie", `${COOKIE_NAME}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0`);
}

function getSessionId(req) {
  const cookie = req.headers.cookie;
  if (!cookie) return null;
  const parts = cookie.split(";").map((part) => part.trim());
  const entry = parts.find((part) => part.startsWith(`${COOKIE_NAME}=`));
  if (!entry) return null;
  return entry.slice(COOKIE_NAME.length + 1);
}

async function serveStatic(res, pathname) {
  const rel = pathname === "/" ? "/index.html" : pathname;
  const filePath = path.join(ROOT, rel);
  if (!filePath.startsWith(ROOT)) return sendText(res, 403, "Forbidden");

  try {
    const stat = await fs.stat(filePath);
    if (stat.isDirectory()) return sendText(res, 403, "Forbidden");
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || "application/octet-stream";
    if (ext === ".html") {
      const raw = await fs.readFile(filePath, "utf-8");
      const data = Buffer.from(injectThemeAssets(raw), "utf-8");
      res.writeHead(200, {
        "Content-Type": contentType,
        "Cache-Control": "no-store"
      });
      res.end(data);
      return;
    }
    const data = await fs.readFile(filePath);
    res.writeHead(200, {
      "Content-Type": contentType,
      "Cache-Control": "no-store"
    });
    res.end(data);
  } catch {
    sendText(res, 404, "Not found");
  }
}

function injectThemeAssets(html) {
  let out = String(html || "");
  const prelude = '<script>try{const p=localStorage.getItem("ps_theme_preference_v2");const l=localStorage.getItem("ps_theme_invert_v1");const pref=(p==="light"||p==="dark"||p==="auto")?p:(l==="1"?"dark":(l==="0"?"light":"auto"));const dark=pref==="dark"||(pref==="auto"&&window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches);if(dark)document.documentElement.classList.add("theme-invert");const qs=new URLSearchParams(window.location.search);const qf=String(qs.get("font")||"").toLowerCase();const sf=String(localStorage.getItem("ps_font_mode_v1")||"").toLowerCase();const f=(qf==="proxima"||qf==="inclusive")?qf:((sf==="proxima"||sf==="inclusive")?sf:"inclusive");document.documentElement.classList.toggle("font-inclusive",f==="inclusive");document.documentElement.classList.toggle("font-proxima",f==="proxima");if(qf==="proxima"||qf==="inclusive")localStorage.setItem("ps_font_mode_v1",f);}catch{}</script>';
  const loader = '<script src="/theme-toggle.js"></script>';

  if (!out.includes("ps_theme_preference_v2")) {
    if (out.includes("</head>")) out = out.replace("</head>", `    ${prelude}\n  </head>`);
    else out = `${prelude}\n${out}`;
  }

  if (!out.includes("theme-toggle.js")) {
    if (out.includes("</body>")) out = out.replace("</body>", `    ${loader}\n  </body>`);
    else out = `${out}\n${loader}`;
  }

  return out;
}

async function ensureDataFiles() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await ensureJsonFile(QUESTIONS_FILE, []);
  await ensureJsonFile(EVENTS_FILE, [
    {
      id: "ev-001",
      title: "Wahrnehmungsorgan - Offenes Gespraech",
      description: "Gesprächsabend mit Fragen aus dem Ensemble.",
      location: "Basel",
      date: "2026-03-10",
      archived: false
    }
  ]);
  await ensureJsonFile(INITIATIVES_FILE, []);
  await ensureJsonFile(PEOPLE_FILE, []);
  await ensureJsonFile(COMMENTS_FILE, []);
  await ensureJsonFile(TOKENS_FILE, []);
  await ensureJsonFile(OUTBOX_FILE, []);
}

async function ensureJsonFile(filePath, fallback) {
  try {
    await fs.access(filePath);
  } catch {
    await writeData(filePath, fallback);
  }
}

async function readData(filePath) {
  const raw = await fs.readFile(filePath, "utf-8");
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

async function writeData(filePath, value) {
  const body = JSON.stringify(value, null, 2) + "\n";
  await fs.writeFile(filePath, body, "utf-8");
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf-8").trim();
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    throw createHttpError(400, "Ungueltiges JSON");
  }
}

function sendJson(res, status, payload) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(JSON.stringify(payload));
}

function sendText(res, status, text) {
  res.writeHead(status, {
    "Content-Type": "text/plain; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(text);
}

function normalizeAuthors(input) {
  if (Array.isArray(input)) {
    return input.map((v) => String(v).trim()).filter(Boolean);
  }
  if (typeof input === "string") {
    return input
      .split(",")
      .map((v) => v.trim())
      .filter(Boolean);
  }
  return [];
}

function normalizeHosts(input) {
  return normalizeAuthors(input);
}

function normalizeLinks(input) {
  if (Array.isArray(input)) {
    return input.map((v) => String(v).trim()).filter(Boolean);
  }
  if (typeof input === "string") {
    return input
      .split(/\r?\n|,/)
      .map((v) => v.trim())
      .filter(Boolean);
  }
  return [];
}

function normalizeCreatedAt(input, fallback) {
  if (input === undefined || input === null || String(input).trim() === "") {
    return fallback || new Date().toISOString();
  }
  const date = new Date(String(input));
  if (Number.isNaN(date.getTime())) {
    return fallback || new Date().toISOString();
  }
  return date.toISOString();
}

function normalizeCommentRow(input) {
  const replies = Array.isArray(input.replies) ? input.replies.map(normalizeReplyRow) : [];
  replies.sort((a, b) => Date.parse(String(a.createdAt || "")) - Date.parse(String(b.createdAt || "")));
  return {
    id: String(input.id || makeId("cm")),
    questionId: String(input.questionId || "").trim(),
    browserId: String(input.browserId || "").trim(),
    rating: Number(input.rating) > 0 ? 1 : 0,
    name: String(input.name || "").trim(),
    comment: String(input.comment || "").trim(),
    updatedAt: normalizeCreatedAt(input.updatedAt),
    replies
  };
}

function normalizeReplyRow(input) {
  return {
    id: String(input.id || makeId("rp")),
    browserId: String(input.browserId || "").trim(),
    name: String(input.name || "").trim(),
    text: String(input.text || "").trim(),
    createdAt: normalizeCreatedAt(input.createdAt)
  };
}

function normalizeName(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function includesMember(hosts, memberName) {
  const target = normalizeName(memberName);
  if (!target) return false;
  const list = Array.isArray(hosts) ? hosts : [];
  return list.some((h) => normalizeName(h) === target);
}

function ensureMemberHost(hosts, memberName) {
  const list = Array.isArray(hosts) ? hosts.map((h) => String(h).trim()).filter(Boolean) : [];
  if (!includesMember(list, memberName)) list.unshift(String(memberName || "").trim());
  return list.filter(Boolean);
}

function normalizePath(pathname) {
  return pathname.replace(/\/+$/, "") || "/";
}

function makeId(prefix) {
  const suffix = crypto.randomUUID ? crypto.randomUUID() : crypto.randomBytes(8).toString("hex");
  return `${prefix}-${suffix}`;
}

function slugify(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function makeUniqueSlug(baseSlug, existingSlugs) {
  const cleaned = slugify(baseSlug) || "mitglied";
  const used = new Set(existingSlugs.map((s) => String(s || "")));
  if (!used.has(cleaned)) return cleaned;
  let n = 2;
  while (used.has(`${cleaned}-${n}`)) n += 1;
  return `${cleaned}-${n}`;
}

async function deliverMemberMagicLink(email, person, loginUrl) {
  const apiKey = process.env.RESEND_API_KEY || "";
  const fromEmail = process.env.PUBLIC_SECRETE_FROM_EMAIL || "";
  const name = String(person.name || "Mitglied");

  if (apiKey && fromEmail) {
    try {
      const payload = {
        from: fromEmail,
        to: [email],
        subject: "Dein Public Secrets Einmalzugang",
        html: `<p>Hallo ${escapeHtmlForEmail(name)},</p><p>hier ist dein Einmalzugang für Public Secrets:</p><p><a href=\"${loginUrl}\">${loginUrl}</a></p><p>Der Link ist 15 Minuten gültig und nur einmal nutzbar.</p>`
      };
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) return { mode: "email" };
    } catch {}
  }

  const outbox = await readData(OUTBOX_FILE);
  outbox.push({
    email,
    memberSlug: String(person.slug || ""),
    createdAt: new Date().toISOString(),
    loginUrl
  });
  await writeData(OUTBOX_FILE, outbox.slice(-200));
  return { mode: "outbox", previewUrl: loginUrl };
}

function escapeHtmlForEmail(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function loadEditors() {
  const fromEnv = process.env.PUBLIC_SECRETE_EDITORS;
  if (fromEnv) {
    try {
      const parsed = JSON.parse(fromEnv);
      if (Array.isArray(parsed) && parsed.every((u) => u && u.username && u.password)) {
        return parsed.map((u) => ({ username: String(u.username), password: String(u.password) }));
      }
    } catch {
      console.warn("PUBLIC_SECRETE_EDITORS could not be parsed. Falling back to default editor.");
    }
  }
  return [{ username: "philipp@saetzerei.com", password: "public-secrets-123" }];
}

function createHttpError(status, message) {
  const err = new Error(message);
  err.status = status;
  return err;
}

process.on("uncaughtException", (err) => {
  if (err && err.status) {
    console.error(`HTTP ${err.status}: ${err.message}`);
    return;
  }
  console.error(err);
});
