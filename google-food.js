(function(){'use strict';
 const $=id=>document.getElementById(id),core=WenareGoogleFood,panel=$('googleFoodPanel');
 let category='all',snapshot=null,frame=null,pending=null,sequence=0,timer=null,launched=0,busy=false,currentIdentity=null;
 function say(text){$('googleFoodStatus').textContent=text;}
 function clear(message){sequence++;clearTimeout(timer);timer=null;pending=null;frame?.remove();frame=null;busy=false;$('googleFoodCancel').hidden=true;if(message)say(message);}
 function sync(){const c=core.context(snapshot),id=core.identity(c),visible=category==='food';panel.hidden=!visible;
  if((!visible||id!==currentIdentity)&&frame)clear(visible?'Position ou rayon modifié. Relancez explicitement la recherche Google.':'');
  currentIdentity=id;$('googleFoodRadius').textContent=c?'Rayon partagé : '+c.radius.toLocaleString('fr-FR')+' m.':'Une position récente est nécessaire. Utilisez « Me relocaliser ».';
  $('googleFoodSearch').disabled=busy||!visible||!c;
  if(!snapshot?.enabled){$('googleFoodKey').value='';if(frame)clear('Complément Google fermé.');}
 }
 async function search(){const c=core.context(snapshot),key=$('googleFoodKey').value.trim();
  if(category!=='food'||!c){say('Relocalisez-vous avant de lancer le complément Google.');return;}
  if(!core.validKey(key)){$('googleFoodSettings').open=true;$('googleFoodKey').focus();say('Ajoutez votre clé de test restreinte au site WENARE.');return;}
  clear();busy=true;const mine=sequence;pending={key,context:c};frame=document.createElement('iframe');frame.title='Restaurants proches — résultats Google Maps';frame.className='google-food-frame';frame.src='./google-food-frame.html?v=21';frame.referrerPolicy='strict-origin-when-cross-origin';$('googleFoodResults').replaceChildren(frame);$('googleFoodCancel').hidden=false;launched++;$('googleFoodCount').textContent=launched+' recherche'+(launched>1?'s':'')+' lancée'+(launched>1?'s':'')+' pendant cette ouverture (hors facturation Google).';say('Chargement du complément Google…');sync();
  timer=setTimeout(()=>{if(mine!==sequence)return;clear('Google ne répond pas. Vérifiez la connexion, la facturation, les API activées et les restrictions de la clé, puis réessayez.');sync();},30000);
 }
 window.addEventListener('message',e=>{if(!frame||e.source!==frame.contentWindow||e.origin!==location.origin||e.data?.channel!=='wenare-google-food')return;
  const m=e.data;if(m.type==='ready'&&pending){const p=pending;pending=null;frame.contentWindow.postMessage({channel:'wenare-google-food',type:'search',...p},location.origin);}
  else if(m.type==='loaded'){clearTimeout(timer);timer=null;busy=false;say('Résultats Google chargés. Au maximum 20 propositions, sans garantie d’exhaustivité ni de disponibilité.');sync();}
  else if(m.type==='error'){clear('Complément Google indisponible. Vérifiez la connexion, la facturation, les API activées et les restrictions de votre clé. Les résultats habituels restent disponibles.');sync();}
  else if(m.type==='height'&&Number.isFinite(m.height)){frame.style.height=Math.max(280,Math.min(1000,Math.ceil(m.height)))+'px';}
 });
 window.addEventListener('wenare:overview',e=>{snapshot=e.detail;sync();});
 window.addEventListener('wenare:domain',e=>{category=e.detail.category;sync();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){clear('Complément Google fermé pendant votre absence.');sync();}});
 window.addEventListener('pagehide',()=>{clear();$('googleFoodKey').value='';});
 $('googleFoodSearch').onclick=search;$('googleFoodCancel').onclick=()=>{clear('Complément Google fermé. Aucun renouvellement automatique.');sync();};
 $('googleFoodKey').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();search();}});
 setInterval(()=>{if(frame&&!core.context(snapshot)){clear('Position trop ancienne. Relocalisez-vous avant une nouvelle recherche.');sync();}},10000);
 sync();
})();
