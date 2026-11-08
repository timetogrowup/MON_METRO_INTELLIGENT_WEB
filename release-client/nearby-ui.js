(function(){'use strict';
const $=id=>document.getElementById(id),core=WenareDepartures,logic=WenareNearby;
let sequence=0,controller=null,timer=null,tick=null,enabled=true,places=[],sources={},lastFix=null,results=new Map(),stopIndex=new Map();
let scanned=[],railScanned=[],railPlaces=[],loading=false,dataIssues=false;
let candidates=[],radius=250,manualRadius=false,view='balanced';
const expanded=new Set(),views=['balanced','departure','directions'];
try{const saved=localStorage.getItem('wenare-overview-view');if(views.includes(saved))view=saved;}catch{}
const icon=mode=>({metro:'Ⓜ',rer:'Ⓡ',bus:'🚌'}[mode]||'🚏');
function badge(service){const e=element('span',icon(service.mode)+' '+label(service.mode)+' '+service.lineName,'line-badge mode-'+service.mode);e.title=label(service.mode)+' '+service.lineName;return e;}
function controls(){document.querySelectorAll('[data-radius]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.radius)===radius)));document.querySelectorAll('button[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));$('radiusStatus').textContent=(manualRadius?'📍':'✨ Auto ·')+' '+radius.toLocaleString('fr-FR')+' m · '+places.length+' point'+(places.length===1?'':'s')+(railPlaces.length?' · ＋'+railPlaces.length+' métro/RER':'');window.dispatchEvent(new CustomEvent('wenare:overview',{detail:{radius,manualRadius,enabled,transportCount:places.length+railPlaces.length,position:enabled?lastFix:null}}));}
const label=mode=>({metro:'Métro',rer:'RER',bus:'Bus'}[mode]||'Transport');
const say=text=>{$('nearbyOverviewStatus').textContent=text;$('nearbyOverviewStatus').classList.toggle('is-error',/⚠|indisponible|Autorisez|imprécise|trop ancienne/i.test(text));};
function cancel(clear=true){sequence++;controller?.abort();controller=null;clearTimeout(timer);clearInterval(tick);timer=tick=null;if(clear){places=[];railPlaces=[];scanned=[];railScanned=[];loading=false;results.clear();$('nearbyCards').replaceChildren();$('railCards').replaceChildren();$('railOverview').hidden=true;}controls();}
function fallback(text){enabled=false;say(text);$('manualOptions').open=true;}
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function groupsFor(place,wall=Date.now(),mono=performance.now()){
 const observations=[];for(const service of place.services){const row=results.get(service.key);if(!row)continue;if(row.error){dataIssues=true;continue;}const now=row.clock.server+mono-row.clock.mono;if(Math.abs((wall-row.clock.wall)-(mono-row.clock.mono))>30000||now>=Date.parse(row.response.validUntilUtc)){dataIssues=true;continue;}for(const event of row.response.departures){const view=core.presentation(event,now);if(logic.imminent(view,now))observations.push({service,event,view});}}
 return logic.directionGroups(observations);
}
function select(){dataIssues=false;const wall=Date.now(),mono=performance.now(),all=[...new Map([...railScanned,...scanned].map(p=>[p.id,p])).values()],groups=new Map(all.map(p=>[p.id,groupsFor(p,wall,mono)])),sections=logic.selectSections(scanned,groups,railScanned);places=sections.primary;railPlaces=sections.rail;}
function render(){
 select();const focusedPlace=document.activeElement?.classList.contains('place-summary')?document.activeElement.dataset.placeId:null;controls();$('nearbyCards').replaceChildren();$('railCards').replaceChildren();$('railOverview').hidden=!railPlaces.length;if(!places.length&&lastFix&&enabled)$('nearbyCards').append(element('p',loading?'⏳ Recherche des départs dans les 60 minutes…':dataIssues?'⚠ Horaires indisponibles ou expirés. Réessayez avec une connexion.':'🔎 Aucun départ dans les 60 minutes à moins de '+radius.toLocaleString('fr-FR')+' m.','nearby-empty'));const nowWall=Date.now(),nowMono=performance.now();
 for(const {i,place,target,prefix} of [...places.map((place,i)=>({place,i,target:'nearbyCards',prefix:'place'})),...railPlaces.map((place,i)=>({place,i,target:'railCards',prefix:'rail'}))]){
 const card=element('article',undefined,'departure-place');card.dataset.view=view;
 const groups=place.groups,lineStates=new Map(place.services.map(service=>[service.lineId,{service}])),partial=dataIssues,list=element('ul',undefined,'all-departures'),shown=new Set();
 for(const group of groups){shown.add(group.lineId);const li=element('li'),name=element('div',undefined,'departure-service');li.dataset.lineId=group.lineId;name.append(badge(group),element('span',(group.gtfsDirectionId===null?'Sens non renseigné · ':'')+'→ '+group.nextName));li.append(name);const times=element('p',undefined,'departure-times');group.events.forEach((item,j)=>times.append(element('span',(j?'Puis ':'')+item.view.label.toLocaleLowerCase('fr')+' → '+(item.event.destinationName||'Destination non renseignée')+' · '+new Date(item.view.time).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris',hour:'2-digit',minute:'2-digit'}))));if(group.events.length===1)times.append(element('span','Puis : aucun dans les 60 min'));li.append(times);list.append(li);}
 const lines=logic.lineRows(groups).sort(view==='departure'?(a,b)=>a.nextTime-b.nextTime:view==='balanced'?(a,b)=>['metro','rer','bus'].indexOf(a.mode)-['metro','rer','bus'].indexOf(b.mode)||a.lineName.localeCompare(b.lineName,'fr',{numeric:true}):(a,b)=>a.lineName.localeCompare(b.lineName,'fr',{numeric:true}));
 const summary=element('button',undefined,'place-summary'),detailId=prefix+'-detail-'+i,open=expanded.has(place.id);
 summary.type='button';summary.dataset.placeId=place.id;summary.setAttribute('aria-expanded',String(open));summary.setAttribute('aria-controls',detailId);
 const row1=element('span',undefined,'summary-row place-heading'),title=element('h2',place.name,'place-name');title.title=place.name;
 row1.append(element('span','📍','place-pin'),title,element('span',Math.ceil(place.distance)+' m','place-distance'),element('span',open?'⌃':'⌄','place-chevron'));
 const row2=element('span',undefined,'summary-row'),row3=element('span',undefined,'summary-row');
 const walk='🚶 ≈ '+core.walkingMinutes(place.distance)+' min';
 const visible=lines.slice(0,2),hiddenLines=lines.length-visible.length;
 if(hiddenLines){const extra=element('span','＋'+hiddenLines,'summary-extra');extra.title=hiddenLines+' autres lignes dans le détail';row1.insertBefore(extra,row1.lastChild);}
 function renderLine(row,line){row.classList.add('line-senses-row');row.dataset.lineId=line.lineId;const logo=element('span',(line.mode==='bus'?'':icon(line.mode)+' ')+line.lineName,'line-badge compact-line mode-'+line.mode);logo.title=label(line.mode)+' '+line.lineName;logo.setAttribute('aria-label',logo.title);row.append(logo);
  const known=line.directions.filter(g=>g.gtfsDirectionId==='0'||g.gtfsDirectionId==='1'),unknown=line.directions.filter(g=>g.gtfsDirectionId===null);
  const slots=known.length?['0','1'].map(id=>known.find(g=>g.gtfsDirectionId===id)||null):[unknown[0]||null,null];
  slots.forEach((direction,index)=>{if(!direction){const absent=element('span','—','sense-cell sense-empty');absent.dataset.gtfsDirectionId=String(index);absent.setAttribute('aria-label','Pas de départ annoncé dans ce sens dans les 60 minutes');row.append(absent);return;}
   const cell=element('span',undefined,'sense-cell');cell.dataset.nextPlaceId=direction.nextPlaceId;cell.dataset.gtfsDirectionId=direction.gtfsDirectionId??'unknown';const name=element('span',(direction.gtfsDirectionId===null?'Sens ? · ':'')+direction.nextName,'sense-name');name.title=direction.nextName;
   const time=element('span',undefined,'sense-time'),next=logic.compactWait(direction.events[0].view);time.append(element('strong',next,'sense-next'));if(direction.events[1]){const following=element('small',' ('+logic.compactWait(direction.events[1].view)+')','sense-following');following.title='Suivant vers '+direction.events[1].event.destinationName;time.append(following);}
   cell.setAttribute('aria-label',label(line.mode)+' '+line.lineName+' '+(direction.gtfsDirectionId===null?'sens non renseigné':'sens GTFS '+direction.gtfsDirectionId)+' vers '+direction.nextName+' : '+direction.events[0].view.label+(direction.events[1]?', puis '+direction.events[1].view.label+' vers '+direction.events[1].event.destinationName:''));cell.append(name,time);row.append(cell);});

  if(line.directions.length>2){const more=element('span','＋'+(line.directions.length-2),'sense-variants');more.title='Autres premiers arrêts dans le détail';row.append(more);}
 }
 if(visible[0])renderLine(row2,visible[0]);if(visible[1])renderLine(row3,visible[1]);else row3.append(element('span',walk,'summary-walk'),element('span',partial?'⚠ Partiel · ⌄ Détails':'⌄ Détails','summary-more'));

 summary.append(row1,row2,row3);const detail=element('div',undefined,'place-detail');detail.id=detailId;detail.hidden=!open;
 detail.append(element('p',Math.ceil(place.distance)+' m à vol d’oiseau · '+walk+' de marche indicative','muted'),list,element('small',(partial?'⚠ Certains horaires sont indisponibles · ':'')+'Horaires théoriques · 60 prochaines minutes · lignes au point utile le plus proche · perturbations non connues'));
 const walking=element('button','🚶 Y aller à pied','walk-button');walking.type='button';walking.onclick=()=>window.WenareWalkingUI?.open(place);detail.append(walking);
 summary.onclick=()=>{if(expanded.has(place.id))expanded.delete(place.id);else expanded.add(place.id);render();};
 card.append(summary,detail);$(target).append(card);
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
function ensureTimetable(){if(window.WenareTimetable?.bundleVersion==='2026-11-08.18'&&typeof window.WenareTimetable.loadMany==='function')return Promise.resolve();if(!timetableReady)timetableReady=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='./timetable.js?v=18';script.onload=()=>window.WenareTimetable?.bundleVersion==='2026-11-08.18'&&typeof window.WenareTimetable.loadMany==='function'?resolve():reject(new Error('CLIENT_UPDATE_REQUIRED'));script.onerror=()=>reject(new Error('CLIENT_UPDATE_REQUIRED'));document.head.append(script);}).catch(error=>{timetableReady=null;throw error;});return timetableReady;}
async function loadQueries(queries,mine,pool){
 await Promise.allSettled(['metro','extra'].map(async mode=>{const src=sources[mode],needed=new Set(queries.filter(s=>(s.mode==='metro'?'metro':'extra')===mode&&!results.has(s.key)).map(s=>s.lineId)),q=[...new Map(pool.flatMap(p=>p.services).filter(s=>needed.has(s.lineId)&&!results.has(s.key)).map(s=>[s.key,s])).values()];if(!src||!q.length)return;try{await ensureTimetable();if(mine!==sequence)return;const rows=await WenareTimetable.loadMany(q,src.sha,controller.signal,mode==='metro'?'./distribution/timetable/':'./distribution/mobility/',true);if(mine!==sequence)return;for(const row of rows)results.set(row.query.key,{...row,clock:row.response?{server:Date.parse(row.response.serverTimeUtc),mono:performance.now(),wall:Date.now()}:null});}catch(error){if(mine!==sequence)return;for(const service of q)results.set(service.key,{error:'Horaires temporairement indisponibles.'});}}));
}
async function departures(mine){if(mine!==sequence||document.hidden||loading)return;loading=true;
 const domainRadii=window.WenareOpportunitiesUI?.radii();const radii=manualRadius?[radius]:domainRadii||logic.RADII.filter(r=>r<=3000);
 if(window.WenareOpportunitiesUI?.transportNeeded()===false){radius=radii[0];scanned=[];railScanned=[];loading=false;render();return;}
 for(const current of radii){if(mine!==sequence)return;radius=current;const pool=candidates.filter(p=>p.distance<=radius);scanned=[];
  for(let i=0;i<pool.length;i+=3){if(mine!==sequence)return;const batch=pool.slice(i,i+3);await loadQueries([...new Map(batch.flatMap(p=>p.services).map(s=>[s.key,s])).values()],mine,pool);if(mine!==sequence)return;scanned.push(...batch);render();if(places.length===3)break;}
  select();if(places.length||manualRadius)break;
 }
 if(mine!==sequence||document.hidden)return;
 const railPool=candidates.filter(p=>p.distance<=radius&&p.services.some(s=>s.mode==='metro'||s.mode==='rer')).map(p=>({...p,services:p.services.filter(s=>s.mode==='metro'||s.mode==='rer')}));railScanned=[];
 for(let i=0;i<railPool.length;i+=3){if(mine!==sequence)return;const batch=railPool.slice(i,i+3);await loadQueries([...new Map(batch.flatMap(p=>p.services).map(s=>[s.key,s])).values()],mine,railPool);if(mine!==sequence)return;railScanned.push(...batch);render();if(railPlaces.length===3)break;}
 if(mine!==sequence||document.hidden)return;loading=false;render();say(dataIssues?'⚠ Certains horaires sont indisponibles ou expirés. Départs vérifiés uniquement.':places.length?'🕒 60 prochaines minutes · les sens de départ sont regroupés.':'🔎 Aucun départ dans les 60 minutes dans ce rayon.');
 $('nearbyOverviewAge').textContent='Position reçue à '+new Date(lastFix.timestamp).toLocaleTimeString('fr-FR',{timeZone:'Europe/Paris'})+' · précision ±'+Math.round(lastFix.coords.accuracy)+' m'+(lastFix.coords.accuracy>100?' · l’ordre des points proches peut être incertain.':'')+(Array.from(results.values()).some(r=>r.response?.clockSource==='device')?' · horaires calculés avec l’horloge de l’appareil.':'');
 clearInterval(tick);tick=setInterval(()=>{render();if(!loading&&((places.length<3&&(scanned.length<candidates.filter(p=>p.distance<=radius).length||(!manualRadius&&!places.length&&radius<3000)))||(railPlaces.length<3&&railScanned.length<candidates.filter(p=>p.distance<=radius&&p.services.some(s=>s.mode==='metro'||s.mode==='rer')).length)))departures(sequence);},1000);clearTimeout(timer);timer=setTimeout(()=>{if(enabled&&!document.hidden)start();},60000);
}
async function start(){window.dispatchEvent(new Event('wenare:restart'));enabled=true;$('manualOptions').open=false;cancel();if(document.hidden)return;controller=new AbortController();const mine=sequence;say('Wenare vous localise et prépare vos départs…');$('nearbyOverviewAge').textContent='';
 const catalogue=catalogues(mine);
 if(!navigator.geolocation){fallback('Localisation indisponible sur cet appareil. La recherche manuelle reste disponible.');return;}
 let position;try{position=await new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:15000,maximumAge:15000}));}catch(error){if(mine===sequence)fallback(error.code===1?'Autorisez la localisation pour voir vos départs automatiquement. Vous pouvez aussi rechercher un arrêt manuellement.':'Position indisponible. La recherche manuelle reste disponible.');return;}
 if(mine!==sequence)return;if(!logic.validPosition(position.coords,position.timestamp)){fallback('Position trop ancienne ou imprécise. Réessayez ou recherchez un arrêt manuellement.');return;}lastFix=position;const stations=await catalogue;if(mine!==sequence||!stations)return;if(!stations.length){fallback('Données indisponibles pour proposer des départs. La recherche manuelle reste disponible.');return;}
 candidates=core.nearby(stations,{lat:position.coords.latitude,lon:position.coords.longitude},stations.length);places=[];render();say('Vos points de départ sont trouvés. Chargement des horaires de toutes les lignes…');await departures(mine);
}
document.querySelectorAll('[data-radius]').forEach(button=>button.onclick=async()=>{if(!lastFix||!enabled||!candidates.length)return;manualRadius=true;radius=Number(button.dataset.radius);cancel();controller=new AbortController();places=[];render();say('Chargement des horaires dans le rayon choisi…');await departures(sequence);});
document.querySelectorAll('button[data-view]').forEach(button=>button.onclick=()=>{view=button.dataset.view;try{localStorage.setItem('wenare-overview-view',view);}catch{}render();});
controls();
$('nearbyRestart').onclick=start;$('nearbyPause').onclick=()=>{enabled=false;cancel();say('Localisation et actualisation arrêtées.');$('nearbyOverviewAge').textContent='';};
$('manualOptions').addEventListener('toggle',()=>{if($('manualOptions').open&&enabled){enabled=false;cancel();say('Options manuelles ouvertes · actualisation automatique suspendue.');}});
$('eraseNetwork').addEventListener('click',()=>{enabled=false;cancel();say('Données locales effacées. Relancez la localisation pour les recharger.');});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancel();say('Consultation suspendue pendant votre absence.');}else if(enabled)start();});
 window.addEventListener('pageshow',event=>{if(event.persisted&&enabled)start();});
 window.WenareOverview={refreshDomain(){if(!enabled||!lastFix||!candidates.length)return;cancel(false);loading=false;scanned=[];railScanned=[];controller=new AbortController();render();departures(sequence);}};
 start();
})();

