/* Shared category colours and lossless map grouping, without network or GPS access. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WenarePlacesMap=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){'use strict';
const COLORS=Object.freeze({transport:'#2463ad',food:'#ba481b',events:'#8841a5',walk:'#2a7540',needs:'#167d85',sport:'#b02d65',shop:'#98620b',work:'#5454a4',sleep:'#655344',health:'#a82f35'});
function valid(p){return p&&Object.hasOwn(COLORS,p.category)&&typeof p.id==='string'&&typeof p.name==='string'&&Number.isFinite(p.lat)&&Math.abs(p.lat)<=85&&Number.isFinite(p.lon)&&Math.abs(p.lon)<=180&&Number.isFinite(p.distance)&&p.distance>=0;}
function select(sources,category,radius){const seen=new Set();return sources.flat().filter(p=>{if(!valid(p)||p.distance>radius||(category!=='all'&&p.category!==category))return false;const key=p.category+'|'+p.id;if(seen.has(key))return false;seen.add(key);return true;});}
function group(items,zoom){const size=256*2**zoom,grid=new Map();for(const p of items){const sin=Math.sin(p.lat*Math.PI/180),x=(p.lon+180)/360*size,y=(.5-Math.log((1+sin)/(1-sin))/(4*Math.PI))*size,key=Math.floor(x/48)+','+Math.floor(y/48);if(!grid.has(key))grid.set(key,[]);grid.get(key).push(p);}return [...grid.values()].map(rows=>({items:rows,lat:rows.reduce((a,p)=>a+p.lat,0)/rows.length,lon:rows.reduce((a,p)=>a+p.lon,0)/rows.length,categories:[...new Set(rows.map(p=>p.category))]}));}
return {COLORS,valid,select,group};
});
