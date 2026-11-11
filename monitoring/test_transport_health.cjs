const assert=require('node:assert/strict'),{assess}=require('../transport-health.js');
const now=Date.parse('2026-11-11T12:00:00Z');
for(const [hours,state] of [[30,'healthy'],[18,'healthy'],[17.99,'warning'],[0,'expired'],[-1,'expired']])assert.equal(assess({validFromUtc:new Date(now-86400000).toISOString(),validUntilUtc:new Date(now+hours*3600000).toISOString()},now).state,state);
assert.equal(assess({},now).state,'invalid');assert.equal(assess({validFromUtc:new Date(now+1000).toISOString(),validUntilUtc:new Date(now+86400000).toISOString()},now).state,'future');
console.log('Transport health browser thresholds OK');
