const $ = (id) => document.getElementById(id);

// Strings only this staff page needs.
const SETTINGS_TEXT = {
  tn: {
    setTempNote: "في الاستضافة المجانية، الإعدادات تتفسخ كي يعاود السيرفر يخدم. بعد كل تبديل، اضغط «نزّل نسخة».",
    setClinic: "العيادة", setClinicName: "إسم العيادة", setClinicNameHint: "مثال: مستوصف المنزه",
    setClinicNameHelp: "يبان للمرضى والمساعد يستعملو.", setDesks: "عدد الشبابيك", setDesksHelp: "بين 1 و 20.",
    setServices: "الخدمات", setServicesHelp: "سكّر خدمة باش ما يقصّولهاش تيكيات. الوقت لكل مريض يتبدّل وحدو كي يكون فما زيارات حقيقية اليوم.",
    setOpen: "محلولة", setMinutes: "دق لكل مريض", setToday: "اليوم",
    setKnowledge: "معلومات المساعد", setKnowledgeHelp: "المساعد يجاوب من هالنصوص برك. اكتب كل موضوع بالثلاث لغات.",
    topics: { appointments: "المواعيد", documents_required: "الوراق", queue_general: "الطابور", services: "الخدمات", wait_times: "أوقات الانتظار" },
    kbLangs: { tn: "تونسي", ar: "عربي فصحى", fr: "فرنسي" },
    setSave: "سجّل", setSaved: "تسجّل ✓", setUnsaved: "فما تبديلات ما تسجّلتش", setError: "ما تسجّلش:",
    setExport: "نزّل نسخة", setImport: "رجّع نسخة", setDefaults: "رجّع الإعدادات الأصلية",
    setConfirmDefaults: "ترجّع الإعدادات الأصلية؟ التبديلات متاعك يتفسخو.", setImported: "النسخة رجعت ✓",
  },
  ar: {
    setTempNote: "في الاستضافة المجانية تُحذف الإعدادات عند إعادة تشغيل الخادم. بعد كل تعديل، اضغط «تنزيل نسخة».",
    setClinic: "العيادة", setClinicName: "اسم العيادة", setClinicNameHint: "مثال: مستوصف المنزه",
    setClinicNameHelp: "يظهر للمرضى ويستعمله المساعد.", setDesks: "عدد الشبابيك", setDesksHelp: "بين 1 و20.",
    setServices: "الخدمات", setServicesHelp: "أغلق خدمة لإيقاف التذاكر. يتعدّل الوقت لكل مريض تلقائياً حسب الزيارات الفعلية اليوم.",
    setOpen: "مفتوحة", setMinutes: "دقائق لكل مريض", setToday: "اليوم",
    setKnowledge: "معلومات المساعد", setKnowledgeHelp: "يجيب المساعد من هذه النصوص فقط. اكتب كل موضوع باللغات الثلاث.",
    topics: { appointments: "المواعيد", documents_required: "الوثائق", queue_general: "الطابور", services: "الخدمات", wait_times: "أوقات الانتظار" },
    kbLangs: { tn: "تونسي", ar: "عربية فصحى", fr: "فرنسية" },
    setSave: "حفظ", setSaved: "تم الحفظ ✓", setUnsaved: "تعديلات غير محفوظة", setError: "تعذّر الحفظ:",
    setExport: "تنزيل نسخة", setImport: "استعادة نسخة", setDefaults: "استعادة الإعدادات الأصلية",
    setConfirmDefaults: "استعادة الإعدادات الأصلية؟ ستُحذف تعديلاتك.", setImported: "تمت استعادة النسخة ✓",
  },
  fr: {
    setTempNote: "Sur l'hébergement gratuit, les réglages sont perdus au redémarrage du serveur. Après chaque changement, cliquez sur « Télécharger une copie ».",
    setClinic: "Clinique", setClinicName: "Nom de la clinique", setClinicNameHint: "ex. Clinique El Menzah",
    setClinicNameHelp: "Affiché aux patients et utilisé par l'assistant.", setDesks: "Nombre de guichets", setDesksHelp: "Entre 1 et 20.",
    setServices: "Services", setServicesHelp: "Fermez un service pour arrêter les tickets. Le temps par patient s'ajuste tout seul avec les vraies visites du jour.",
    setOpen: "Ouvert", setMinutes: "min par patient", setToday: "Aujourd'hui",
    setKnowledge: "Connaissances de l'assistant", setKnowledgeHelp: "L'assistant répond uniquement à partir de ces textes. Écrivez chaque sujet dans les trois langues.",
    topics: { appointments: "Rendez-vous", documents_required: "Documents", queue_general: "File d'attente", services: "Services", wait_times: "Temps d'attente" },
    kbLangs: { tn: "Tunisien", ar: "Arabe standard", fr: "Français" },
    setSave: "Enregistrer", setSaved: "Enregistré ✓", setUnsaved: "Modifications non enregistrées", setError: "Échec de l'enregistrement :",
    setExport: "Télécharger une copie", setImport: "Restaurer une copie", setDefaults: "Réglages d'origine",
    setConfirmDefaults: "Revenir aux réglages d'origine ? Vos changements seront perdus.", setImported: "Copie restaurée ✓",
  },
  en: {
    setTempNote: "On free hosting, settings are lost when the server restarts. After each change, click “Download backup”.",
    setClinic: "Clinic", setClinicName: "Clinic name", setClinicNameHint: "e.g. El Menzah Clinic",
    setClinicNameHelp: "Shown to patients and used by the assistant.", setDesks: "Number of desks", setDesksHelp: "Between 1 and 20.",
    setServices: "Services", setServicesHelp: "Close a service to stop new tickets. Minutes per patient adjust on their own from today's real visits.",
    setOpen: "Open", setMinutes: "min per patient", setToday: "Today",
    setKnowledge: "Assistant knowledge", setKnowledgeHelp: "The assistant answers only from these texts. Write each topic in all three languages.",
    topics: { appointments: "Appointments", documents_required: "Documents", queue_general: "Queue", services: "Services", wait_times: "Wait times" },
    kbLangs: { tn: "Tunisian", ar: "Standard Arabic", fr: "French" },
    setSave: "Save", setSaved: "Saved ✓", setUnsaved: "Unsaved changes", setError: "Couldn't save:",
    setExport: "Download backup", setImport: "Restore backup", setDefaults: "Restore defaults",
    setConfirmDefaults: "Restore the default settings? Your changes will be lost.", setImported: "Backup restored ✓",
  },
};
for (const [lang, text] of Object.entries(SETTINGS_TEXT)) Object.assign(I18N[lang], text);

let settings = null, learned = {}, topic = null, dirty = false;

function render() {
  if (!settings) return;
  $("clinic-name").value = settings.clinic_name;
  $("desks").value = settings.desks;

  $("services").innerHTML = Object.entries(settings.services).map(([key, s]) => {
    const [name, desc] = Lang.t("services")[key];
    const today = learned[key] ? `<small class="learned">${Lang.t("setToday")}: ${learned[key]} min</small>` : "";
    return `<div class="set-service ${s.enabled ? "" : "closed"}" data-key="${key}">
      <span class="service-icon">${SERVICE_ICONS[key]}</span>
      <div class="set-service-name"><b>${esc(name)}</b><small>${esc(desc)}</small></div>
      <label class="switch"><input type="checkbox" data-f="enabled" ${s.enabled ? "checked" : ""}><span>${Lang.t("setOpen")}</span></label>
      <label class="set-minutes"><input type="number" min="1" max="180" data-f="avg_minutes" value="${s.avg_minutes}"><span>${Lang.t("setMinutes")}</span>${today}</label>
    </div>`;
  }).join("");

  const topics = Object.keys(settings.knowledge);
  topic = topics.includes(topic) ? topic : topics[0];
  $("topics").innerHTML = topics.map((t) =>
    `<button type="button" class="chip ${t === topic ? "active" : ""}" data-topic="${t}">${esc(Lang.t("topics")[t] || t)}</button>`).join("");
  $("kb").innerHTML = ["tn", "ar", "fr"].map((lang) => `
    <label class="field"><span>${Lang.t("kbLangs")[lang]}</span>
      <textarea data-lang="${lang}" dir="${lang === "fr" ? "ltr" : "rtl"}" rows="9" maxlength="4000">${esc(settings.knowledge[topic][lang])}</textarea>
    </label>`).join("");
}

// Read the form back into `settings` (keeps edits when switching topic or language).
function collect() {
  settings.clinic_name = $("clinic-name").value.trim();
  settings.desks = Number($("desks").value) || 1;
  document.querySelectorAll(".set-service").forEach((row) => {
    const s = settings.services[row.dataset.key];
    s.enabled = row.querySelector('[data-f="enabled"]').checked;
    s.avg_minutes = Number(row.querySelector('[data-f="avg_minutes"]').value) || 1;
  });
  document.querySelectorAll("#kb textarea").forEach((ta) => { settings.knowledge[topic][ta.dataset.lang] = ta.value; });
  return settings;
}

function setStatus(key, extra = "", cls = "") {
  $("status").textContent = key ? `${Lang.t(key)} ${extra}`.trim() : "";
  $("status").className = `set-status ${cls}`;
}

function markDirty() { dirty = true; setStatus("setUnsaved", "", "warn"); }

async function load() {
  const [s, queue] = await Promise.all([api("/api/settings"), api("/api/queue")]);
  settings = s;
  learned = Object.fromEntries(queue.services.filter((x) => x.learned).map((x) => [x.key, x.minutes_per_patient]));
  render();
}

async function save(data, okKey = "setSaved") {
  $("save").disabled = true;
  try {
    settings = await api("/api/settings", { method: "PUT", body: data });
    dirty = false;
    render();
    setStatus(okKey, "", "ok");
  } catch (e) {
    setStatus("setError", e.detail || `HTTP ${e.status}`, "err");
  } finally { $("save").disabled = false; }
}

$("save").addEventListener("click", () => save(collect()));
document.querySelector("main").addEventListener("input", (e) => { if (e.target.matches("input, textarea") && e.target.id !== "import") markDirty(); });
$("services").addEventListener("change", (e) => {
  if (e.target.dataset.f === "enabled") e.target.closest(".set-service").classList.toggle("closed", !e.target.checked);
});
$("topics").addEventListener("click", (e) => {
  const b = e.target.closest("[data-topic]");
  if (!b) return;
  collect();
  topic = b.dataset.topic;
  render();
});

$("export").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(collect(), null, 1)], { type: "application/json" });
  const a = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(blob), download: `dawrek-settings-${new Date().toISOString().slice(0, 10)}.json`,
  });
  a.click();
  URL.revokeObjectURL(a.href);
});

$("import").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;
  try { await save(JSON.parse(await file.text()), "setImported"); }
  catch { setStatus("setError", "JSON", "err"); }
});

$("defaults").addEventListener("click", async () => {
  if (!confirm(Lang.t("setConfirmDefaults"))) return;
  settings = await api("/api/settings/reset", { method: "POST" });
  dirty = false;
  render();
  setStatus("setSaved", "", "ok");
});

window.addEventListener("beforeunload", (e) => { if (dirty) e.preventDefault(); });

Lang.key = "dawrek.lang.staff";
Lang.current = "fr";
Lang.init(() => { if (settings) { collect(); render(); } if (dirty) markDirty(); });
Lang.renderSwitch($("lang"));
load();
