(function(){'use strict';
const $=id=>document.getElementById(id),core=WenareDepartures,logic=WenareNearby;
let sequence=0,controller=null,timer=null,tick=null,enabled=true,places=[],sources={},lastFix=null,results=new Map(),stopIndex=new Map();
let candidates=[],radius=250,manualRadius=false,view='balanced';
const expanded=new Set(),views=['balanced','departure','directions'];
try{const saved=localStorage.getItem('wenare-overview-view');if(views.includes(saved))view=saved;}catch{}
const icon=mode=>({metro:'Ⓜ',rer:'Ⓡ',bus:'🚌'}[mode]||'🚏');
function badge(service){const e=element('span',icon(service.mode)+' '+label(service.mode)+' '+service.lineName,'line-badge mode-'+service.mode);e.title=label(service.mode)+' '+service.lineName;return e;}
function controls(){document.querySelectorAll('[data-radius]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.radius)===radius)));document.querySelectorAll('button[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));$('radiusStatus').textContent=(manualRadius?'📍':'✨ Auto ·')+' '+radius.toLocaleString('fr-FR')+' m · '+places.length+' point'+(places.length===1?'':'s');}
const label=mode=>({metro:'Métro',rer:'RER',bus:'Bus'}[mode]||'Transport');
const say=text=>{$('nearbyOverviewStatus').textContent=text};
function cancel(clear=true){sequence++;controller?.abort();controller=null;clearTimeout(timer);clearInterval(tick);timer=tick=null;if(clear){places=[];results.clear();$('nearbyCards').replaceChildren();}}
function fallback(text){enabled=false;say(text);$('manualOptions').open=true;}
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function render(){
 const focusedPlace=document.activeElement?.classList.contains('place-summary')?document.activeElement.dataset.placeId:null;controls();$('nearbyCards').replaceChildren();if(!places.length&&lastFix&&enabled)$('nearbyCards').append(element('p','🔎 Aucun point de départ à moins de '+radius.toLocaleString('fr-FR')+' m. Essayez un autre rayon.','nearby-empty'));const nowWall=Date.now(),nowMono=performance.now();
 for(const [i,place] of places.entries()){
 const card=element('article',undefined,'departure-place');card.dataset.view=view;
 const observations=[],lineStates=new Map();let partial=false;
 for(const service of place.services){const key=service.lineId,row=results.get(service.key);if(!lineStates.has(key))lineStates.set(key,{service,text:'Aucun départ annoncé sur la période disponible.'});if(!row){lineStates.get(key).text='Recherche des horaires…';continue;}if(row.error){lineStates.get(key).text=row.error;partial=true;continue;}const now=row.clock.server+nowMono-row.clock.mono;if(Math.abs((nowWall-row.clock.wall)-(nowMono-row.clock.mono))>30000||now>=Date.parse(row.response.validUntilUtc)){lineStates.get(key).text='Horaires expirés ou horloge modifiée. Actualisation nécessaire.';partial=true;continue;}for(const event of row.response.departures){const view=core.presentation(event,now);if(view?.active)observations.push({service,event,view});}}
 const groups=logic.departureGroups(observations,stopIndex),list=element('ul',undefined,'all-departures'),shown=new Set();
 for(const group of groups){shown.add(group.lineId);const li=element('li'),name=element('div',undefined,'departure-service');name.append(badge(group),element('span','→ '+group.nextName));li.append(name);const times=element('p',undefined,'departure-times');group.events.forEach((item,j)=>times.append(element('span',(j?'Puis ':'')+item.view.label.toLocaleLowerCase('fr')+' · '+new Date(item.view.time).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit'}))));if(group.events.length===1)times.append(element('span','Puis : non annoncé'));li.append(times);list.append(li);}
 for(const [line,{service,text}] of lineStates)if(!shown.has(line)){const li=element('li'),name=element('div',undefined,'departure-service');name.append(badge(service));li.append(name,element('p',text,'muted'));list.append(li);}
 const ordered=[...groups].sort((a,b)=>a.events[0].view.time-b.events[0].view.time),first=ordered[0],second=ordered[1];
 const summary=element('button',undefined,'place-summary'),detailId='place-detail-'+i,open=expanded.has(place.id);
 summary.type='button';summary.dataset.placeId=place.id;summary.setAttribute('aria-expanded',String(open));summary.setAttribute('aria-controls',detailId);
 const row1=element('span',undefined,'summary-row place-heading'),title=element('h2',place.name,'place-name');title.title=place.name;
 row1.append(element('span','📍','place-pin'),title,element('span',Math.ceil(place.distance)+' m','place-distance'),element('span',open?'⌃':'⌄','place-chevron'));
 const row2=element('span',undefined,'summary-row'),row3=element('span',undefined,'summary-row');
 const walk='🚶 ≈ '+core.walkingMinutes(place.distance)+' min',time=item=>item.view.label.toLocaleLowerCase('fr').replace(/^dans /,''),remaining=Math.max(0,ordered.length-(view==='directions'?2:1));
 const groupRow=(row,g,large=false)=>{row.append(badge(g),element('span','→ '+g.nextName,'summary-destination'));row.append(element('span',time(g.events[0]),large?'summary-time large-time':'summary-time'));};
 const more=()=>element('span',remaining?'＋'+remaining+' autres':(partial?'⚠ Partiel':'⌄ Détails'),'summary-more');
 if(view==='balanced'){
   row2.append(element('span',walk,'summary-walk'));const lines=[...lineStates.values()].map(x=>x.service).sort((a,b)=>['metro','rer','bus'].indexOf(a.mode)-['metro','rer','bus'].indexOf(b.mode));lines.slice(0,2).forEach(service=>row2.append(badge(service)));if(lines.length>2)row2.append(element('span','＋'+(lines.length-2),'summary-more'));
   if(first){row3.append(badge(first),element('span','→ '+first.nextName,'summary-destination'),element('span',time(first.events[0]),'summary-time'),element('span',first.events[1]?'puis '+time(first.events[1]):'Puis : —','summary-following'));}else row3.append(element('span',[...lineStates.values()][0]?.text||'Horaires indisponibles','summary-destination'));
 }else if(view==='departure'){
   if(first)groupRow(row2,first,true);else row2.append(element('span',[...lineStates.values()][0]?.text||'Horaires indisponibles','summary-destination'));
   row3.append(element('span',walk,'summary-walk'),element('span',first?.events[1]?'Puis '+time(first.events[1]):'Puis : —','summary-following'),more());
 }else{
   if(first)groupRow(row2,first);else row2.append(element('span',[...lineStates.values()][0]?.text||'Horaires indisponibles','summary-destination'));
   if(second)groupRow(row3,second);else row3.append(element('span',walk,'summary-walk'),element('span',first?.events[1]?'Puis '+time(first.events[1]):'Puis : —','summary-following'));
   row3.append(more());
 }

 summary.append(row1,row2,row3);const detail=element('div',undefined,'place-detail');detail.id=detailId;detail.hidden=!open;
 detail.append(element('p',Math.ceil(place.distance)+' m à vol d’oiseau · '+walk+' de marche indicative','muted'),list,element('small',(partial?'⚠ Certains horaires sont indisponibles · ':'')+'Horaires théoriques · départs regroupés par premier arrêt · perturbations non connues'));
 summary.onclick=()=>{if(expanded.has(place.id))expanded.delete(place.id);else expanded.add(place.id);render();};
 card.append(summary,detail);$('nearbyCards').append(card);
 }
 if(focusedPlace)Array.from(document.querySelectorAll('.place-summary')).find(b=>b.dataset.placeId===focusedPlace)?.focus({preventScroll:true});
}
async function catalogues(mine){
 const outputs=await Promise.allSettled([
 (async()=>{let record;try{record=await MMIReference.update();}catch{record=await MMIReference.read();}if(!record)throw new Error();if(mine===sequence)window.mmiSetReference?.(record);return {mode:'metro',stations:core.catalogue(record.data),stops:record.data.stops,sha:record.manifest.sha256};})(),
 (async()=>{const record=await WenareMobility.load(controller.signal);return {record,mode:'extra',stations:core.catalogue(record.data),stops:record.data.stops,sha:record.manifest.networkSha256};})()
 ]);if(mine!==sequence)return null;sources={};stopIndex=new Map();const data=[];for(let i=0;i<outputs.length;i++){const r=outputs[i];if(r.status==='fulfilled'){sources[r.value.mode]=r.value;data.push(r.value.stations);for(const stop of r.value.stops)stopIndex.set(stop.stop_id,stop);}}
 $('nearbyCoverage').textContent=(sources.extra?.record?.manifest.catalogueVersion===3?'Couverture : métro (16 lignes), RER A–E et '+sources.extra.record.manifest.qa.busLines+' lignes de bus au catalogue Île-de-France. Arrêts disposant de départs théoriques sur la période.':'Couverture : métro (16 lignes), RER A–E et cinq lignes de bus pilotes. Classement parmi les points couverts.')+(outputs.some(r=>r.status==='rejected')?' Certaines données sont indisponibles : propositions partielles.':'');return logic.mergePlaces(data);
}
let timetableReady=null;
function ensureTimetable(){if(window.WenareTimetable?.bundleVersion==='2026-11-03.12'&&typeof window.WenareTimetable.loadMany==='function')return Promise.resolve();if(!timetableReady)timetableReady=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='./timetable.js?v=14';script.onload=()=>window.WenareTimetable?.bundleVersion==='2026-11-03.12'&&typeof window.WenareTimetable.loadMany==='function'?resolve():reject(new Error('CLIENT_UPDATE_REQUIRED'));script.onerror=()=>reject(new Error('CLIENT_UPDATE_REQUIRED'));document.head.append(script);}).catch(error=>{timetableReady=null;throw error;});return timetableReady;}
async function departures(mine){if(mine!==sequence||document.hidden)return;const queries=[...new Map(places.flatMap(p=>p.services).map(s=>[s.key,s])).values()];
 await Promise.allSettled(['metro','extra'].map(async mode=>{const src=sources[mode],q=queries.filter(s=>(s.mode==='metro'?'metro':'extra')===mode);if(!src||!q.length)return;try{await ensureTimetable();if(mine!==sequence)return;const rows=await WenareTimetable.loadMany(q,src.sha,controller.signal,mode==='metro'?'./distribution/timetable/':'./distribution/mobility/',true);if(mine!==sequence)return;for(const row of rows)results.set(row.query.key,{...row,clock:row.response?{server:Date.parse(row.response.serverTimeUtc),mono:performance.now(),wall:Date.now()}:null});render();}catch(error){if(mine!==sequence)return;for(const s of q)results.set(s.key,{error:error.message==='CLIENT_UPDATE_REQUIRED'?'Mise à jour de l’application indisponible. Fermez puis rouvrez WENARE avec une connexion.':'Horaires temporairement indisponibles.'});render();}}));
 if(mine!==sequence||document.hidden)return;say(places.length?'🕒 Horaires théoriques · les sens de départ sont regroupés.':'🔎 Aucun point dans ce rayon.');$('nearbyOverviewAge').textContent='Position reçue à '+new Date(lastFix.timestamp).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris'})+' · précision ±'+Math.round(lastFix.coords.accuracy)+' m'+(lastFix.coords.accuracy>100?' · l’ordre des points proches peut être incertain.':'')+(Array.from(results.values()).some(r=>r.response?.clockSource==='device')?' · horaires calculés avec l’horloge de l’appareil.':'');
 clearInterval(tick);tick=setInterval(render,1000);clearTimeout(timer);timer=setTimeout(()=>{if(enabled&&!document.hidden)start();},60000);
}
async function start(){enabled=true;$('manualOptions').open=false;cancel();if(document.hidden)return;controller=new AbortController();const mine=sequence;say('Wenare vous localise et prépare vos départs…');$('nearbyOverviewAge').textContent='';
 const catalogue=catalogues(mine);
 if(!navigator.geolocation){fallback('Localisation indisponible sur cet appareil. La recherche manuelle reste disponible.');return;}
 let position;try{position=await new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:15000,maximumAge:15000}));}catch(error){if(mine===sequence)fallback(error.code===1?'Autorisez la localisation pour voir vos départs automatiquement. Vous pouvez aussi rechercher un arrêt manuellement.':'Position indisponible. La recherche manuelle reste disponible.');return;}
 if(mine!==sequence)return;if(!logic.validPosition(position.coords,position.timestamp)){fallback('Position trop ancienne ou imprécise. Réessayez ou recherchez un arrêt manuellement.');return;}lastFix=position;const stations=await catalogue;if(mine!==sequence||!stations)return;if(!stations.length){fallback('Données indisponibles pour proposer des départs. La recherche manuelle reste disponible.');return;}
 candidates=core.nearby(stations,{lat:position.coords.latitude,lon:position.coords.longitude},3);if(!manualRadius)radius=logic.automaticRadius(candidates);places=logic.withinRadius(candidates,radius);render();say('Vos points de départ sont trouvés. Chargement des horaires de toutes les lignes…');await departures(mine);
}
document.querySelectorAll('[data-radius]').forEach(button=>button.onclick=async()=>{if(!lastFix||!enabled||!candidates.length)return;manualRadius=true;radius=Number(button.dataset.radius);cancel();controller=new AbortController();places=logic.withinRadius(candidates,radius);render();say('Chargement des horaires dans le rayon choisi…');await departures(sequence);});
document.querySelectorAll('button[data-view]').forEach(button=>button.onclick=()=>{view=button.dataset.view;try{localStorage.setItem('wenare-overview-view',view);}catch{}render();});
controls();
$('nearbyRestart').onclick=start;$('nearbyPause').onclick=()=>{enabled=false;cancel();say('Localisation et actualisation arrêtées.');$('nearbyOverviewAge').textContent='';};
$('manualOptions').addEventListener('toggle',()=>{if($('manualOptions').open&&enabled){enabled=false;cancel();say('Options manuelles ouvertes · actualisation automatique suspendue.');}});
$('eraseNetwork').addEventListener('click',()=>{enabled=false;cancel();say('Données locales effacées. Relancez la localisation pour les recharger.');});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancel();say('Consultation suspendue pendant votre absence.');}else if(enabled)start();});
 window.addEventListener('pageshow',event=>{if(event.persisted&&enabled)start();});
 start();
})();

