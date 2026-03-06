const identityInput = document.getElementById("identity");
const secretInput = document.getElementById("secret");
const requestBtn = document.getElementById("requestBtn");
const loginBtn = document.getElementById("loginBtn");
const loginMsg = document.getElementById("loginMsg");

init();

requestBtn.addEventListener("click", async () => {
  loginMsg.textContent = "";
  const email = String(identityInput.value || "").trim();
  if (!email || !email.includes("@")) {
    loginMsg.textContent = "Bitte E-Mail eingeben.";
    return;
  }

  const res = await fetch("/api/member/auth/request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });
  if (!res.ok) {
    loginMsg.textContent = "Link konnte nicht gesendet werden.";
    return;
  }
  const data = await res.json();
  loginMsg.textContent = data.previewUrl
    ? `Link erzeugt (Outbox): ${data.previewUrl}`
    : "Wenn eine passende Adresse hinterlegt ist, wurde ein Link versendet.";
});

loginBtn.addEventListener("click", async () => {
  await loginWithSecret(false);
});

secretInput.addEventListener("keydown", async (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  await loginWithSecret(false);
});

async function init() {
  const urlToken = String(new URLSearchParams(window.location.search).get("token") || "").trim();
  await redirectIfAlreadyLoggedIn();
  if (!urlToken) return;
  secretInput.value = urlToken;
  await loginWithSecret(true);
}

async function redirectIfAlreadyLoggedIn() {
  const memberRes = await fetch("/api/member/auth/me");
  if (memberRes.ok) {
    window.location.href = "/member-area.html";
    return true;
  }
  const editorRes = await fetch("/api/auth/me");
  if (editorRes.ok) {
    window.location.href = "/admin.html";
    return true;
  }
  return false;
}

async function loginWithSecret(silent) {
  const identity = String(identityInput.value || "").trim();
  const secret = String(secretInput.value || "").trim();
  if (!secret) {
    if (!silent) loginMsg.textContent = "Bitte Code oder Passwort eingeben.";
    return;
  }

  loginMsg.textContent = silent ? "Anmeldung läuft..." : "";

  const memberOk = await tryMemberToken(secret);
  if (memberOk) {
    window.location.href = "/member-area.html";
    return;
  }

  if (identity) {
    const editorOk = await tryEditorLogin(identity, secret);
    if (editorOk) {
      window.location.href = "/admin.html";
      return;
    }
  }

  if (!silent) {
    loginMsg.textContent = "Anmeldung fehlgeschlagen. Bitte Daten prüfen.";
  }
}

async function tryMemberToken(token) {
  const res = await fetch("/api/member/auth/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token })
  });
  return res.ok;
}

async function tryEditorLogin(username, password) {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  return res.ok;
}
