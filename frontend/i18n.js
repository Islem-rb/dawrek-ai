// UI strings for every page. `tn` = Tunisian Darija, `ar` = Modern Standard Arabic.
const I18N = {
  tn: {
    dir: "rtl", label: "تونسي", name: "تونسي · Darija",
    tagline: "طابورك في جيبك",
    heroTitle: "ما عادش تستنى واقف",
    heroText: "خوذ تيكيت من تليفونك، تبّع دورك لايف، وإسأل دورك على أي حاجة.",
    chooseService: "اختار الخدمة",
    namePlaceholder: "إسمك (اختياري)",
    waitingShort: "يستناو", minutes: "دق", noWait: "ما فماش طابور",
    emergencyTitle: "حالة عاجلة؟", emergencyText: "ما تاخوش تيكيت. امشي طول للطوارئ ولا عيّط 190.",
    yourTicket: "التيكيت متاعك", peopleAhead: "قدامك", estWait: "الانتظار", nowServing: "توا يعدّيو",
    statusWaiting: "في الطابور", statusSoon: "قرب دورك! حضّر روحك", statusCalled: "دورك توا!",
    goToDesk: "امشي للشباك", statusDone: "يعطيك الصحة!", doneText: "سلامتك، ربي يشفيك.",
    statusCancelled: "خرجت من الطابور", statusMissed: "فاتك الدور", missedText: "عيّطولك زوز مرات وما جيتش.",
    noShowWarn: "عيّطولك وما جيتش، رجعت لآخر الطابور.",
    leaveQueue: "اخرج من الطابور", confirmLeave: "متأكد تحب تخرج من الطابور؟", newTicket: "تيكيت جديد", gotIt: "فهمت، ماشي",
    askDawrek: "إسأل دورك", chatTitle: "دورك، المساعد متاعك", chatPlaceholder: "اكتب بالتونسي، بالعربي، بالفرنسي…",
    chatHello: "عسلامة! أنا دورك 👋 إسألني على دورك في الطابور، الوراق اللي لازمك، ولا المواعيد.",
    suggestions: ["قداش باقي قدامي؟", "شنوة الوراق اللي لازمني؟", "كيفاش نلغي موعد؟"],
    aiOn: "ذكاء اصطناعي", aiOff: "وضع بدون أنترنت", safety: "سلامة", typing: "دورك يكتب…", chatError: "صار مشكل، عاود جرّب.",
    services: {
      consultation: ["استشارة عامة", "دكتور عام"], followup: ["متابعة طبية", "أمراض مزمنة"],
      lab: ["تحاليل", "أخذ عينات"], imaging: ["أشعة وإيكو", "تصوير طبي"], admin: ["خدمات إدارية", "شهادات ووراق"],
    },
    pinPrompt: "دخّل الكود السري متاع الطاقم", micStart: "احكي", micStop: "وقّف وابعث", listening: "نسمع فيك… انزل باش توقف", transcribing: "نكتب في كلامك…", micDenied: "المايكرو مسكّر. حلّو من إعدادات المتصفح.", voiceError: "ما فهمتش الصوت، عاود جرّب.", speak: "اقرا الجواب", tooMany: "برشا أسئلة، استنى شوية.",
    bigText: "كتيبة كبيرة", haveAppointment: "عندي موعد", apptHint: "الطاقم يثبّتو في الشباك. اللي عندهم موعد يتعدّاو قبل.",
    apptPending: "📅 موعدك يستنى تثبيت من الطاقم", apptConfirmed: "📅 موعدك تثبّت: تتعدّى قبل",
    alertsTitle: "خلّي تليفونك ينبّهك", alertsText: "نرنّولك كي يقرب دورك، حتى كان التليفون مسكّر.",
    alertsBtn: "شغّل التنبيهات", alertsOn: "التنبيهات شغّالة ✓ تنجم تسكّر التليفون.",
    alertsDenied: "التنبيهات مسكّرة. حلّها من إعدادات المتصفح لهالموقع.",
    alertsIos: "في الآيفون: اضغط مشاركة ← إضافة للشاشة الرئيسية، وحلّ دورك من غادي باش تخدم التنبيهات.",
    alertsError: "ما نجمناش نشغّلو التنبيهات. خلّي الصفحة محلولة.",
    apptCheck: "مواعيد للتثبيت", confirm: "ثبّت", reject: "ما عندوش", perPatient: "دق/مريض", learned: "محسوبة اليوم", settings: "الإعدادات",
    // staff
    staffTitle: "لوحة الشبابيك", desk: "الشباك", callNext: "عيّط اللي بعدو", done: "كمل", absent: "غايب", recall: "عاود عيّط",
    nobodyWaiting: "ما فما حتى حد", waitingList: "يستناو", served: "تخدموا", avgWait: "معدل الانتظار",
    noShows: "غيابات", addDemo: "زيد مرضى (ديمو)", reset: "صفّر", confirmReset: "تفسخ الطابور الكل؟",
    insTitle: "إحصائيات", openScreen: "الشاشة", openPatient: "تطبيق المريض", serving: "يتخدم", emptyQueue: "الطابور فارغ",
    // screen
    screenNow: "توا يعدّيو", screenJoin: "سكاني باش تاخو تيكيت", screenSound: "شغّل الصوت", screenRecent: "آخر النداءات",
  },
  ar: {
    dir: "rtl", label: "عربي", name: "العربية",
    tagline: "طابورك في جيبك",
    heroTitle: "لا مزيد من الانتظار وقوفاً",
    heroText: "احجز تذكرتك من هاتفك، تابع دورك مباشرة، واسأل المساعد عن أي شيء.",
    chooseService: "اختر الخدمة",
    namePlaceholder: "اسمك (اختياري)",
    waitingShort: "في الانتظار", minutes: "د", noWait: "لا يوجد طابور",
    emergencyTitle: "حالة طارئة؟", emergencyText: "لا تأخذ تذكرة. توجّه مباشرة إلى الطوارئ أو اتصل بالرقم 190.",
    yourTicket: "تذكرتك", peopleAhead: "أمامك", estWait: "الانتظار", nowServing: "يُخدم الآن",
    statusWaiting: "في الطابور", statusSoon: "اقترب دورك! استعد", statusCalled: "حان دورك!",
    goToDesk: "توجّه إلى الشباك", statusDone: "شكراً لك!", doneText: "نتمنى لك الشفاء العاجل.",
    statusCancelled: "غادرت الطابور", statusMissed: "فاتك الدور", missedText: "تم استدعاؤك مرتين دون حضور.",
    noShowWarn: "تم استدعاؤك ولم تحضر، فانتقلت إلى آخر الطابور.",
    leaveQueue: "مغادرة الطابور", confirmLeave: "هل تريد فعلاً مغادرة الطابور؟", newTicket: "تذكرة جديدة", gotIt: "حسناً، أنا في الطريق",
    askDawrek: "اسأل دورك", chatTitle: "دورك، مساعدك الذكي", chatPlaceholder: "اكتب بالعربية أو الدارجة أو الفرنسية…",
    chatHello: "مرحباً! أنا دورك 👋 اسألني عن موقعك في الطابور أو الوثائق المطلوبة أو المواعيد.",
    suggestions: ["كم شخصاً أمامي؟", "ما الوثائق المطلوبة؟", "كيف ألغي موعداً؟"],
    aiOn: "ذكاء اصطناعي", aiOff: "وضع غير متصل", safety: "سلامة", typing: "دورك يكتب…", chatError: "حدث خطأ، حاول مجدداً.",
    services: {
      consultation: ["الاستشارة العامة", "طبيب عام"], followup: ["المتابعة الطبية", "الأمراض المزمنة"],
      lab: ["التحاليل", "أخذ العينات"], imaging: ["الأشعة والتصوير", "أشعة وإيكو"], admin: ["الخدمات الإدارية", "شهادات ووثائق"],
    },
    pinPrompt: "أدخل الرمز السري للطاقم", micStart: "تحدّث", micStop: "إيقاف وإرسال", listening: "أستمع إليك… اضغط للإيقاف", transcribing: "أكتب كلامك…", micDenied: "الميكروفون محظور. فعّله من إعدادات المتصفح.", voiceError: "لم أفهم التسجيل، حاول مجدداً.", speak: "اقرأ الإجابة", tooMany: "طلبات كثيرة، انتظر قليلاً.",
    bigText: "خط كبير", haveAppointment: "لديّ موعد", apptHint: "يتحقق الموظفون منه عند الشباك. أصحاب المواعيد لهم الأولوية.",
    apptPending: "📅 موعدك في انتظار تأكيد الموظفين", apptConfirmed: "📅 تم تأكيد موعدك: لك الأولوية",
    alertsTitle: "تنبيه على هاتفك", alertsText: "سننبّهك عندما يقترب دورك، حتى لو كان الهاتف مقفلاً.",
    alertsBtn: "تفعيل التنبيهات", alertsOn: "التنبيهات مفعّلة ✓ يمكنك قفل الهاتف.",
    alertsDenied: "التنبيهات محظورة. اسمح بها لهذا الموقع من إعدادات المتصفح.",
    alertsIos: "على الآيفون: اضغط مشاركة ← إضافة إلى الشاشة الرئيسية، ثم افتح دورك من هناك لتفعيل التنبيهات.",
    alertsError: "تعذّر تفعيل التنبيهات. أبقِ هذه الصفحة مفتوحة.",
    apptCheck: "مواعيد للتحقق", confirm: "تأكيد", reject: "لا موعد", perPatient: "د/مريض", learned: "محسوبة اليوم", settings: "الإعدادات",
    staffTitle: "لوحة الشبابيك", desk: "الشباك", callNext: "استدعاء التالي", done: "تم", absent: "غائب", recall: "إعادة النداء",
    nobodyWaiting: "لا أحد في الانتظار", waitingList: "في الانتظار", served: "تمت خدمتهم", avgWait: "متوسط الانتظار",
    noShows: "الغيابات", addDemo: "إضافة مرضى (عرض)", reset: "إعادة ضبط", confirmReset: "مسح الطابور بالكامل؟",
    insTitle: "الإحصائيات", openScreen: "الشاشة", openPatient: "تطبيق المريض", serving: "قيد الخدمة", emptyQueue: "الطابور فارغ",
    screenNow: "يُخدم الآن", screenJoin: "امسح الرمز لأخذ تذكرة", screenSound: "تفعيل الصوت", screenRecent: "آخر النداءات",
  },
  fr: {
    dir: "ltr", label: "FR", name: "Français",
    tagline: "Votre file d'attente dans la poche",
    heroTitle: "Fini d'attendre debout",
    heroText: "Prenez un ticket depuis votre téléphone, suivez votre tour en direct et posez vos questions à Dawrek.",
    chooseService: "Choisissez un service",
    namePlaceholder: "Votre prénom (optionnel)",
    waitingShort: "en attente", minutes: "min", noWait: "Pas d'attente",
    emergencyTitle: "Urgence ?", emergencyText: "Ne prenez pas de ticket. Allez directement aux urgences ou appelez le 190.",
    yourTicket: "Votre ticket", peopleAhead: "Devant vous", estWait: "Attente", nowServing: "En cours",
    statusWaiting: "Dans la file", statusSoon: "C'est bientôt à vous !", statusCalled: "C'est votre tour !",
    goToDesk: "Présentez-vous au guichet", statusDone: "Merci !", doneText: "Prompt rétablissement.",
    statusCancelled: "Vous avez quitté la file", statusMissed: "Tour manqué", missedText: "Vous avez été appelé deux fois sans vous présenter.",
    noShowWarn: "Vous avez été appelé en votre absence : vous êtes repassé en fin de file.",
    leaveQueue: "Quitter la file", confirmLeave: "Voulez-vous vraiment quitter la file ?", newTicket: "Nouveau ticket", gotIt: "J'arrive !",
    askDawrek: "Demander à Dawrek", chatTitle: "Dawrek, votre assistant", chatPlaceholder: "Écrivez en français, en tounsi, en arabe…",
    chatHello: "Bonjour ! Je suis Dawrek 👋 Demandez-moi votre place dans la file, les documents à apporter ou les rendez-vous.",
    suggestions: ["Combien de personnes devant moi ?", "Quels documents apporter ?", "Comment annuler un rendez-vous ?"],
    aiOn: "IA", aiOff: "Hors ligne", safety: "Sécurité", typing: "Dawrek écrit…", chatError: "Une erreur est survenue, réessayez.",
    services: {
      consultation: ["Consultation générale", "Médecin généraliste"], followup: ["Suivi médical", "Maladies chroniques"],
      lab: ["Analyses", "Prélèvements"], imaging: ["Radiologie", "Radio & échographie"], admin: ["Administratif", "Certificats, dossiers"],
    },
    pinPrompt: "Code PIN du personnel", micStart: "Parler", micStop: "Arrêter et envoyer", listening: "Je vous écoute… touchez pour arrêter", transcribing: "Transcription…", micDenied: "Micro bloqué. Autorisez-le dans les réglages du navigateur.", voiceError: "Je n'ai pas compris l'audio, réessayez.", speak: "Lire la réponse", tooMany: "Trop de questions, patientez un instant.",
    bigText: "Grand texte", haveAppointment: "J'ai un rendez-vous", apptHint: "Le personnel le vérifie au guichet. Les rendez-vous passent en priorité.",
    apptPending: "📅 Rendez-vous en attente de vérification", apptConfirmed: "📅 Rendez-vous confirmé : vous passez en priorité",
    alertsTitle: "Être prévenu sur mon téléphone", alertsText: "Votre téléphone sonne quand votre tour approche, même verrouillé.",
    alertsBtn: "Activer les alertes", alertsOn: "Alertes activées ✓ Vous pouvez verrouiller votre téléphone.",
    alertsDenied: "Les alertes sont bloquées. Autorisez les notifications pour ce site dans le navigateur.",
    alertsIos: "Sur iPhone : touchez Partager → Sur l'écran d'accueil, puis ouvrez Dawrek depuis là pour les alertes.",
    alertsError: "Impossible d'activer les alertes. Gardez cette page ouverte.",
    apptCheck: "Rendez-vous à vérifier", confirm: "Confirmer", reject: "Pas de RDV", perPatient: "min/patient", learned: "appris aujourd'hui", settings: "Réglages",
    staffTitle: "Console guichets", desk: "Guichet", callNext: "Appeler le suivant", done: "Terminé", absent: "Absent", recall: "Rappeler",
    nobodyWaiting: "Personne en attente", waitingList: "En attente", served: "Servis", avgWait: "Attente moyenne",
    noShows: "Absences", addDemo: "Ajouter des patients (démo)", reset: "Réinitialiser", confirmReset: "Vider toute la file ?",
    insTitle: "Insights", openScreen: "Écran", openPatient: "App patient", serving: "En cours", emptyQueue: "File vide",
    screenNow: "En cours", screenJoin: "Scannez pour prendre un ticket", screenSound: "Activer le son", screenRecent: "Derniers appels",
  },
  en: {
    dir: "ltr", label: "EN", name: "English",
    tagline: "Your queue, in your pocket",
    heroTitle: "No more waiting on your feet",
    heroText: "Take a ticket from your phone, follow your turn live, and ask Dawrek anything.",
    chooseService: "Choose a service",
    namePlaceholder: "Your first name (optional)",
    waitingShort: "waiting", minutes: "min", noWait: "No wait",
    emergencyTitle: "Emergency?", emergencyText: "Don't take a ticket. Go straight to the emergency department or call 190.",
    yourTicket: "Your ticket", peopleAhead: "Ahead of you", estWait: "Wait", nowServing: "Now serving",
    statusWaiting: "In the queue", statusSoon: "Almost your turn! Get ready", statusCalled: "It's your turn!",
    goToDesk: "Please go to desk", statusDone: "Thank you!", doneText: "Get well soon.",
    statusCancelled: "You left the queue", statusMissed: "Turn missed", missedText: "You were called twice but didn't show up.",
    noShowWarn: "You were called while away, so you moved to the end of the line.",
    leaveQueue: "Leave the queue", confirmLeave: "Do you really want to leave the queue?", newTicket: "New ticket", gotIt: "On my way!",
    askDawrek: "Ask Dawrek", chatTitle: "Dawrek, your assistant", chatPlaceholder: "Write in English, French, Tounsi, Arabic…",
    chatHello: "Hi! I'm Dawrek 👋 Ask me about your place in line, which documents to bring, or appointments.",
    suggestions: ["How many people are ahead of me?", "What documents do I need?", "How do I cancel an appointment?"],
    aiOn: "AI", aiOff: "Offline", safety: "Safety", typing: "Dawrek is typing…", chatError: "Something went wrong, please retry.",
    services: {
      consultation: ["General consultation", "General practitioner"], followup: ["Medical follow-up", "Chronic conditions"],
      lab: ["Lab tests", "Sample collection"], imaging: ["Imaging", "X-ray & ultrasound"], admin: ["Administrative", "Certificates, records"],
    },
    pinPrompt: "Staff PIN", micStart: "Speak", micStop: "Stop and send", listening: "Listening… tap to stop", transcribing: "Transcribing…", micDenied: "Microphone blocked. Allow it in your browser settings.", voiceError: "I couldn't understand the audio, please retry.", speak: "Read the answer aloud", tooMany: "Too many questions, please wait a moment.",
    bigText: "Bigger text", haveAppointment: "I have an appointment", apptHint: "Staff check it at the desk. Appointments are served first.",
    apptPending: "📅 Appointment waiting for staff to check", apptConfirmed: "📅 Appointment confirmed: you're served first",
    alertsTitle: "Get alerted on your phone", alertsText: "Your phone rings when your turn is near, even when it's locked.",
    alertsBtn: "Turn on alerts", alertsOn: "Alerts on ✓ You can lock your phone.",
    alertsDenied: "Alerts are blocked. Allow notifications for this site in your browser settings.",
    alertsIos: "On iPhone: tap Share → Add to Home Screen, then open Dawrek from there to get alerts.",
    alertsError: "Couldn't turn on alerts. Keep this page open instead.",
    apptCheck: "Appointments to check", confirm: "Confirm", reject: "No appointment", perPatient: "min/patient", learned: "learned today", settings: "Settings",
    staffTitle: "Desk console", desk: "Desk", callNext: "Call next", done: "Done", absent: "No-show", recall: "Recall",
    nobodyWaiting: "Nobody waiting", waitingList: "Waiting", served: "Served", avgWait: "Avg. wait",
    noShows: "No-shows", addDemo: "Add patients (demo)", reset: "Reset", confirmReset: "Clear the whole queue?",
    insTitle: "Insights", openScreen: "Screen", openPatient: "Patient app", serving: "Serving", emptyQueue: "Queue is empty",
    screenNow: "Now serving", screenJoin: "Scan to take a ticket", screenSound: "Enable sound", screenRecent: "Recent calls",
  },
};

const SERVICE_ICONS = { consultation: "🩺", followup: "🔁", lab: "🧪", imaging: "🩻", admin: "📄" };

const Lang = {
  key: "dawrek.lang",
  current: "tn",
  init(onChange) {
    try { this.current = localStorage.getItem(this.key) || this.current; } catch {}
    if (!I18N[this.current]) this.current = "tn";
    this.onChange = onChange;
    this.apply();
  },
  t(k) { return I18N[this.current][k] ?? I18N.en[k] ?? k; },
  set(lang) {
    this.current = lang;
    try { localStorage.setItem(this.key, lang); } catch {}
    this.apply();
    this.onChange && this.onChange();
  },
  apply() {
    document.documentElement.lang = this.current === "tn" ? "ar-TN" : this.current;
    document.documentElement.dir = I18N[this.current].dir;
    document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = this.t(el.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = this.t(el.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-title]").forEach((el) => { el.title = el.ariaLabel = this.t(el.dataset.i18nTitle); });
    document.querySelectorAll(".lang-switch select").forEach((s) => { s.value = this.current; });
  },
  renderSwitch(container) {
    container.innerHTML = `<span aria-hidden="true">🌐</span><select aria-label="Language">${Object.entries(I18N)
      .map(([k, v]) => `<option value="${k}">${v.name}</option>`).join("")}</select>`;
    container.querySelector("select").addEventListener("change", (e) => this.set(e.target.value));
    this.apply();
  },
};

const PIN_KEY = "dawrek.pin";
const api = async (path, options = {}, retried = false) => {
  let pin = "";
  try { pin = localStorage.getItem(PIN_KEY) || ""; } catch {}
  const raw = options.body instanceof Blob;
  const res = await fetch(path, {
    ...options,
    headers: { "Content-Type": raw ? options.body.type : "application/json", "X-Staff-Pin": pin },
    body: raw ? options.body : options.body ? JSON.stringify(options.body) : undefined,
  });
  if (res.status === 401 && !retried) {
    // Staff action on a public deployment: ask for the PIN once, remember it on this device.
    const entered = prompt(Lang.t("pinPrompt"));
    if (entered) {
      try { localStorage.setItem(PIN_KEY, entered.trim()); } catch {}
      return api(path, options, true);
    }
  }
  if (!res.ok) {
    const detail = await res.json().then((j) => j.detail).catch(() => "");
    throw Object.assign(new Error(`HTTP ${res.status}`), { status: res.status, detail: typeof detail === "string" ? detail : "" });
  }
  return res.json();
};

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const serviceName = (key) => Lang.t("services")[key][0];

// Short two-tone chime (Web Audio, no asset needed). Browsers allow it after a user gesture.
let audioCtx;
function chime() {
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    [880, 660].forEach((freq, i) => {
      const o = audioCtx.createOscillator(), g = audioCtx.createGain();
      o.frequency.value = freq; o.type = "sine";
      const t0 = audioCtx.currentTime + i * 0.28;
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.35, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.6);
      o.connect(g).connect(audioCtx.destination);
      o.start(t0); o.stop(t0 + 0.65);
    });
  } catch {}
}
function unlockAudio() { try { audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)(); audioCtx.resume(); } catch {} }
