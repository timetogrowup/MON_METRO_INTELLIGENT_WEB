const assert=require('node:assert/strict'),{assess}=require('../transport-health.js');
const now=Date.parse('2026-11-11T12:00:00Z');
for(const [hours,state] of [[30,'healthy'],[18,'healthy'],[17.99,'warning'],[0,'expired'],[-1,'expired']])assert.equal(assess({validFromUtc:new Date(now-86400000).toISOString(),validUntilUtc:new Date(now+hours*3600000).toISOString()},now).state,state);
assert.equal(assess({},now).state,'invalid');assert.equal(assess({validFromUtc:new Date(now+1000).toISOString(),validUntilUtc:new Date(now+86400000).toISOString()},now).state,'future');
console.log('Transport health browser thresholds OK');
const vm=require('node:vm'),fs=require('node:fs');
async function checkPanel(hours,offline=false){
 let panel;const host={prepend:p=>{panel=p;}},doc={hidden:false,getElementById:id=>id==='transportOverview'?host:null,createElement:()=>({setAttribute(){},style:{}}),addEventListener(){}};
 const current=Date.now(),manifest={validFromUtc:new Date(current-86400000).toISOString(),validUntilUtc:new Date(current+hours*3600000).toISOString()};
 vm.runInNewContext(fs.readFileSync(require.resolve('../transport-health.js'),'utf8'),{document:doc,window:{addEventListener(){}},Date,AbortController,setTimeout,clearTimeout,setInterval(){},fetch:async()=>{if(offline)throw Error('offline');return {ok:true,headers:{get:()=>null},json:async()=>manifest};}});
 await new Promise(resolve=>setImmediate(resolve));return panel;
}
(async()=>{
 let panel=await checkPanel(30);assert.equal(panel.hidden,true,'Healthy data must not display an alarm');
 panel=await checkPanel(10);assert.equal(panel.hidden,false);assert.match(panel.textContent,/mise à jour attendue/);assert.match(panel.textContent,/RER et bus/);
 panel=await checkPanel(-1);assert.equal(panel.hidden,false);assert.match(panel.textContent,/horaires expirés/);
 panel=await checkPanel(30,true);assert.equal(panel.hidden,false);assert.match(panel.textContent,/impossible à vérifier/);
 console.log('Transport health UI OK: healthy, warning, expired and offline states');
})().catch(e=>{console.error(e);process.exit(1)});
