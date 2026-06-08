// Service worker "kill switch".
// O site institucional antigo registrava um service worker que guardava a
// página em cache e a servia mesmo depois de novas publicações. Este SW
// substitui aquele: limpa todos os caches, se desregistra e recarrega as
// abas abertas — garantindo que todos passem a ver a versão atual.
self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
      await self.registration.unregister();
      const clients = await self.clients.matchAll({ type: 'window' });
      clients.forEach((client) => client.navigate(client.url));
    } catch (e) {
      // silencioso — em qualquer falha, apenas não faz nada
    }
  })());
});
