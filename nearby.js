/* Pure rules for the automatic overview. Place IDs, never names, define identity. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WenareNearby=api})(typeof globalThis!=='undefined'?globalThis:this,function(){'use strict';
function mergePlaces(catalogues){const places=new Map();for(const catalogue of catalogues)for(const station of catalogue){let p=places.get(station.id);if(!p){p={...station,services:[]};places.set(station.id,p);}const keys=new Set(p.services.map(s=>s.key));for(const s of station.services)if(!keys.has(s.key)){p.services.push(s);keys.add(s.key);}}return [...places.values()];}
function validPosition(coords,timestamp,now=Date.now()){return coords&&Number.isFinite(coords.latitude)&&Math.abs(coords.latitude)<=90&&Number.isFinite(coords.longitude)&&Math.abs(coords.longitude)<=180&&Number.isFinite(coords.accuracy)&&coords.accuracy>=0&&coords.accuracy<=1000&&Number.isFinite(timestamp)&&Math.abs(now-timestamp)<=60000;}
function activeEvents(events,now,presentation){return events.map(event=>({event,view:presentation(event,now)})).filter(r=>r.view?.active&&Number.isFinite(r.view.time)).sort((a,b)=>a.view.time-b.view.time).slice(0,2);}
return {mergePlaces,validPosition,activeEvents};
});
