const headline = document.getElementById("memberHeadline");
const logoutBtn = document.getElementById("logoutBtn");

const roleInput = document.getElementById("role");
const portraitUrlInput = document.getElementById("portraitUrl");
const portraitFileInput = document.getElementById("portraitFile");
const uploadPortraitBtn = document.getElementById("uploadPortraitBtn");
const portraitUploadStatus = document.getElementById("portraitUploadStatus");
const linksInput = document.getElementById("links");
const bioInput = document.getElementById("bio");
const saveProfileBtn = document.getElementById("saveProfileBtn");

const qId = document.getElementById("qId");
const qText = document.getElementById("qText");
const qDate = document.getElementById("qDate");
const qLocation = document.getElementById("qLocation");
const saveQuestionBtn = document.getElementById("saveQuestionBtn");
const resetQuestionBtn = document.getElementById("resetQuestionBtn");
const questionList = document.getElementById("questionList");

const iId = document.getElementById("iId");
const iTitle = document.getElementById("iTitle");
const iStatus = document.getElementById("iStatus");
const iDescription = document.getElementById("iDescription");
const iImageUrl = document.getElementById("iImageUrl");
const iImageFile = document.getElementById("iImageFile");
const uploadInitiativeImageBtn = document.getElementById("uploadInitiativeImageBtn");
const initiativeUploadStatus = document.getElementById("initiativeUploadStatus");
const iSourceUrl = document.getElementById("iSourceUrl");
const saveInitiativeBtn = document.getElementById("saveInitiativeBtn");
const resetInitiativeBtn = document.getElementById("resetInitiativeBtn");
const initiativeList = document.getElementById("initiativeList");

const eId = document.getElementById("eId");
const eTitle = document.getElementById("eTitle");
const eDate = document.getElementById("eDate");
const eLocation = document.getElementById("eLocation");
const eDescription = document.getElementById("eDescription");
const eImageUrl = document.getElementById("eImageUrl");
const eImageFile = document.getElementById("eImageFile");
const uploadEventImageBtn = document.getElementById("uploadEventImageBtn");
const eventUploadStatus = document.getElementById("eventUploadStatus");
const eSourceUrl = document.getElementById("eSourceUrl");
const eArchived = document.getElementById("eArchived");
const saveEventBtn = document.getElementById("saveEventBtn");
const resetEventBtn = document.getElementById("resetEventBtn");
const eventList = document.getElementById("eventList");

let me = null;
let cache = { questions: [], initiatives: [], events: [] };

init();

async function init() {
  const auth = await fetch("/api/member/auth/me");
  if (!auth.ok) {
    window.location.href = "/login.html";
    return;
  }
  me = await auth.json();
  headline.textContent = `Public Secrets - ${me.memberName}`;
  await Promise.all([loadProfile(), refreshQuestions(), refreshInitiatives(), refreshEvents()]);
}

logoutBtn.addEventListener("click", async () => {
  await fetch("/api/member/auth/logout", { method: "POST" });
  window.location.href = "/login.html";
});

saveProfileBtn.addEventListener("click", async () => {
  const body = {
    role: roleInput.value.trim(),
    portraitUrl: portraitUrlInput.value.trim(),
    links: parseLines(linksInput.value),
    bio: bioInput.value.trim()
  };
  const res = await fetch("/api/member/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) return alert("Profil konnte nicht gespeichert werden");
  await loadProfile();
});

uploadPortraitBtn.addEventListener("click", () =>
  handleImageUpload({
    fileInput: portraitFileInput,
    targetInput: portraitUrlInput,
    statusEl: portraitUploadStatus,
    target: "profile"
  })
);

saveQuestionBtn.addEventListener("click", async () => {
  const body = {
    text: qText.value.trim(),
    createdAt: qDate.value ? `${qDate.value}T12:00:00.000Z` : "",
    location: qLocation.value.trim()
  };
  const id = qId.value.trim();
  const url = id ? `/api/member/questions/${id}` : "/api/member/questions";
  const method = id ? "PUT" : "POST";
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) return alert("Frage konnte nicht gespeichert werden");
  resetQuestionForm();
  await refreshQuestions();
});

resetQuestionBtn.addEventListener("click", resetQuestionForm);

saveInitiativeBtn.addEventListener("click", async () => {
  const body = {
    title: iTitle.value.trim(),
    status: iStatus.value.trim() || "aktiv",
    description: iDescription.value.trim(),
    imageUrl: iImageUrl.value.trim(),
    sourceUrl: iSourceUrl.value.trim()
  };
  const id = iId.value.trim();
  const url = id ? `/api/member/initiatives/${id}` : "/api/member/initiatives";
  const method = id ? "PUT" : "POST";
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) return alert("Initiative konnte nicht gespeichert werden");
  resetInitiativeForm();
  await refreshInitiatives();
});

resetInitiativeBtn.addEventListener("click", resetInitiativeForm);

uploadInitiativeImageBtn.addEventListener("click", () =>
  handleImageUpload({
    fileInput: iImageFile,
    targetInput: iImageUrl,
    statusEl: initiativeUploadStatus,
    target: "initiative"
  })
);

saveEventBtn.addEventListener("click", async () => {
  const body = {
    title: eTitle.value.trim(),
    date: eDate.value,
    location: eLocation.value.trim(),
    description: eDescription.value.trim(),
    imageUrl: eImageUrl.value.trim(),
    sourceUrl: eSourceUrl.value.trim(),
    archived: eArchived.checked
  };
  const id = eId.value.trim();
  const url = id ? `/api/member/events/${id}` : "/api/member/events";
  const method = id ? "PUT" : "POST";
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) return alert("Termin konnte nicht gespeichert werden");
  resetEventForm();
  await refreshEvents();
});

resetEventBtn.addEventListener("click", resetEventForm);

uploadEventImageBtn.addEventListener("click", () =>
  handleImageUpload({
    fileInput: eImageFile,
    targetInput: eImageUrl,
    statusEl: eventUploadStatus,
    target: "event"
  })
);

questionList.addEventListener("click", async (event) => {
  const btn = event.target.closest("button[data-action]");
  if (!btn) return;
  const id = btn.dataset.id;
  if (btn.dataset.action === "edit-q") {
    const row = cache.questions.find((q) => q.id === id);
    if (!row) return;
    qId.value = row.id;
    qText.value = row.text || "";
    qDate.value = row.createdAt ? String(row.createdAt).slice(0, 10) : "";
    qLocation.value = row.location || "";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  if (btn.dataset.action === "del-q") {
    if (!confirm("Frage löschen?")) return;
    await fetch(`/api/member/questions/${id}`, { method: "DELETE" });
    await refreshQuestions();
  }
});

initiativeList.addEventListener("click", async (event) => {
  const btn = event.target.closest("button[data-action]");
  if (!btn) return;
  const id = btn.dataset.id;
  if (btn.dataset.action === "edit-i") {
    const row = cache.initiatives.find((i) => i.id === id);
    if (!row) return;
    iId.value = row.id;
    iTitle.value = row.title || "";
    iStatus.value = row.status || "";
    iDescription.value = row.description || "";
    iImageUrl.value = row.imageUrl || "";
    iSourceUrl.value = row.sourceUrl || "";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  if (btn.dataset.action === "del-i") {
    if (!confirm("Initiative löschen?")) return;
    await fetch(`/api/member/initiatives/${id}`, { method: "DELETE" });
    await refreshInitiatives();
  }
});

eventList.addEventListener("click", async (event) => {
  const btn = event.target.closest("button[data-action]");
  if (!btn) return;
  const id = btn.dataset.id;
  if (btn.dataset.action === "edit-e") {
    const row = cache.events.find((e) => e.id === id);
    if (!row) return;
    eId.value = row.id;
    eTitle.value = row.title || "";
    eDate.value = row.date || "";
    eLocation.value = row.location || "";
    eDescription.value = row.description || "";
    eImageUrl.value = row.imageUrl || "";
    eSourceUrl.value = row.sourceUrl || "";
    eArchived.checked = Boolean(row.archived);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  if (btn.dataset.action === "del-e") {
    if (!confirm("Termin löschen?")) return;
    await fetch(`/api/member/events/${id}`, { method: "DELETE" });
    await refreshEvents();
  }
});

async function loadProfile() {
  const res = await fetch("/api/member/profile");
  if (!res.ok) return;
  const profile = await res.json();
  roleInput.value = profile.role || "";
  portraitUrlInput.value = profile.portraitUrl || "";
  linksInput.value = Array.isArray(profile.links) ? profile.links.join("\n") : "";
  bioInput.value = profile.bio || "";
}

async function refreshQuestions() {
  const res = await fetch("/api/member/questions");
  if (!res.ok) return;
  cache.questions = await res.json();
  questionList.innerHTML = cache.questions
    .map((q) => {
      const d = q.createdAt ? String(q.createdAt).slice(0, 10) : "";
      const where = q.location ? ` · ${escapeHtml(q.location)}` : "";
      return `<article class="card"><h3>${escapeHtml(q.text || "")}</h3><p class="muted">${escapeHtml(d)}${where}</p><div class="actions"><button class="secondary" data-action="edit-q" data-id="${q.id}">Bearbeiten</button><button class="secondary" data-action="del-q" data-id="${q.id}">Löschen</button></div></article>`;
    })
    .join("");
}

async function refreshInitiatives() {
  const res = await fetch("/api/member/initiatives");
  if (!res.ok) return;
  cache.initiatives = await res.json();
  initiativeList.innerHTML = cache.initiatives
    .map((i) => {
      const image = i.imageUrl
        ? `<p><a class="member-link" target="_blank" rel="noopener noreferrer" href="${escapeHtml(i.imageUrl)}">Bild</a></p>`
        : "";
      return `<article class="card"><h3>${escapeHtml(i.title || "")}</h3><p class="muted">${escapeHtml(i.status || "")}</p><p>${escapeHtml(i.description || "")}</p>${image}<div class="actions"><button class="secondary" data-action="edit-i" data-id="${i.id}">Bearbeiten</button><button class="secondary" data-action="del-i" data-id="${i.id}">Löschen</button></div></article>`;
    })
    .join("");
}

async function refreshEvents() {
  const res = await fetch("/api/member/events");
  if (!res.ok) return;
  cache.events = await res.json();
  eventList.innerHTML = cache.events
    .map((e) => {
      const image = e.imageUrl
        ? `<p><a class="member-link" target="_blank" rel="noopener noreferrer" href="${escapeHtml(e.imageUrl)}">Bild</a></p>`
        : "";
      return `<article class="card"><h3>${escapeHtml(e.title || "")}</h3><p class="muted">${escapeHtml(e.date || "")} - ${escapeHtml(e.location || "")}</p><p>${escapeHtml(e.description || "")}</p>${image}<div class="actions"><button class="secondary" data-action="edit-e" data-id="${e.id}">Bearbeiten</button><button class="secondary" data-action="del-e" data-id="${e.id}">Löschen</button></div></article>`;
    })
    .join("");
}

function resetQuestionForm() {
  qId.value = "";
  qText.value = "";
  qDate.value = "";
  qLocation.value = "";
}

function resetInitiativeForm() {
  iId.value = "";
  iTitle.value = "";
  iStatus.value = "aktiv";
  iDescription.value = "";
  iImageUrl.value = "";
  iSourceUrl.value = "";
  if (iImageFile) iImageFile.value = "";
  setUploadStatus(initiativeUploadStatus, "");
}

function resetEventForm() {
  eId.value = "";
  eTitle.value = "";
  eDate.value = "";
  eLocation.value = "";
  eDescription.value = "";
  eImageUrl.value = "";
  eSourceUrl.value = "";
  eArchived.checked = false;
  if (eImageFile) eImageFile.value = "";
  setUploadStatus(eventUploadStatus, "");
}

async function handleImageUpload({ fileInput, targetInput, statusEl, target }) {
  const file = fileInput && fileInput.files ? fileInput.files[0] : null;
  if (!file) {
    setUploadStatus(statusEl, "Bitte zuerst eine Bilddatei wählen.", true);
    return;
  }
  if (!file.type || !file.type.startsWith("image/")) {
    setUploadStatus(statusEl, "Nur Bilddateien sind erlaubt.", true);
    return;
  }

  try {
    setUploadStatus(statusEl, "Upload läuft …");
    const dataBase64 = await fileToBase64(file);
    const res = await fetch("/api/member/uploads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: file.name,
        contentType: file.type,
        dataBase64,
        target
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(String(err.error || "Upload fehlgeschlagen"));
    }
    const payload = await res.json();
    targetInput.value = String(payload.url || "").trim();
    setUploadStatus(statusEl, "Bild hochgeladen.");
    fileInput.value = "";
  } catch (error) {
    setUploadStatus(statusEl, String(error.message || "Upload fehlgeschlagen"), true);
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || "");
      const encoded = result.includes(",") ? result.split(",").pop() : result;
      resolve(encoded || "");
    };
    reader.onerror = () => reject(new Error("Datei konnte nicht gelesen werden"));
    reader.readAsDataURL(file);
  });
}

function setUploadStatus(el, message, isError = false) {
  if (!el) return;
  el.textContent = String(message || "");
  el.style.color = isError ? "#b42318" : "";
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

function parseLines(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}
