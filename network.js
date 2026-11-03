/* Versioned network cache, separate from the legacy 803-association database. */
(function(global){
'use strict';
const DB='mmi-network-v1';
function open(){return new Promise((resolve,reject)=>{const r=indexedDB.open(DB,1);r.onupgradeneeded=()=>r.result.createObjectStore('versions');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}
async function read(){const db=await open();try{const records=await new Promise((resolve,reject)=>{const tx=db.transaction('versions'),store=tx.objectStore('versions'),a=store.get('current'),b=store.get('previous');tx.oncomplete=()=>resolve([a.result,b.result]);tx.onerror=()=>reject(tx.error)});if(!records[0]&&!records[1])return undefined;for(let i=0;i<records.length;i++){const record=records[i];if(!record)continue;try{const data=await validate(record.bytes,record.manifest);if(i===1)await new Promise((resolve,reject)=>{const tx=db.transaction('versions','readwrite');tx.objectStore('versions').put(record,'current');tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)});return {...record,data,recovered:i===1}}catch(e){if(i===1)throw e}}throw new Error('Cache réseau corrompu ; actualisez le référentiel')}finally{db.close()}}
async function save(record,previous){const db=await open();try{await new Promise((resolve,reject)=>{const tx=db.transaction('versions','readwrite'),s=tx.objectStore('versions');try{if(previous)s.put(previous,'previous');s.put(record,'current')}catch(e){tx.abort();reject(e)}tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error||new Error('Transaction annulée'))})}finally{db.close()}}
async function rollback(){const db=await open();try{await new Promise((resolve,reject)=>{const tx=db.transaction('versions','readwrite'),s=tx.objectStore('versions'),r=s.get('previous');r.onsuccess=()=>{if(!r.result){tx.abort();return}s.put(r.result,'current')};tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(new Error('Version précédente indisponible'))})}finally{db.close()}return read()}
async function validate(bytes,m){
 if(m.schema_version!==1||m.bytes!==bytes.byteLength)throw new Error('Schéma ou taille invalide');
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');
 if(digest!==m.sha256)throw new Error('Empreinte du référentiel invalide');
 const data=JSON.parse(new TextDecoder().decode(bytes));
 if(data.schema_version!==1||data.service_date!==m.service_date)throw new Error('Version incohérente');
 for(const name of ['stations','patterns','lines','stops','segments'])if(!Array.isArray(data[name])||data[name].length!==m.counts[name])throw new Error('Données incomplètes : '+name);
 return data;
}
async function update(base='./distribution/'){
 const response=await fetch(base+'manifest.json',{cache:'no-store'});if(!response.ok)throw new Error('Manifeste indisponible');const m=await response.json();
 if(m.file!=='network.json')throw new Error('Chemin de données refusé');
 const current=await read().catch(()=>null);if(current&&current.manifest.sha256===m.sha256)return current;
 const payload=await fetch(base+m.file,{cache:'no-store'});if(!payload.ok)throw new Error('Référentiel indisponible');
 const bytes=await payload.arrayBuffer(),data=await validate(bytes,m),record={manifest:m,data,bytes};await save(record,current);return record;
}
function currentDay(){return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Paris',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())}
function describe(record){if(!record)return 'Les données du métro sont à installer sur cet appareil.';const c=record.manifest.counts;return (record.recovered?'Version précédente restaurée après corruption · ':'')+c.stations+' stations · '+c.lines+' lignes · services du '+record.data.service_date+(record.data.service_date===currentDay()?'':' · actualisez les données pour poursuivre la localisation')}
global.MMIReference={read,update,rollback,validate,describe,currentDay};
})(typeof window==='undefined'?globalThis:window);
