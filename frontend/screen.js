// Waiting-room display: always bilingual (Arabic + French), like real Tunisian signage.
const $ = (id) => document.getElementById(id);
let lastSeq = null;
let soundOn = false;

const label = (key) => `${I18N.ar.services[key][0]}<span class="bilingual">${I18N.fr.services[key][0]}</span>`;

function render(snap, flashId) {
  $("now").innerHTML = snap.services.map((svc) => {
    const current = svc.serving[svc.serving.length - 1];
    const latest = snap.recent_calls.find((c) => c.service === svc.key && c.status === "called") || current;
    return `<article class="card now ${latest ? "" : "idle"} ${latest && latest.id === flashId ? "flash" : ""}">
      <div class="lbl">${SERVICE_ICONS[svc.key]} ${label(svc.key)}</div>
      <div class="num ticket-no">${latest ? latest.number : "—"}</div>
      <div class="desk">${latest ? `الشباك ${latest.desk} · Guichet ${latest.desk}` : "&nbsp;"}</div>
      <small class="bilingual">${svc.waiting_count} في الانتظار · en attente</small>
    </article>`;
  }).join("");

  $("recent").innerHTML = snap.recent_calls.map((c) =>
    `<li><span class="ticket-no">${c.number}</span><span>${c.desk ? `Guichet ${c.desk}` : c.status}</span></li>`).join("");
}

function announce(call) {
  chime();
  if (!("speechSynthesis" in window)) return;
  const spoken = call.number.replace("-", " ").replace(/\b0+(?=\d)/, ""); // "C-007" -> "C 7"
  const lines = [
    { lang: "fr-FR", text: `Numéro ${spoken}, guichet ${call.desk}` },
    { lang: "ar", text: `الرقم ${spoken}، الشباك ${call.desk}` },
  ];
  const voices = speechSynthesis.getVoices();
  setTimeout(() => lines.forEach(({ lang, text }) => {
    const voice = voices.find((v) => v.lang.toLowerCase().startsWith(lang.slice(0, 2)));
    if (!voice && lang === "ar") return; // no Arabic voice installed: French only
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang; if (voice) u.voice = voice; u.rate = 0.95;
    speechSynthesis.speak(u);
  }), 700);
}

async function refresh() {
  try {
    const snap = await api("/api/queue");
    const top = snap.recent_calls[0];
    const isNew = lastSeq !== null && snap.call_seq > lastSeq && top;
    if (isNew && soundOn) announce(top);
    lastSeq = snap.call_seq;
    render(snap, isNew ? top.id : null);
  } catch {}
}

async function showQr() {
  let url = location.origin;
  try {
    const info = await api("/api/info");
    if (["localhost", "127.0.0.1"].includes(location.hostname)) url = info.lan_url; // phones can't open "localhost"
  } catch {}
  $("url").textContent = url;
  if (window.QRCode) new QRCode($("qr"), { text: url, width: 200, height: 200, correctLevel: QRCode.CorrectLevel.M });
  else $("qr").classList.add("hidden");
}

$("sound").addEventListener("click", () => {
  unlockAudio(); chime();
  soundOn = !soundOn;
  speechSynthesis?.getVoices();
  $("sound").textContent = soundOn ? "🔊 الصوت مفعّل · Son activé" : "🔈 تفعيل الصوت · Activer le son";
});

setInterval(() => {
  $("clock").textContent = new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}, 1000);
showQr();
refresh();
setInterval(refresh, 1500);
