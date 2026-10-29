const $ = (id) => document.getElementById(id);

Object.entries({
  tn: {
    insTitle: "إحصائيات", insSub: "شنوة صار في الطابور، وشنوة يسألو المرضى.",
    simulateDay: "حاكي نهار كامل", clearSim: "نحّي المحاكاة", sourceLive: "معطيات لايف", sourceSim: "فيها نهار محاكى ({date})",
    emptyTitle: "مازال ما فما معطيات", emptyText: "خوذ تيكيتات وإسأل دورك، ولا حاكي نهار كامل في كلينيك.",
    kPatients: "مرضى", kAvgWait: "معدل الانتظار", kAvgService: "معدل الخدمة", kNoShow: "غيابات", kQuestions: "أسئلة للمساعد", kDarija: "بالتونسي",
    chartHours: "الوصول حسب الساعة", chartHoursSub: "قداش من مريض وصل", chartServices: "معدل الانتظار حسب الخدمة",
    chartLanguages: "باش يكتبو المرضى", chartTopics: "على شنوة يسألو", showTable: "جدول", showChart: "رسم",
    arrivals: "وصلو", avgWaitShort: "معدل الانتظار", peak: "الذروة", questionsUnit: "سؤال", recsTitle: "اقتراحات", noRecs: "زيد معطيات باش نعطيك اقتراحات.",
    langs: { tn: "تونسي", arabizi: "تونسي بالحروف اللاتينية", ar: "عربي فصيح", fr: "فرنسي", en: "إنجليزي" },
    topics: { position: "دوري في الطابور", documents_required: "الوراق", wait_times: "وقت الانتظار", appointments: "المواعيد", services: "الخدمات", queue_general: "كيفاش يخدم الطابور", emergency: "حالات عاجلة" },
    recs: {
      add_desk: "أكثر ساعة فيها زحمة {hour}:00 ({arrivals} مريض). {service} يستناو {wait} دق في المعدل: حلّ شباك زايد في الذروة.",
      no_shows: "{rate}% من المرضى فاتهم الدور. تنبيه «ارجع بعد 20 دقيقة» ينقّص هالرقم.",
      top_question: "{share}% من الأسئلة على {topic}. علّق الجواب في الدخلة وزيدو في التيكيت.",
      darija: "{share}% من الأسئلة بالتونسي ({arabizi}% بالحروف اللاتينية). أداة بالفرنسي برك كانت تخسرهم.",
      emergency: "{count} مرضى عندهم أعراض عاجلة تبعثو طول للطوارئ بفضل الحماية.",
    },
  },
  ar: {
    insTitle: "الإحصائيات", insSub: "ماذا حدث في الطابور، وعمّ يسأل المرضى.",
    simulateDay: "محاكاة يوم كامل", clearSim: "إزالة المحاكاة", sourceLive: "بيانات مباشرة", sourceSim: "يتضمن يوماً محاكى ({date})",
    emptyTitle: "لا توجد بيانات بعد", emptyText: "خذ بعض التذاكر واسأل المساعد، أو حاكِ يوماً كاملاً في عيادة.",
    kPatients: "المرضى", kAvgWait: "متوسط الانتظار", kAvgService: "متوسط الخدمة", kNoShow: "الغيابات", kQuestions: "أسئلة للمساعد", kDarija: "بالدارجة",
    chartHours: "الوصول حسب الساعة", chartHoursSub: "عدد المرضى الواصلين", chartServices: "متوسط الانتظار حسب الخدمة",
    chartLanguages: "اللغات التي يكتب بها المرضى", chartTopics: "عمّ يسأل المرضى", showTable: "جدول", showChart: "رسم",
    arrivals: "وصول", avgWaitShort: "متوسط الانتظار", peak: "الذروة", questionsUnit: "سؤال", recsTitle: "توصيات", noRecs: "أضف بيانات للحصول على توصيات.",
    langs: { tn: "الدارجة التونسية", arabizi: "الدارجة بحروف لاتينية", ar: "العربية الفصحى", fr: "الفرنسية", en: "الإنجليزية" },
    topics: { position: "الدور في الطابور", documents_required: "الوثائق", wait_times: "مدة الانتظار", appointments: "المواعيد", services: "الخدمات", queue_general: "طريقة عمل الطابور", emergency: "حالات طارئة" },
    recs: {
      add_desk: "أكثر الساعات ازدحاماً {hour}:00 ({arrivals} مريضاً). ينتظر مرضى {service} {wait} دقيقة في المتوسط: افتح شباكاً إضافياً في الذروة.",
      no_shows: "{rate}% من المرضى فاتهم دورهم. تنبيه «عُد بعد 20 دقيقة» سيقلل ذلك.",
      top_question: "{share}% من الأسئلة عن {topic}. اعرض الإجابة عند المدخل وعلى التذكرة.",
      darija: "{share}% من الأسئلة بالدارجة التونسية ({arabizi}% بحروف لاتينية). أداة بالفرنسية فقط كانت ستفقدهم.",
      emergency: "تم توجيه {count} مرضى ذوي أعراض طارئة مباشرة إلى الطوارئ بفضل آلية الحماية.",
    },
  },
  fr: {
    insTitle: "Insights", insSub: "Ce qui s'est passé dans la file, et ce que demandent les patients.",
    simulateDay: "Simuler une journée", clearSim: "Retirer la simulation", sourceLive: "Données en direct", sourceSim: "Inclut une journée simulée ({date})",
    emptyTitle: "Pas encore de données", emptyText: "Prenez quelques tickets et posez des questions à Dawrek, ou simulez une journée complète de clinique.",
    kPatients: "Patients", kAvgWait: "Attente moyenne", kAvgService: "Durée de service", kNoShow: "Absences", kQuestions: "Questions à l'IA", kDarija: "En tounsi",
    chartHours: "Arrivées par heure", chartHoursSub: "patients arrivés", chartServices: "Attente moyenne par service",
    chartLanguages: "Langues utilisées par les patients", chartTopics: "Ce que demandent les patients", showTable: "Tableau", showChart: "Graphique",
    arrivals: "arrivées", avgWaitShort: "attente moy.", peak: "Pic", questionsUnit: "questions", recsTitle: "Recommandations", noRecs: "Ajoutez des données pour obtenir des recommandations.",
    langs: { tn: "Tounsi (arabe)", arabizi: "Tounsi (arabizi)", ar: "Arabe standard", fr: "Français", en: "Anglais" },
    topics: { position: "Ma place dans la file", documents_required: "Documents", wait_times: "Temps d'attente", appointments: "Rendez-vous", services: "Services", queue_general: "Fonctionnement", emergency: "Urgences" },
    recs: {
      add_desk: "L'heure la plus chargée est {hour}h ({arrivals} arrivées). {service} attend {wait} min en moyenne : ouvrez un guichet de plus aux heures de pointe.",
      no_shows: "{rate}% des patients ont manqué leur appel. Des alertes « revenez dans 20 min » réduiraient ce chiffre.",
      top_question: "{share}% des questions portent sur : {topic}. Affichez la réponse à l'entrée et sur le ticket.",
      darija: "{share}% des questions étaient en tounsi ({arabizi}% en arabizi). Un outil uniquement en français les aurait perdues.",
      emergency: "{count} patients avec des symptômes urgents ont été orientés directement vers les urgences par le garde-fou.",
    },
  },
  en: {
    insTitle: "Insights", insSub: "What happened in the queue, and what patients ask.",
    simulateDay: "Simulate a day", clearSim: "Remove simulation", sourceLive: "Live data", sourceSim: "Includes a simulated day ({date})",
    emptyTitle: "No data yet", emptyText: "Take a few tickets and ask Dawrek some questions, or simulate a full clinic day.",
    kPatients: "Patients", kAvgWait: "Avg. wait", kAvgService: "Avg. service", kNoShow: "No-shows", kQuestions: "AI questions", kDarija: "In Tunisian",
    chartHours: "Arrivals by hour", chartHoursSub: "patients arriving", chartServices: "Average wait by service",
    chartLanguages: "Languages patients write in", chartTopics: "What patients ask", showTable: "Table", showChart: "Chart",
    arrivals: "arrivals", avgWaitShort: "avg. wait", peak: "Peak", questionsUnit: "questions", recsTitle: "Recommendations", noRecs: "Add more data to get recommendations.",
    langs: { tn: "Tunisian (Arabic script)", arabizi: "Tunisian (Arabizi)", ar: "Standard Arabic", fr: "French", en: "English" },
    topics: { position: "My place in line", documents_required: "Documents", wait_times: "Wait times", appointments: "Appointments", services: "Services", queue_general: "How it works", emergency: "Emergencies" },
    recs: {
      add_desk: "The busiest hour is {hour}:00 ({arrivals} arrivals). {service} waits {wait} min on average: open one more desk at peak hours.",
      no_shows: "{rate}% of patients missed their call. 'Come back in 20 min' alerts would cut this.",
      top_question: "{share}% of questions are about {topic}. Show the answer at the entrance and on the ticket.",
      darija: "{share}% of questions were in Tunisian ({arabizi}% in Arabizi). A French-only tool would have missed them.",
      emergency: "{count} patients with urgent symptoms were sent straight to emergency by the safety guardrail.",
    },
  },
}).forEach(([lang, strings]) => Object.assign(I18N[lang], strings));

const REC_ICONS = { add_desk: "🪑", no_shows: "🔔", top_question: "📄", darija: "🗣️", emergency: "🛡️" };
const tableMode = {};
let data = null;

// ------------------------------------------------------------- chart builders

const fill = (template, values) => template.replace(/\{(\w+)\}/g, (_, k) => values[k] ?? "");
const min = (v) => `${v} ${Lang.t("minutes")}`;

function hoursChart(rows) {
  const max = Math.max(1, ...rows.map((r) => r.arrivals));
  const peak = Math.max(...rows.map((r) => r.arrivals));
  const cols = rows.map((r) => {
    const tip = `${r.arrivals} ${Lang.t("arrivals")}|${r.hour}:00–${r.hour + 1}:00 · ${Lang.t("avgWaitShort")} ${min(r.avg_wait)}`;
    const label = r.arrivals && r.arrivals === peak ? `<span class="peak" style="bottom:calc(${(r.arrivals / max) * 100}% + 4px)">${Lang.t("peak")} · ${r.arrivals}</span>` : "";
    return `<div class="col" tabindex="0" data-tip="${esc(tip)}">${label}<div class="bar" style="height:${(r.arrivals / max) * 100}%"></div></div>`;
  }).join("");
  const labels = rows.map((r) => `<span>${r.hour}h</span>`).join("");
  return `<div dir="ltr"><div class="cols">${cols}</div><div class="col-labels">${labels}</div></div>`;
}

function hbars(rows) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return `<div class="hbars">${rows.map((r) => `
    <div class="hbar" tabindex="0" data-tip="${esc(`${r.display}|${r.name}${r.extra ? ` · ${r.extra}` : ""}`)}">
      <span class="name" title="${esc(r.name)}">${esc(r.name)}</span>
      <div class="track"><div class="fill" style="width:${(r.value / max) * 100}%"></div></div>
      <span class="val">${esc(r.display)}</span>
    </div>`).join("")}</div>`;
}

function table(headers, rows) {
  return `<table class="data-table"><thead><tr>${headers.map((h, i) => `<th class="${i ? "num" : ""}">${esc(h)}</th>`).join("")}</tr></thead>
    <tbody>${rows.map((r) => `<tr>${r.map((c, i) => `<td class="${i ? "num" : ""}">${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function shareRows(counts, names) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  return Object.entries(counts)
    .map(([k, v]) => ({ name: names[k], value: v, display: `${Math.round((100 * v) / total)}%`, extra: `${v} ${Lang.t("questionsUnit")}` }))
    .sort((a, b) => b.value - a.value);
}

const CHARTS = {
  hours: {
    chart: (d) => hoursChart(d.by_hour),
    table: (d) => table(["", Lang.t("arrivals"), Lang.t("avgWaitShort")], d.by_hour.map((r) => [`${r.hour}:00`, r.arrivals, min(r.avg_wait)])),
  },
  services: {
    rows: (d) => d.by_service.map((s) => ({ name: serviceName(s.service), value: s.avg_wait, display: min(s.avg_wait),
      extra: `${s.patients} ${Lang.t("kPatients").toLowerCase()} · max ${min(s.max_wait)}` })).sort((a, b) => b.value - a.value),
    table: (d) => table(["", Lang.t("kPatients"), Lang.t("avgWaitShort"), "max"],
      d.by_service.map((s) => [serviceName(s.service), s.patients, min(s.avg_wait), min(s.max_wait)])),
  },
  languages: {
    rows: (d) => shareRows(d.languages, Lang.t("langs")),
    table: (d) => table(["", Lang.t("questionsUnit"), "%"], shareRows(d.languages, Lang.t("langs")).map((r) => [r.name, r.value, r.display])),
  },
  topics: {
    rows: (d) => shareRows(d.topics, Lang.t("topics")),
    table: (d) => table(["", Lang.t("questionsUnit"), "%"], shareRows(d.topics, Lang.t("topics")).map((r) => [r.name, r.value, r.display])),
  },
};

// ------------------------------------------------------------- render

function render() {
  if (!data) return;
  const k = data.kpis, src = data.sources;
  const hasData = k.patients || k.questions;
  $("empty").classList.toggle("hidden", !!hasData);
  $("content").classList.toggle("hidden", !hasData);
  $("clear-sim").classList.toggle("hidden", !src.simulated_date);
  $("source").className = `pill ${src.simulated_date ? "pill-amber" : "pill-teal"}`;
  $("source").innerHTML = src.simulated_date
    ? `🧪 ${esc(fill(Lang.t("sourceSim"), { date: src.simulated_date }))}`
    : `<span class="dot live"></span>${esc(Lang.t("sourceLive"))}`;
  if (!hasData) return;

  const tiles = [
    ["kPatients", k.patients, ""], ["kAvgWait", k.avg_wait, Lang.t("minutes")], ["kAvgService", k.avg_service, Lang.t("minutes")],
    ["kNoShow", k.no_show_rate, "%"], ["kQuestions", k.questions, ""], ["kDarija", k.darija_share, "%"],
  ];
  $("kpis").innerHTML = tiles.map(([label, value, unit]) =>
    `<div class="card kpi"><small>${esc(Lang.t(label))}</small><b>${value}<span> ${unit}</span></b></div>`).join("");

  document.querySelectorAll("[data-chart]").forEach((card) => {
    const name = card.dataset.chart, def = CHARTS[name];
    const asTable = !!tableMode[name];
    card.querySelector(".chart-body").innerHTML = asTable ? def.table(data) : def.chart ? def.chart(data) : hbars(def.rows(data));
    card.querySelector("[data-toggle]").textContent = Lang.t(asTable ? "showChart" : "showTable");
  });

  const recs = Lang.t("recs");
  $("recs").innerHTML = data.recommendations.length
    ? data.recommendations.map((r) => {
        const values = { ...r, service: r.service && serviceName(r.service), topic: r.topic && Lang.t("topics")[r.topic] };
        return `<div class="rec"><span class="ico">${REC_ICONS[r.kind]}</span><span>${esc(fill(recs[r.kind], values))}</span></div>`;
      }).join("")
    : `<p class="empty">${esc(Lang.t("noRecs"))}</p>`;
}

async function refresh() {
  try { data = await api("/api/insights"); render(); } catch {}
}

async function simulate(method) {
  document.querySelectorAll(".chart-card").forEach((c) => c.classList.add("loading"));
  try { data = await api("/api/insights/simulate", { method }); render(); }
  finally { document.querySelectorAll(".chart-card").forEach((c) => c.classList.remove("loading")); }
}

// ------------------------------------------------------------- interaction

const tip = $("tooltip");
function showTip(el, x, y) {
  const [value, label] = el.dataset.tip.split("|");
  tip.innerHTML = `<b>${esc(value)}</b>${esc(label)}`;
  tip.classList.remove("hidden");
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = `${Math.min(window.innerWidth - w - 8, Math.max(8, x - w / 2))}px`;
  tip.style.top = `${Math.max(8, y - h - 12)}px`;
}
document.addEventListener("pointermove", (e) => {
  const el = e.target.closest("[data-tip]");
  if (el) showTip(el, e.clientX, e.clientY); else tip.classList.add("hidden");
});
document.addEventListener("focusin", (e) => {
  const el = e.target.closest("[data-tip]");
  if (!el) return tip.classList.add("hidden");
  const r = el.getBoundingClientRect();
  showTip(el, r.left + r.width / 2, r.top);
});
document.addEventListener("focusout", () => tip.classList.add("hidden"));

document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-toggle]");
  if (!t) return;
  const name = t.closest("[data-chart]").dataset.chart;
  tableMode[name] = !tableMode[name];
  render();
});
$("simulate").addEventListener("click", () => simulate("POST"));
$("simulate-2").addEventListener("click", () => simulate("POST"));
$("clear-sim").addEventListener("click", () => simulate("DELETE"));

Lang.key = "dawrek.lang.staff";
Lang.current = "fr";
Lang.init(render);
Lang.renderSwitch($("lang"));
refresh();
setInterval(refresh, 5000);
