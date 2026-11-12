const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto').webcrypto;
globalThis.crypto=crypto;
const mobility=require('../mobility.js'),nearby=require('../nearby.js');
test('regional client accepts each new mode with validated manifest bindings',async()=>{
 const original=JSON.parse(fs.readFileSync('distribution/mobility/index.json')),base=JSON.parse(fs.readFileSync('distribution/mobility/manifest.json'));
 for(const mode of ['tram','train','ter','shuttle','cable','funicular']){
  const d=structuredClone(original),m=structuredClone(base),id='IDFM:C99999';d.lines.push({route_id:id,route_short_name:'Fixture',mode,operator:'Fixture'});d.coverage[id]='no_dated_departures';m.scope.C99999=mode;m.lines[id]={file:'IDFM-C99999.json'};
  let bytes=Buffer.from(JSON.stringify(d));m.index.bytes=bytes.length;m.index.sha256=m.networkSha256=Buffer.from(await crypto.subtle.digest('SHA-256',bytes)).toString('hex');
  await mobility.validate(bytes,m,Date.parse(m.validFromUtc)+1000);
  d.lines.at(-1).mode='unknown';bytes=Buffer.from(JSON.stringify(d));m.index.bytes=bytes.length;m.index.sha256=m.networkSha256=Buffer.from(await crypto.subtle.digest('SHA-256',bytes)).toString('hex');
  await assert.rejects(mobility.validate(bytes,m,Date.parse(m.validFromUtc)+1000));
 }
});
test('new modes remain visible in the complementary section when buses fill nearby points',()=>{
 const buses=[0,1,2].map(i=>({id:'bus'+i,distance:i,services:[{lineId:'bus'+i,mode:'bus'}]}));
 for(const mode of ['tram','train','ter','shuttle','cable','funicular']){
  const rail={id:mode,distance:10,services:[{lineId:mode,mode}]},places=[...buses,rail],groups=new Map(places.map(p=>[p.id,[{lineId:p.id,mode:p.services[0].mode,events:[{}]}]]));
  const result=nearby.selectSections(places,groups);assert.equal(result.primary.length,3);assert.deepEqual(result.rail.map(p=>p.id),[mode]);
 }
});
