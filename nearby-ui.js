(function(){'use strict';
const $=id=>document.getElementById(id),core=WenareDepartures,logic=WenareNearby;
let sequence=0,controller=null,timer=null,tick=null,enabled=true,places=[],sources={},lastFix=null,results=new Map();
const label=mode=>({metro:'Métro',rer:'RER',bus:'Bus'}[mode]||'Transport');
const say=text=>{$('nearbyOverviewStatus').textContent=text};
function cancel(clear=true){sequence++;controller?.abort();controller=null;clearTimeout(timer);clearInterval(tick);timer=tick=null;if(clear){places=[];results.clear();$('nearbyCards').replaceChildren();}}
function fallback(text){enabled=false;say(text);$('manualOptions').open=true;}
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function render(){
 $('nearbyCards').replaceChildren();const nowWall=Date.now(),nowMono=performance.now();
 for(const [i,place] of places.entries()){
 const card=element('article',undefined,'departure-place'),heading=element('div',undefined,'place-heading');heading.append(element('span',String(i+1),'place-rank'),element('h2',place.name));card.append(heading);
 card.append(element('p',Math.round(place.distance)+' m à vol d’oiseau · ≈ '+core.walkingMinutes(place.distance)+' min de marche indicative','muted'));
 const list=element('ul',undefined,'all-departures');let pending=false;
 for(const service of [...place.services].sort((a,b)=>a.mode.localeCompare(b.mode)||a.lineName.localeCompare(b.lineName,'fr',{numeric:true})||a.destinationName.localeCompare(b.destinationName,'fr'))){
 const li=element('li'),name=element('div',undefined,'departure-service');name.append(element('span',label(service.mode)+' '+service.lineName,'line-badge'),element('span','→ '+service.destinationName));if(service.quayName)name.append(element('small','Quai '+service.quayName));li.append(name);
 const row=results.get(service.key);if(!row){li.append(element('p','Recherche des horaires…','departure-times'));pending=true;}else if(row.error){li.append(element('p',row.error,'muted'));}else{
 const b=row.response,now=row.clock.server+nowMono-row.clock.mono;
 if(Math.abs((nowWall-row.clock.wall)-(nowMono-row.clock.mono))>30000||now>=Date.parse(b.validUntilUtc)){li.append(element('p','Horaires expirés ou horloge modifiée. Actualisation nécessaire.','muted'));}else{
 const events=logic.activeEvents(b.departures,now,core.presentation),times=element('p',undefined,'departure-times');
 if(events.length){events.forEach((item,j)=>{const time=element('span',(j?'Puis ':'')+item.view.label.toLocaleLowerCase('fr')+' · '+new Date(item.view.time).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit'}));times.append(time);});if(events.length===1)times.append(element('span','Puis : non annoncé'));}else times.textContent='Aucun départ annoncé sur la période disponible.';li.append(times);
 }}list.append(li);
 }card.append(list);card.append(element('small',pending?'Chargement…':'Horaires théoriques · perturbations non connues'));$('nearbyCards').append(card);
 }
}
async function catalogues(mine){
 const outputs=await Promise.allSettled([
 (async()=>{let record;try{record=await MMIReference.update();}catch{record=await MMIReference.read();}if(!record)throw new Error();if(mine===sequence)window.mmiSetReference?.(record);return {mode:'metro',stations:core.catalogue(record.data),sha:record.manifest.sha256};})(),
 (async()=>{const record=await WenareMobility.load(controller.signal);return {mode:'extra',stations:core.catalogue(record.data),sha:record.manifest.networkSha256};})()
 ]);if(mine!==sequence)return null;sources={};const data=[];for(let i=0;i<outputs.length;i++){const r=outputs[i];if(r.status==='fulfilled'){sources[r.value.mode]=r.value;data.push(r.value.stations);}}
 $('nearbyCoverage').textContent='Couverture : métro (16 lignes), RER A–E et bus 20, 21, 26, 38, 91 uniquement. Classement parmi les points couverts.'+(outputs.some(r=>r.status==='rejected')?' Certaines données sont indisponibles : propositions partielles.':'');return logic.mergePlaces(data);
}
async function departures(mine){if(mine!==sequence||document.hidden)return;const queries=[...new Map(places.flatMap(p=>p.services).map(s=>[s.key,s])).values()];
 await Promise.allSettled(['metro','extra'].map(async mode=>{const src=sources[mode],q=queries.filter(s=>(s.mode==='metro'?'metro':'extra')===mode);if(!src||!q.length)return;try{const rows=await WenareTimetable.loadMany(q,src.sha,controller.signal,mode==='metro'?'./distribution/timetable/':'./distribution/mobility/');if(mine!==sequence)return;for(const row of rows)results.set(row.query.key,{...row,clock:row.response?{server:Date.parse(row.response.serverTimeUtc),mono:performance.now(),wall:Date.now()}:null});render();}catch{if(mine!==sequence)return;for(const s of q)results.set(s.key,{error:'Horaires temporairement indisponibles.'});render();}}));
 if(mine!==sequence||document.hidden)return;say('Vos '+places.length+' points de départ les plus proches parmi les données disponibles. Tous les sens sont affichés.');$('nearbyOverviewAge').textContent='Position reçue à '+new Date(lastFix.timestamp).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris'})+' · précision ±'+Math.round(lastFix.coords.accuracy)+' m'+(lastFix.coords.accuracy>100?' · l’ordre des points proches peut être incertain.':'')+(Array.from(results.values()).some(r=>r.response?.clockSource==='device')?' · horaires calculés avec l’horloge de l’appareil.':'');
 clearInterval(tick);tick=setInterval(render,1000);clearTimeout(timer);timer=setTimeout(()=>{if(enabled&&!document.hidden)start();},60000);
}
async function start(){enabled=true;$('manualOptions').open=false;cancel();if(document.hidden)return;controller=new AbortController();const mine=sequence;say('Wenare vous localise et prépare vos départs…');$('nearbyOverviewAge').textContent='';
 const catalogue=catalogues(mine);
 if(!navigator.geolocation){fallback('Localisation indisponible sur cet appareil. La recherche manuelle reste disponible.');return;}
 let position;try{position=await new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:15000,maximumAge:15000}));}catch(error){if(mine===sequence)fallback(error.code===1?'Autorisez la localisation pour voir vos départs automatiquement. Vous pouvez aussi rechercher un arrêt manuellement.':'Position indisponible. La recherche manuelle reste disponible.');return;}
 if(mine!==sequence)return;if(!logic.validPosition(position.coords,position.timestamp)){fallback('Position trop ancienne ou imprécise. Réessayez ou recherchez un arrêt manuellement.');return;}lastFix=position;const stations=await catalogue;if(mine!==sequence||!stations)return;if(!stations.length){fallback('Données indisponibles pour proposer des départs. La recherche manuelle reste disponible.');return;}
 places=core.nearby(stations,{lat:position.coords.latitude,lon:position.coords.longitude},3);render();say('Vos points de départ sont trouvés. Chargement des horaires de toutes les lignes…');await departures(mine);
}
$('nearbyRestart').onclick=start;$('nearbyPause').onclick=()=>{enabled=false;cancel();say('Localisation et actualisation arrêtées.');$('nearbyOverviewAge').textContent='';};
$('manualOptions').addEventListener('toggle',()=>{if($('manualOptions').open&&enabled){enabled=false;cancel();say('Options manuelles ouvertes · actualisation automatique suspendue.');}});
$('eraseNetwork').addEventListener('click',()=>{enabled=false;cancel();say('Données locales effacées. Relancez la localisation pour les recharger.');});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancel();say('Consultation suspendue pendant votre absence.');}else if(enabled)start();});
 window.addEventListener('pageshow',event=>{if(event.persisted&&enabled)start();});
 start();
})();
