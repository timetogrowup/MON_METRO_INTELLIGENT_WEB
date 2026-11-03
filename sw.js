'use strict';
const CACHE='mmi-shell-v2';const FILES=['./','./index.html','./network.js','./journey.js','./journey-ui.js','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES))));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('mmi-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
const url=new URL(event.request.url);if(url.pathname.includes('/distribution/'))return;
event.respondWith(fetch(event.request).then(response=>{if(response.ok&&FILES.some(f=>new URL(f,self.registration.scope).href===url.href)){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put(event.request,copy)))}return response}).catch(()=>caches.match(event.request).then(r=>r|| (event.request.mode==='navigate'?caches.match('./index.html'):Response.error()))));});
