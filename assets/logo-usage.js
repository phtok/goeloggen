(function () {
  var endpoint = String(window.GOE_LOGO_USAGE_ENDPOINT || "").trim().replace(/\/+$/, "");
  if (!endpoint || !window.JSON || !window.navigator) {
    return;
  }

  var sessionId = getSessionId();
  var sentPageview = false;
  var stateChangeTimer = null;
  var lastStateKey = "";

  function getSessionId() {
    try {
      var existing = window.sessionStorage.getItem("goe_logo_usage_session");
      if (existing) {
        return existing;
      }
      var id = createId();
      window.sessionStorage.setItem("goe_logo_usage_session", id);
      return id;
    } catch (err) {
      return createId();
    }
  }

  function createId() {
    if (window.crypto && window.crypto.randomUUID) {
      return window.crypto.randomUUID();
    }
    return String(Date.now()) + "-" + Math.random().toString(16).slice(2);
  }

  function stateSnapshot() {
    var st = window.st || {};
    var custom = document.getElementById("customtext");
    return {
      org: st.org || "",
      category: st.cat || "",
      layout: st.layout || "",
      lang: st.lang || "",
      mode: st.mode || "",
      scale: Number(st.scale || 0),
      advancedOpen: Boolean(window.adv),
      customTextLength: custom && custom.value ? custom.value.length : 0
    };
  }

  function basePayload(eventType) {
    var st = window.st || {};
    return {
      eventType: eventType,
      sessionId: sessionId,
      path: window.location.href,
      referrer: document.referrer || "",
      uiLang: st.uiLang || document.documentElement.lang || "",
      viewport: {
        width: window.innerWidth || 0,
        height: window.innerHeight || 0
      },
      logo: stateSnapshot()
    };
  }

  function send(eventType, extra) {
    var payload = basePayload(eventType);
    if (extra) {
      Object.keys(extra).forEach(function (key) {
        payload[key] = extra[key];
      });
    }

    var body = JSON.stringify(payload);
    var url = endpoint + "/collect";

    if (navigator.sendBeacon) {
      var blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon(url, blob)) {
        return;
      }
    }

    try {
      window.fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: body,
        keepalive: true,
        credentials: "omit"
      }).catch(function () {});
    } catch (err) {}
  }

  function sendPageviewOnce() {
    if (sentPageview) {
      return;
    }
    sentPageview = true;
    send("pageview");
  }

  function scheduleStateChange() {
    clearTimeout(stateChangeTimer);
    stateChangeTimer = setTimeout(function () {
      var key = JSON.stringify(stateSnapshot());
      if (key !== lastStateKey) {
        lastStateKey = key;
        send("ui_change");
      }
    }, 450);
  }

  function bindExport(id, format) {
    var el = document.getElementById(id);
    if (!el) {
      return;
    }
    el.addEventListener(
      "click",
      function () {
        send("export", { exportFormat: format });
      },
      true
    );
  }

  function bindStateChanges() {
    ["entity-pane", "options-below-preview", "preview-area"].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) {
        return;
      }
      el.addEventListener("click", scheduleStateChange, true);
      el.addEventListener("input", scheduleStateChange, true);
      el.addEventListener("change", scheduleStateChange, true);
    });
  }

  function installDashboardLink() {
    if (document.getElementById("goe-logo-stats-link")) {
      return;
    }

    var style = document.createElement("style");
    style.textContent =
      "#goe-logo-stats-link{position:fixed;right:0;bottom:0;width:34px;height:34px;z-index:9998;opacity:0;background:rgba(235,181,101,.84);border-radius:8px 0 0 0;transition:opacity .15s ease;outline:none}" +
      "#goe-logo-stats-link:hover,#goe-logo-stats-link:focus-visible{opacity:.28}" +
      "#goe-logo-stats-link:focus-visible{box-shadow:0 0 0 3px rgba(235,181,101,.38)}";
    document.head.appendChild(style);

    var link = document.createElement("a");
    link.id = "goe-logo-stats-link";
    link.href = endpoint + "/dashboard";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Statistiken");
    link.title = "Statistiken";
    document.body.appendChild(link);
  }

  function init() {
    sendPageviewOnce();
    lastStateKey = JSON.stringify(stateSnapshot());
    bindExport("exp-svg", "svg");
    bindExport("exp-svg48", "svg48");
    bindExport("exp-png", "png");
    bindExport("exp-webp", "webp");
    bindExport("exp-jpg", "jpg");
    bindExport("exp-pdf", "pdf");
    bindStateChanges();
    installDashboardLink();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
