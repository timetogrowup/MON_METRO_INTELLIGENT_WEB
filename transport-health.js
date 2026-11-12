/* Operations keep the 18-hour prealert; users only see confirmed unavailability. */
(function(root){
'use strict';
const WARNING_HOURS=18;
function assess(manifest,now=Date.now()){
 const start=Date.parse(manifest?.validFromUtc),end=Date.parse(manifest?.validUntilUtc);
 if(!Number.isFinite(start)||!Number.isFinite(end)||start>=end)return {state:'invalid'};
 const hours=(end-now)/3600000;
 return {state:start>now?'future':hours<=0?'expired':hours<WARNING_HOURS?'warning':'healthy',hours,end};
}
if(typeof module!=='undefined')module.exports={assess};
if(typeof document==='undefined')return;
const host=document.getElementById('transportOverview');if(!host)return;
const panel=document.createElement('p');panel.id='transportHealth';panel.setAttribute('role','status');panel.setAttribute('aria-live','polite');panel.hidden=true;panel.style.cssText='padding:12px;border-radius:12px;background:#fff3d6;color:#503500;line-height:1.5';host.prepend(panel);
let busy=false;const known=new Map();
async function check(){
 if(busy||document.hidden)return;busy=true;
 try{
  const rows=await Promise.all(['timetable','mobility'].map(async folder=>{
   const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),10000);
   try{const r=await fetch('./distribution/'+folder+'/manifest.json?health='+Date.now(),{cache:'no-store',signal:abort.signal});if(!r.ok)throw new Error('HTTP '+r.status);const manifest=await r.json();const date=Date.parse(r.headers.get('Date')),age=Number(r.headers.get('Age')||0);const now=Number.isFinite(date)&&Number.isFinite(age)&&age>=0?date+age*1000:Date.now();const result=assess(manifest,now);if(result.state!=='invalid')known.set(folder,{manifest,server:now,wall:Date.now()});return {folder,...result};}catch{const previous=known.get(folder);return {folder,...(previous?assess(previous.manifest,previous.server+Date.now()-previous.wall):{state:'unreachable'})};}finally{clearTimeout(timer);}
  }));
  const messages=rows.filter(r=>['expired','invalid','future'].includes(r.state)).map(r=>{
   const name=r.folder==='timetable'?'Métro':'RER et bus';
   if(r.state==='expired')return name+' : horaires expirés, départs indisponibles. Réessayez dans quelques instants.';
   if(r.state==='unreachable')return name+' : validité des horaires impossible à vérifier. Vérifiez votre connexion.';
   return name+' : période de validité des horaires incorrecte, départs potentiellement indisponibles.';
  });console.debug('[WENARE transport]',rows);panel.textContent=messages.join(' ');panel.hidden=!messages.length;
 }finally{busy=false;}
}
check();setInterval(check,300000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)check();});window.addEventListener('online',check);
})(typeof globalThis!=='undefined'?globalThis:this);
