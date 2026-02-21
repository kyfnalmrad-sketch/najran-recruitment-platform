const CACHE_NAME = 'recruitment-platform-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/manifest.json',
  '/offline.html'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('تم فتح الذاكرة المؤقتة');
        return cache.addAll(urlsToCache);
      })
      .catch(error => {
        console.error('خطأ في تثبيت Service Worker:', error);
      })
  );
  self.skipWaiting();
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('حذف الذاكرة المؤقتة القديمة:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// اعتراض الطلبات
self.addEventListener('fetch', event => {
  // تجاهل الطلبات غير HTTP
  if (!event.request.url.startsWith('http')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // إذا كانت الموارد في الذاكرة المؤقتة، أرجعها
        if (response) {
          return response;
        }

        // وإلا، حاول جلبها من الشبكة
        return fetch(event.request)
          .then(response => {
            // تحقق من أن الاستجابة صحيحة
            if (!response || response.status !== 200 || response.type === 'error') {
              return response;
            }

            // انسخ الاستجابة
            const responseToCache = response.clone();

            // أضفها إلى الذاكرة المؤقتة
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // في حالة الفشل، عد إلى صفحة offline
            return caches.match('/offline.html');
          });
      })
  );
});
