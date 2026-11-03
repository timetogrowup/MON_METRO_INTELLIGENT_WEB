/* Shared catalogue and display rules. No credentials, network calls or user storage. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WenareDepartures=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const fold=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr').replace(/[’'-]/g,' ');
function catalogue(data){
 const stops=new Map(data.stops.map(s=>[s.stop_id,s])),lines=new Map(data.lines.map(l=>[l.route_id,l])),byPoint=new Map();
 for(const pattern of data.patterns){const destinationId=pattern.stop_ids.at(-1),destinationName=stops.get(destinationId)?.stop_name;if(!destinationName)continue;
  pattern.stop_ids.forEach((id,i)=>{if(i===pattern.stop_ids.length-1||pattern.stop_rules?.[i]?.pickup_type==='1')return;const s=stops.get(id),line=lines.get(pattern.route_id);if(!s||!line)return;const list=byPoint.get(id)||[];
   const key=JSON.stringify([id,pattern.route_id,destinationId]);if(!list.some(x=>x.key===key))list.push({key,stopId:id,lineId:pattern.route_id,lineName:line.route_short_name,directionId:destinationId,destinationName,mode:'metro',quayName:s.platform_code||null});byPoint.set(id,list);
  });
 }
 return data.stations.map(s=>({...s,services:s.stop_point_ids.flatMap(id=>byPoint.get(id)||[])})).filter(s=>s.services.length).sort((a,b)=>a.name.localeCompare(b.name,'fr'));
}
function search(stations,text){const words=fold(text).trim().split(/\s+/).filter(Boolean);return stations.filter(s=>words.every(w=>fold(s.name).includes(w)))}
function nearby(stations,pos,max=8){const rad=Math.PI/180;return stations.map(s=>{const a=Math.sin((s.lat-pos.lat)*rad/2)**2+Math.cos(pos.lat*rad)*Math.cos(s.lat*rad)*Math.sin((s.lon-pos.lon)*rad/2)**2;return {...s,distance:6371000*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))}}).sort((a,b)=>a.distance-b.distance).slice(0,max)}
function walkingMinutes(distance){return Number.isFinite(distance)&&distance>=0?Math.max(1,Math.ceil(distance/80)):null}
function instant(value){return typeof value==='string'&&/^\d{4}-\d\d-\d\dT.*(?:Z|[+-]\d\d:\d\d)$/.test(value)&&Number.isFinite(Date.parse(value))?Date.parse(value):NaN}
function presentation(event,now){
 const quality=event.quality,recorded=instant(event.sourceRecordedAtUtc),validUntil=instant(event.validUntilUtc);
 const fresh=quality!=='real_time'||(Number.isFinite(recorded)&&recorded<=now+15000&&Number.isFinite(validUntil)&&now<=validUntil);
 if(quality==='stale'||!fresh)return {label:'Information ancienne',quality:'Donnée périmée',active:false};
 if(quality==='unknown'||!['real_time','timetable'].includes(quality))return {label:'Horaire indisponible',quality:'Information indisponible',active:false};
 const badge=quality==='real_time'?'Temps réel':'Horaire théorique';
 if(event.status==='cancelled')return {label:'Supprimé',quality:badge,active:false};
 if(event.status==='departed')return null;
 if(event.status==='at_stop'&&quality==='real_time')return {label:'À l’arrêt',quality:badge,active:true};
 const time=instant(quality==='real_time'?event.expectedTimeUtc:event.scheduledTimeUtc);
 if(!Number.isFinite(time))return {label:'Heure non précisée',quality:badge,active:false};
 const seconds=(time-now)/1000;if(seconds<=0)return null;
 return {label:seconds<60?'Moins d’une minute':'Dans '+Math.ceil(seconds/60)+' min',quality:badge,active:true,time};
}
function validateResponse(body,query){
 if(!body||body.schemaVersion!==1||!Number.isFinite(instant(body.serverTimeUtc))||!Array.isArray(body.departures)||body.departures.length>500||!body.query||!['available','partial','none_announced','no_service_verified','unavailable'].includes(body.serviceStatus)||!['covered','uncovered','unknown'].includes(body.coverage?.status))throw new Error('Réponse de passages invalide');
 for(const key of ['stopId','lineId','directionId'])if(body.query[key]!==query[key])throw new Error('Réponse pour un autre service');
 const ids=new Set();for(const event of body.departures){if(!event||typeof event!=='object'||!['estimated','scheduled','at_stop','cancelled','departed','unknown'].includes(event.status))throw new Error('Passage invalide');for(const key of ['stopId','lineId','directionId'])if(event[key]!==query[key])throw new Error('Passage rattaché à un autre service');if(typeof event.id!=='string'||ids.has(event.id)||!['real_time','timetable','stale','unknown'].includes(event.quality))throw new Error('Passage invalide');ids.add(event.id);}
 if(!Number.isFinite(body.nextRefreshAfterSeconds)||body.nextRefreshAfterSeconds<1||body.nextRefreshAfterSeconds>86400)throw new Error('Cadence de passages invalide');return body;
}
return {catalogue,search,nearby,walkingMinutes,instant,presentation,validateResponse};
});
