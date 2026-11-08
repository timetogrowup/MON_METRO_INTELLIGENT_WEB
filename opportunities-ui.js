(function(){'use strict';
const core=WenareOpportunities,$=id=>document.getElementById(id),el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
let category='all',snapshot=null,catalogue=null,error=null,key=null,stopped=false,request=0,controller=null,resultCount=0;
const expanded=new Set();
function position(){const c=snapshot?.position?.coords;return c?{lat:c.latitude,lon:c.longitude}:null;}
function radiusStatus(){if(!snapshot)return;const count=category==='transport'?(snapshot.transportCount||0):category==='all'?(snapshot.transportCount||0)+resultCount:resultCount;$('radiusStatus').textContent=(snapshot.manualRadius?'📍 ':'✨ Auto · ')+snapshot.radius.toLocaleString('fr-FR')+' m · '+count+' lieu'+(count===1?'':'x');}
function relevant(){if(!catalogue)return [];return category==='all'?Object.values(catalogue.items).flat():catalogue.items[category]||[];}
function radii(){const p=position();if(!p||!catalogue||category==='transport')return null;const rows=relevant();if(category==='all'&&!core.select(rows,p,3000,Date.now(),1).length)return null;const r=core.automaticRadius(rows,p);return category==='all'?core.RADII.filter(x=>x<=r):[r];}
function link(text,url){const a=el('a',text);a.href=core.safeUrl(url)||'#';a.target='_blank';a.rel='noopener noreferrer';return a;}
function status(p){if(p.category==='health')return 'Garde non renseignée';if(p.category==='sleep')return 'Disponibilités à vérifier';if(p.category==='events')return 'Horaire à vérifier';if(p.category==='sport')return 'Créneaux à vérifier';if(p.category==='work')return 'Places non renseignées';if(p.availability==='declared-in-service')return 'En service déclaré';return p.openingHours?'Horaires déclarés':'Ouverture non renseignée';}
function card(p){const c=core.CATEGORIES.find(c=>c.id===p.category),a=el('article',undefined,'opportunity-card'),b=el('button',undefined,'opportunity-summary'),row1=el('span',undefined,'opportunity-row opportunity-heading'),row2=el('span',undefined,'opportunity-row'),row3=el('span',undefined,'opportunity-row opportunity-meta'),title=el('span',c.icon+' '+p.name,'opportunity-name'),detail=el('div',undefined,'opportunity-detail');
 a.dataset.category=p.category;a.dataset.sourceId=p.id;title.title=p.name;b.type='button';b.dataset.opportunityId=p.id;detail.id='opportunity-'+p.category+'-'+String(p.id).replace(/[^a-zA-Z0-9]/g,'-');b.setAttribute('aria-controls',detail.id);const open=expanded.has(p.category+'|'+p.id);b.setAttribute('aria-expanded',String(open));detail.hidden=!open;
 row1.append(title,el('span',Math.ceil(p.distance)+' m','opportunity-distance'),el('span',open?'⌃':'⌄','opportunity-chevron'));
 row2.append(el('span',status(p),'opportunity-status'));
 if(p.fee==='no')row2.append(el('span','Gratuit déclaré','opportunity-chip'));if(p.access==='yes')row2.append(el('span','♿ Déclaré','opportunity-chip'));
 row3.append(el('span','🚶 ≈ '+Math.max(1,Math.ceil(p.distance/80))+' min'),el('span',p.category==='events'?'Aujourd’hui · Détails':'ⓘ Détails','opportunity-more'));
 b.append(row1,row2,row3);detail.append(el('p',p.address||'Adresse non renseignée'),el('p',c.limit+'. Aucun accueil immédiat garanti.'));
 if(p.description)detail.append(el('p',p.description));
 if(p.openingHours)detail.append(el('p','Horaires transmis par la source, à vérifier : '+p.openingHours));
 if(p.category==='events')detail.append(el('p','La période inclut aujourd’hui ; elle ne prouve pas une séance en cours ou dans les 60 minutes. Consultez les horaires de l’organisateur avant de vous déplacer.'));
 if(p.positionKind==='centroid')detail.append(el('p','Distance calculée vers le centre cartographique du lieu, pas vers une entrée vérifiée.'));
 const walk=el('button','🚶 Y aller à pied','walk-button');walk.type='button';walk.onclick=()=>window.WenareWalkingUI?.open(p);detail.append(walk);
 const source=catalogue.manifest.sources[p.source];detail.append(link('Consulter la fiche du lieu ↗',p.url));
 const provenance=el('p',undefined,'opportunity-source');provenance.append(el('span','Source : '+source.name+(p.producer?' · '+p.producer:'')+'. '),link(source.license,source.licenseUrl),el('span',' · fiche mise à jour : '+(p.modified||'date non renseignée')+'. Collecte du catalogue : '+new Date(catalogue.manifest.collectedAt).toLocaleDateString('fr-FR')+'.'));
 detail.append(provenance);b.onclick=()=>{const id=p.category+'|'+p.id;if(expanded.has(id))expanded.delete(id);else expanded.add(id);detail.hidden=!expanded.has(id);b.setAttribute('aria-expanded',String(!detail.hidden));row1.lastChild.textContent=detail.hidden?'⌄':'⌃';};a.append(b,detail);return a;
}
function render(force=false){
 window.dispatchEvent(new CustomEvent('wenare:domain',{detail:{category}}));
 const p=position(),active=category==='all'||category==='transport';$('transportOverview').hidden=!active;$('nearbyOverviewStatus').hidden=!!p&&!active;
 $('domainAll').setAttribute('aria-pressed',String(category==='all'));document.querySelectorAll('[data-domain]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.domain===category)));
 const identity=JSON.stringify([category,snapshot?.radius,snapshot?.manualRadius,snapshot?.position?.timestamp,!!catalogue,error,stopped,core.parisDay()]);if(!force&&identity===key){radiusStatus();return;}key=identity;
 $('opportunityOverview').replaceChildren();if(category==='transport'){radiusStatus();return;}
 const selected=core.CATEGORIES.filter(c=>c.id!=='transport'&&(category==='all'||category===c.id));let total=0;
 for(const c of selected){const section=el('section',undefined,'opportunity-section'),h=el('h3',c.icon+' '+c.title,'opportunity-title'),rows=catalogue&&p?core.select(catalogue.items[c.id]||[],p,snapshot.radius):[];
 h.append(el('span',rows.length?' '+rows.length+' lieu'+(rows.length>1?'x':''):'' ,'opportunity-count'));section.append(h);
 if(rows.length){total+=rows.length;rows.forEach(row=>section.append(card(row)));}
 else{let message=stopped?'Consultation arrêtée. Relocalisez-vous pour reprendre.':!p?'Localisez-vous pour découvrir les lieux proches.':error||catalogue?.errors[c.id]||(!catalogue?'Chargement des lieux…':'Aucune proposition référencée dans ce rayon. La couverture peut être partielle.');section.append(el('p',message,'opportunity-empty'));}
 $('opportunityOverview').append(section);
 }
 if(catalogue){const note=el('small','Couverture partielle · catalogue du '+new Date(catalogue.manifest.collectedAt).toLocaleDateString('fr-FR')+' · lieux référencés, disponibilités non confirmées.','opportunity-foot');$('opportunityOverview').append(note);}
 resultCount=total;radiusStatus();$('domainResultsStatus').textContent=p&&!stopped?(category==='all'?total+' autres lieux proposés':total+' lieu'+(total>1?'x':'')+' proposé'+(total>1?'s':'')):'Position nécessaire pour les autres domaines.';
}
async function load(){controller?.abort();controller=new AbortController();const mine=++request;try{const next=await core.load(controller.signal);if(mine!==request||stopped)return;catalogue=next;error=null;render(true);if(snapshot?.position)window.WenareOverview?.refreshDomain();}catch(e){if(mine!==request||e.name==='AbortError')return;error='Catalogue indisponible ou expiré. Réessayez avec une connexion.';render(true);}finally{if(mine===request)controller=null;}}
for(const c of core.CATEGORIES){const b=el('button',undefined,'domain-button');b.type='button';b.dataset.domain=c.id;b.setAttribute('aria-pressed','false');const icon=el('span',c.icon,'domain-icon');icon.setAttribute('aria-hidden','true');b.append(icon,el('span',c.short));b.onclick=()=>{category=c.id;render(true);window.WenareOverview?.refreshDomain();};$('domainChoices').append(b);}
document.querySelector('#domainAll').onclick=()=>{category='all';render(true);window.WenareOverview?.refreshDomain();};
window.addEventListener('wenare:overview',e=>{snapshot=e.detail;const was=stopped;stopped=!snapshot.enabled;if(stopped){request++;controller?.abort();}else if(was&&!catalogue)load();render();});
window.WenareOpportunitiesUI={radii,transportNeeded:()=>category==='all'||category==='transport'};
setInterval(()=>{if(document.hidden||stopped)return;if(catalogue&&Date.now()>=Date.parse(catalogue.manifest.validUntilUtc)){catalogue=null;error='Catalogue expiré. Relocalisez-vous avec une connexion pour l’actualiser.';}render();},60000);
window.addEventListener('wenare:restart',()=>{if(!controller&&(!catalogue||error||Object.keys(catalogue.errors).length)){stopped=false;load();}});
render();load();
})();
