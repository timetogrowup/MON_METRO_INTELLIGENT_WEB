(function(){'use strict';
 const channel='wenare-google-food',send=(type,extra={})=>parent.postMessage({channel,type,...extra},location.origin);let started=false;
 function error(){document.getElementById('frameStatus').textContent='Chargement Google indisponible.';send('error');}
 window.gm_authFailure=error;
 window.addEventListener('message',async e=>{
  if(started||e.source!==parent||e.origin!==location.origin||e.data?.channel!==channel||e.data.type!=='search')return;
  const {key,context}=e.data;if(!WenareGoogleFood.validKey(key)||!WenareGoogleFood.validRequest(context)){error();return;}started=true;
  document.getElementById('frameStatus').textContent='Recherche des restaurants proches…';
  try{
   await new Promise((resolve,reject)=>{window.wenareGoogleReady=resolve;const s=document.createElement('script');const url=new URL('https://maps.googleapis.com/maps/api/js');url.search=new URLSearchParams({key,v:'weekly',loading:'async',callback:'wenareGoogleReady',language:'fr',region:'FR'});s.src=url.href;s.async=true;s.onerror=reject;document.head.append(s);});
   await google.maps.importLibrary('places');await customElements.whenDefined('gmp-place-search');await customElements.whenDefined('gmp-place-nearby-search-request');
   const search=document.createElement('gmp-place-search'),content=document.createElement('gmp-place-all-content'),request=document.createElement('gmp-place-nearby-search-request');
   request.maxResultCount=20;request.includedPrimaryTypes=['restaurant','cafe','bakery'];request.rankPreference=google.maps.places.SearchNearbyRankPreference.DISTANCE;
   request.locationRestriction={center:{lat:context.lat,lng:context.lng},radius:context.radius};
   search.addEventListener('gmp-load',()=>{document.getElementById('frameStatus').hidden=true;send('loaded');});search.addEventListener('gmp-requesterror',error);
   search.append(content,request);document.getElementById('widget').replaceChildren(search);
   new ResizeObserver(()=>send('height',{height:document.documentElement.scrollHeight})).observe(document.body);
  }catch{error();}
 });
 if(parent!==window)send('ready');
})();
