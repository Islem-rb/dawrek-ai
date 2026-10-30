const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};

const state = {
  ticketId: store.get("dawrek.ticket"),
  ticket: null,
  queue: null,
  info: null,
  maxAhead: store.get("dawrek.maxAhead") || 0,
  dismissedCall: store.get("dawrek.dismissed"),
  history: [],
  busy: false,
};
const RING = 452.4;
const CLOSED = ["done", "cancelled", "missed"];

// ------------------------------------------------------------- rendering

function render() {
  const t = state.ticket;
  $("home").classList.toggle("hidden", !!t);
  $("ticket-view").classList.toggle("hidden", !t);
  if (!t) renderServices(); else renderTicket(t);
  renderAiPill();
  renderAlerts();
}

function renderServices() {
  if (!state.queue) return;
  $("services").innerHTML = state.queue.services.filter((s) => s.enabled).map((s) => {
    const [name, desc] = Lang.t("services")[s.key];
    const meta = s.waiting_count
      ? `<b>${s.waiting_count}</b>${Lang.t("waitingShort")} · ~${s.eta_minutes} ${Lang.t("minutes")}`
      : `<b>0</b>${Lang.t("noWait")}`;
    return `<button class="card service" data-service="${s.key}" ${state.busy ? "disabled" : ""}>
      <span class="service-icon">${SERVICE_ICONS[s.key]}</span>
      <span class="service-body"><b>${esc(name)}</b><small>${esc(desc)}</small></span>
      <span class="service-meta">${meta}</span></button>`;
  }).join("");
}

function renderTicket(t) {
  const closed = CLOSED.includes(t.status);
  const soon = t.status === "waiting" && t.people_ahead <= 2;
  $("t-number").textContent = t.number;
  $("t-service").textContent = `${SERVICE_ICONS[t.service]} ${serviceName(t.service)}`;
  $("ticket-card").classList.toggle("soon", soon);

  const pill = $("t-status");
  const [cls, key] = {
    waiting: soon ? ["pill-amber", "statusSoon"] : ["pill-teal", "statusWaiting"],
    called: ["pill-green", "statusCalled"],
    done: ["pill-green", "statusDone"],
    cancelled: ["pill-muted", "statusCancelled"],
    missed: ["pill-red", "statusMissed"],
  }[t.status];
  pill.className = `pill ${cls}`;
  pill.innerHTML = `${t.status === "waiting" ? '<span class="dot live"></span>' : ""}${esc(Lang.t(key))}`;
  const appt = t.status === "waiting" && t.appointment;
  $("t-appt").classList.toggle("hidden", !appt);
  $("t-appt").classList.toggle("confirmed", t.appointment === "confirmed");
  if (appt) $("t-appt").textContent = Lang.t(t.appointment === "confirmed" ? "apptConfirmed" : "apptPending");

  $("t-live").classList.toggle("hidden", closed);
  $("t-end").classList.toggle("hidden", !closed);
  $("leave").classList.toggle("hidden", closed);
  $("again").classList.toggle("hidden", !closed);

  if (closed) {
    $("t-end-text").textContent = { done: Lang.t("doneText"), missed: Lang.t("missedText"), cancelled: "" }[t.status];
  } else {
    $("t-ahead").textContent = t.people_ahead;
    $("t-eta").textContent = t.status === "called" ? "—" : `~${t.eta_minutes} ${Lang.t("minutes")}`;
    $("t-serving").textContent = t.now_serving.join(" · ") || "—";
    state.maxAhead = Math.max(state.maxAhead, t.people_ahead);
    store.set("dawrek.maxAhead", state.maxAhead);
    const progress = t.status === "called" ? 1 : state.maxAhead ? 1 - t.people_ahead / (state.maxAhead + 1) : 0.9;
    $("ring").style.strokeDashoffset = RING * (1 - progress);
    $("t-noshow").classList.toggle("hidden", !(t.no_shows && t.status === "waiting"));
  }

  const callKey = `${t.id}:${t.desk}:${t.no_shows}`;
  const showCall = t.status === "called" && state.dismissedCall !== callKey;
  $("called").classList.toggle("hidden", !showCall);
  $("c-number").textContent = t.number;
  $("c-desk").textContent = t.desk ?? "";
  document.title = t.status === "called" ? `🔔 ${t.number} · Dawrek` : `${t.number} · Dawrek`;
}

function renderClinic() {
  const name = state.info?.clinic_name;
  $("clinic").classList.toggle("hidden", !name);
  $("clinic").textContent = name ? `🏥 ${name}` : "";
}

function renderAiPill() {
  const on = state.info?.ai_enabled;
  $("ai-pill").className = `pill ${on ? "pill-teal" : "pill-muted"}`;
  $("ai-pill").textContent = Lang.t(on ? "aiOn" : "aiOff");
}

// ------------------------------------------------------------- live updates

async function refresh() {
  try {
    const [queue, ticket] = await Promise.all([
      api("/api/queue"),
      state.ticketId ? api(`/api/tickets/${state.ticketId}`).catch((e) => (e.status === 404 ? null : state.ticket)) : null,
    ]);
    state.queue = queue;
    if (state.ticketId && !ticket) forgetTicket();
    const prev = state.ticket;
    state.ticket = ticket;
    if (ticket && ticket.status === "called" && prev?.status !== "called") onCalled();
    render();
  } catch { /* offline for a moment: keep showing last state */ }
}

function onCalled() {
  chime();
  navigator.vibrate?.([300, 120, 300, 120, 600]);
}

function forgetTicket() {
  state.ticketId = null; state.ticket = null; state.maxAhead = 0;
  store.set("dawrek.ticket", null); store.set("dawrek.maxAhead", null);
}

// ------------------------------------------------------------- actions

$("services").addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-service]");
  if (!btn || state.busy) return;
  unlockAudio();
  state.busy = true; renderServices();
  try {
    const t = await api("/api/tickets", {
      method: "POST", body: { service: btn.dataset.service, name: $("name").value, appointment: $("appt").checked },
    });
    state.ticketId = t.id; state.ticket = t; state.maxAhead = t.people_ahead;
    store.set("dawrek.ticket", t.id); store.set("dawrek.maxAhead", t.people_ahead);
    $("appt").checked = false;
    if (pushReady() && Notification.permission === "granted") enableAlerts(); // already allowed once: no need to ask

  } finally { state.busy = false; render(); }
});

$("leave").addEventListener("click", async () => {
  if (!confirm(Lang.t("confirmLeave"))) return;
  state.ticket = await api(`/api/tickets/${state.ticketId}`, { method: "DELETE" });
  render();
});

$("again").addEventListener("click", () => { forgetTicket(); render(); });

$("c-ok").addEventListener("click", () => {
  const t = state.ticket;
  state.dismissedCall = `${t.id}:${t.desk}:${t.no_shows}`;
  store.set("dawrek.dismissed", state.dismissedCall);
  render();
});

// ------------------------------------------------------------- phone alerts

// Web Push: the server rings the phone ("almost your turn", "your turn, desk 2") even when it's locked.
// Android: any modern browser. iPhone: only once Dawrek is added to the home screen (iOS 16.4+).
const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
const isStandalone = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const pushReady = () => window.isSecureContext && "serviceWorker" in navigator && "PushManager" in window
  && "Notification" in window && !!state.info?.push_key;
const alertsOn = () => !!state.ticketId && store.get("dawrek.alerts") === state.ticketId;

function renderAlerts() {
  const t = state.ticket;
  const card = $("alerts"), btn = $("alerts-btn"), text = $("alerts-text");
  let msg = null, showBtn = false;
  if (t && t.status === "waiting") {
    if (alertsOn()) msg = "alertsOn";
    else if (pushReady() && Notification.permission === "denied") msg = "alertsDenied";
    else if (pushReady()) { msg = "alertsText"; showBtn = true; }
    else if (isIOS && !isStandalone()) msg = "alertsIos";
  }
  card.classList.toggle("hidden", !msg);
  card.classList.toggle("on", msg === "alertsOn");
  btn.classList.toggle("hidden", !showBtn);
  if (msg) text.textContent = Lang.t(msg);
}

const keyBytes = (b64) => {
  const raw = atob((b64 + "=".repeat((4 - (b64.length % 4)) % 4)).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(raw, (c) => c.charCodeAt(0));
};

async function enableAlerts() {
  const ticketId = state.ticketId;
  try {
    if (Notification.permission !== "granted" && (await Notification.requestPermission()) !== "granted") return;
    const reg = await navigator.serviceWorker.ready;
    let sub = await reg.pushManager.getSubscription();
    const key = keyBytes(state.info.push_key);
    const sameKey = sub?.options?.applicationServerKey
      && new Uint8Array(sub.options.applicationServerKey).every((b, i) => b === key[i]);
    if (sub && !sameKey) { await sub.unsubscribe(); sub = null; } // the server restarted with new keys
    sub = sub || await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
    await api(`/api/tickets/${ticketId}/push`, { method: "POST", body: { subscription: sub.toJSON(), lang: Lang.current } });
    store.set("dawrek.alerts", ticketId);
  } catch {
    $("alerts-text").textContent = Lang.t("alertsError");
    return;
  } finally {
    $("alerts-btn").disabled = false;
  }
  renderAlerts();
}

$("alerts-btn").addEventListener("click", () => { $("alerts-btn").disabled = true; unlockAudio(); enableAlerts(); });
navigator.serviceWorker?.register("/sw.js").catch(() => {});

// ------------------------------------------------------------- bigger text

function applyBigText(on) {
  document.documentElement.classList.toggle("big", on);
  $("big").setAttribute("aria-pressed", on);
}
$("big").addEventListener("click", () => {
  const on = !document.documentElement.classList.contains("big");
  store.set("dawrek.big", on);
  applyBigText(on);
});
applyBigText(!!store.get("dawrek.big"));

// ------------------------------------------------------------- chat

function addMessage(role, text, tag, lang) {
  const el = document.createElement("div");
  el.className = `msg ${role === "user" ? "me" : "bot"}`;
  el.textContent = text;
  if (tag) { const s = document.createElement("span"); s.className = "tag"; s.textContent = tag; el.append(s); }
  if (lang && canSpeak(lang)) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "speak-btn"; b.textContent = `🔊 ${Lang.t("speak")}`;
    b.addEventListener("click", () => speak(text, lang));
    (el.querySelector(".tag") || el).append(b);
  }
  $("messages").append(el);
  $("messages").scrollTop = $("messages").scrollHeight;
  return el;
}

function renderChips() {
  $("chips").innerHTML = Lang.t("suggestions").map((s) => `<button class="chip" type="button">${esc(s)}</button>`).join("");
}

function resetChat() {
  $("messages").innerHTML = "";
  state.history = [];
  addMessage("bot", Lang.t("chatHello"));
  renderChips();
}

async function send(text, { speakReply = false } = {}) {
  text = text.trim();
  if (!text) return;
  addMessage("user", text);
  $("msg").value = "";
  const typing = addMessage("bot", Lang.t("typing"));
  typing.classList.add("typing");
  try {
    const r = await api("/api/chat", { method: "POST", body: { message: text, ticket_id: state.ticketId, history: state.history } });
    typing.remove();
    const tag = { ai: `✨ ${Lang.t("aiOn")}`, offline: Lang.t("aiOff"), safety: `🛡️ ${Lang.t("safety")}` }[r.mode];
    addMessage("bot", r.reply, tag, r.lang);
    if (speakReply) speak(r.reply, r.lang);
    state.history.push({ role: "user", content: text }, { role: "assistant", content: r.reply });
    state.history = state.history.slice(-10);
  } catch (e) {
    typing.remove();
    addMessage("bot", Lang.t(e.status === 429 ? "tooMany" : "chatError"));
  }
}

// ------------------------------------------------------------- voice

// Speech in: record with MediaRecorder, transcribe with Groq Whisper on the server, then chat as usual.
// Browsers only allow the microphone on HTTPS (or localhost), so the button hides elsewhere.
const voice = { rec: null, timer: null };
const MAX_RECORD_MS = 30000;
const canRecord = () => window.isSecureContext && !!navigator.mediaDevices?.getUserMedia && "MediaRecorder" in window;

function updateMic() {
  $("mic").classList.toggle("hidden", !(state.info?.voice_enabled && canRecord()));
  $("mic").title = Lang.t("micStart");
}

function setMicState(mode) {
  const mic = $("mic"), status = $("voice-status");
  mic.classList.toggle("rec", mode === "rec");
  mic.disabled = mode === "busy";
  mic.textContent = mode === "rec" ? "■" : "🎤";
  mic.title = Lang.t(mode === "rec" ? "micStop" : "micStart");
  $("msg").disabled = mode !== "idle";
  status.classList.toggle("hidden", mode === "idle");
  status.classList.toggle("busy", mode === "busy");
  status.textContent = mode === "rec" ? `● ${Lang.t("listening")}` : mode === "busy" ? Lang.t("transcribing") : "";
}

async function toggleMic() {
  if (voice.rec) { voice.rec.stop(); return; }
  window.speechSynthesis?.cancel();
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch { addMessage("bot", Lang.t("micDenied")); return; }

  const mimeType = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"].find((t) => MediaRecorder.isTypeSupported(t));
  const rec = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  const chunks = [];
  rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
  rec.onstop = async () => {
    stream.getTracks().forEach((t) => t.stop());
    clearTimeout(voice.timer);
    voice.rec = null;
    setMicState("busy");
    const blob = new Blob(chunks, { type: (rec.mimeType || mimeType || "audio/webm").split(";")[0] });
    try {
      const { text } = await api("/api/transcribe", { method: "POST", body: blob });
      setMicState("idle");
      if (text) send(text, { speakReply: true }); else addMessage("bot", Lang.t("voiceError"));
    } catch (e) {
      setMicState("idle");
      addMessage("bot", Lang.t(e.status === 429 ? "tooMany" : "voiceError"));
    }
  };
  voice.rec = rec;
  rec.start();
  setMicState("rec");
  voice.timer = setTimeout(() => rec.state === "recording" && rec.stop(), MAX_RECORD_MS);
}

// Speech out: the browser's built-in voices (free, offline). Arabizi has no matching voice, so it's skipped.
const SPEECH_LANG = { tn: "ar", ar: "ar", fr: "fr", en: "en" };
const pickVoice = (lang) => {
  const code = SPEECH_LANG[lang];
  const voices = window.speechSynthesis?.getVoices() || [];
  return voices.find((v) => v.lang.toLowerCase() === `${code}-tn`) || voices.find((v) => v.lang.toLowerCase().startsWith(code));
};
const canSpeak = (lang) => "speechSynthesis" in window && !!SPEECH_LANG[lang];

function speak(text, lang) {
  if (!canSpeak(lang)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, ""));
  u.lang = SPEECH_LANG[lang];
  const v = pickVoice(lang);
  if (v) { u.voice = v; u.lang = v.lang; }
  speechSynthesis.speak(u);
}
window.speechSynthesis?.getVoices(); // voices load lazily in Chrome

function openChat(open) {
  if (!open && voice.rec) voice.rec.stop();
  $("chat").classList.toggle("hidden", !open);
  $("backdrop").classList.toggle("hidden", !open);
  $("open-chat").classList.toggle("hidden", open);
  if (open) setTimeout(() => $("msg").focus(), 50);
}

$("open-chat").addEventListener("click", () => { unlockAudio(); openChat(true); });
$("mic").addEventListener("click", toggleMic);
$("close-chat").addEventListener("click", () => openChat(false));
$("backdrop").addEventListener("click", () => openChat(false));
$("composer").addEventListener("submit", (e) => { e.preventDefault(); send($("msg").value); });
$("chips").addEventListener("click", (e) => { const c = e.target.closest(".chip"); if (c) send(c.textContent); });

// ------------------------------------------------------------- boot

Lang.init(() => {
  render(); resetChat(); updateMic();
  if (alertsOn()) enableAlerts(); // alerts follow the new language
});
Lang.renderSwitch($("lang"));
resetChat();
api("/api/info").then((info) => { state.info = info; renderAiPill(); renderClinic(); renderAlerts(); updateMic(); }).catch(() => {});
refresh();
setInterval(refresh, 2000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
