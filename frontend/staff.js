const $ = (id) => document.getElementById(id);
let snapshot = null;
let desk = 1;
try { desk = Number(localStorage.getItem("dawrek.desk")) || 1; } catch {}

$("desk").innerHTML = [1, 2, 3, 4, 5, 6].map((n) => `<option value="${n}">${n}</option>`).join("");
$("desk").value = desk;
$("desk").addEventListener("change", (e) => {
  desk = Number(e.target.value);
  try { localStorage.setItem("dawrek.desk", desk); } catch {}
  render();
});

function render() {
  if (!snapshot) return;
  const s = snapshot.stats;
  $("k-waiting").textContent = s.waiting;
  $("k-served").textContent = s.served;
  $("k-avg").textContent = `${s.avg_wait_minutes} ${Lang.t("minutes")}`;
  $("k-noshow").textContent = s.no_shows;

  $("board").innerHTML = snapshot.services.map((svc) => {
    const [name, desc] = Lang.t("services")[svc.key];
    const serving = svc.serving.map((t) => `
      <div class="serving-row">
        <span class="ticket-no">${t.number}</span>
        <span class="who">${esc(t.name)} · ${Lang.t("desk")} ${t.desk}</span>
        <button class="btn btn-soft" data-act="recall" data-id="${t.id}">🔔</button>
        <button class="btn btn-soft" data-act="no-show" data-id="${t.id}">${Lang.t("absent")}</button>
        <button class="btn btn-primary" data-act="done" data-id="${t.id}">✓ ${Lang.t("done")}</button>
      </div>`).join("");
    const waiting = svc.waiting.slice(0, 12).map((t, i) =>
      `<span class="qchip ${i === 0 ? "mine" : ""}" title="${esc(t.name)}">${t.number}${t.no_shows ? ' <span class="ns">↺</span>' : ""}</span>`).join("")
      + (svc.waiting.length > 12 ? `<span class="qchip">+${svc.waiting.length - 12}</span>` : "");
    return `<article class="card svc">
      <div class="svc-head">
        <span class="service-icon">${SERVICE_ICONS[svc.key]}</span>
        <div><b>${esc(name)}</b><small>${svc.prefix} · ${esc(desc)}</small></div>
        <div class="count"><b>${svc.waiting_count}</b><br><small>~${svc.eta_minutes} ${Lang.t("minutes")}</small></div>
      </div>
      ${serving}
      <div class="queue-chips">${waiting || `<span class="empty">${Lang.t("nobodyWaiting")}</span>`}</div>
      <button class="btn btn-primary btn-block" data-act="call" data-service="${svc.key}" ${svc.waiting_count ? "" : "disabled"}>
        📣 ${Lang.t("callNext")}</button>
    </article>`;
  }).join("");
}

async function refresh() {
  try { snapshot = await api("/api/queue"); render(); } catch {}
}

$("board").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-act]");
  if (!b) return;
  b.disabled = true;
  try {
    if (b.dataset.act === "call") await api("/api/staff/call", { method: "POST", body: { service: b.dataset.service, desk } });
    else await api(`/api/staff/tickets/${b.dataset.id}/${b.dataset.act}`, { method: "POST" });
  } finally { refresh(); }
});

$("demo").addEventListener("click", async () => { await api("/api/staff/demo", { method: "POST" }); refresh(); });
$("reset").addEventListener("click", async () => {
  if (!confirm(Lang.t("confirmReset"))) return;
  await api("/api/staff/reset", { method: "POST" });
  refresh();
});

Lang.key = "dawrek.lang.staff";
Lang.current = "fr";
Lang.init(render);
Lang.renderSwitch($("lang"));
refresh();
setInterval(refresh, 1500);
