(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WenareGoogleFood=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){'use strict';
 const RADII=[250,500,1000,3000];
 function context(snapshot,now=Date.now()){
  const p=snapshot?.position,c=p?.coords;
  if(!snapshot?.enabled||!RADII.includes(snapshot.radius)||!c||!Number.isFinite(c.latitude)||!Number.isFinite(c.longitude)||Math.abs(c.latitude)>90||Math.abs(c.longitude)>180||!Number.isFinite(c.accuracy)||c.accuracy<0||c.accuracy>500||!Number.isFinite(p.timestamp)||now-p.timestamp>120000||p.timestamp-now>5000)return null;
  return {lat:c.latitude,lng:c.longitude,radius:snapshot.radius};
 }
 function validRequest(p){return p&&Number.isFinite(p.lat)&&Math.abs(p.lat)<=90&&Number.isFinite(p.lng)&&Math.abs(p.lng)<=180&&RADII.includes(p.radius);}
 function validKey(k){return typeof k==='string'&&/^[A-Za-z0-9_-]{20,200}$/.test(k);}
 function identity(c){return c?JSON.stringify([c.lat,c.lng,c.radius]):null;}
 return {context,validRequest,validKey,identity};
});
