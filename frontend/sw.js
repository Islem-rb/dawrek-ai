// Dawrek service worker: shows "your turn" alerts sent by the server, even when the page is closed.
// No offline caching on purpose: the queue is live, a stale copy would show the wrong turn.

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data.json(); } catch { data = { title: "Dawrek", body: event.data?.text() || "" }; }
  event.waitUntil(self.registration.showNotification(data.title || "Dawrek", {
    body: data.body || "",
    tag: data.tag || "dawrek",
    renotify: true,
    requireInteraction: !!data.urgent,  // "your turn" stays on screen until the patient sees it
    vibrate: data.urgent ? [300, 120, 300, 120, 600] : [200],
    icon: "/static/icons/icon-192.png",
    badge: "/static/icons/icon-192.png",
    data: { url: "/" },
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    const open = windows.find((w) => new URL(w.url).pathname === "/");
    if (open) return open.focus();
    return self.clients.openWindow(event.notification.data?.url || "/");
  })());
});
