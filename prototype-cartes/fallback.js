/* Canvas vector renderer for devices without WebGL2. Same IGN data and style. */
export async function canvasRenderer(initialStyle){
 const load=src=>new Promise((ok,no)=>{const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=()=>no(new Error('Moteur cartographique indisponible'));document.head.append(s);});
 const css=document.createElement('link');css.rel='stylesheet';css.href='https://cdn.jsdelivr.net/npm/ol@10.11.0/ol.css';document.head.append(css);
 if(!window.ol)await load('https://cdn.jsdelivr.net/npm/ol@10.11.0/dist/ol.js');
 if(!window.olms)await load('https://cdn.jsdelivr.net/npm/ol-mapbox-style@13.9.0/dist/olms.js');
 const ol=window.ol,olms=window.olms;document.getElementById('map').replaceChildren();
 const source=new ol.source.VectorTile({format:new ol.format.MVT(),url:'https://data.geopf.fr/tms/1.0.0/PLAN.IGN/{z}/{x}/{y}.pbf',maxZoom:18,attributions:'© IGN · Géoplateforme',cacheSize:128}),layer=new ol.layer.VectorTile({source,declutter:true,renderMode:'vector'});
 let style=JSON.parse(JSON.stringify(initialStyle)),timer=null,run=0;
 await olms.applyStyle(layer,style,'plan_ign',{updateSource:false});
 const raw=new ol.Map({target:'map',layers:[layer],controls:[new ol.control.Zoom(),new ol.control.Attribution({collapsible:false}),new ol.control.ScaleLine()],view:new ol.View({center:ol.proj.fromLonLat([2.0401,48.9325]),zoom:14.2,maxZoom:18})});
 const byId=new Map(style.layers.map(l=>[l.id,l]));
 const adapter={raw,engine:'canvas',getLayer:id=>byId.get(id),getPaintProperty:(id,key)=>byId.get(id)?.paint?.[key],getLayoutProperty:(id,key)=>byId.get(id)?.layout?.[key],setPaintProperty(id,key,value){const l=byId.get(id);l.paint=l.paint||{};if(value===null)delete l.paint[key];else l.paint[key]=value;},setLayoutProperty(id,key,value){const l=byId.get(id);l.layout=l.layout||{};l.layout[key]=value;},triggerRepaint(){clearTimeout(timer);const mine=++run;timer=setTimeout(async()=>{try{await olms.applyStyle(layer,JSON.parse(JSON.stringify(style)),'plan_ign',{updateSource:false});if(mine===run){raw.render();document.documentElement.dataset.styleApplied=String(mine);}}catch(e){document.getElementById('mapMessage').textContent='Le réglage n’a pas pu être appliqué. Réinitialisez le style.';document.getElementById('mapMessage').hidden=false;console.error(e);}},40);},jumpTo(camera){const view=raw.getView();if(camera.center)view.setCenter(ol.proj.fromLonLat(camera.center));if(camera.zoom!==undefined)view.setZoom(camera.zoom);if(camera.bearing!==undefined)view.setRotation(camera.bearing*Math.PI/180);}};
 class Marker{constructor(options){this.element=options.element;this.position=null;this.overlay=null;this.map=null;}setLngLat(point){this.position=point;if(this.overlay)this.overlay.setPosition(ol.proj.fromLonLat(point));return this;}addTo(map){this.map=map;this.overlay=new ol.Overlay({element:this.element,position:ol.proj.fromLonLat(this.position),positioning:'bottom-center',stopEvent:true});map.raw.addOverlay(this.overlay);return this;}remove(){if(this.overlay)this.map.raw.removeOverlay(this.overlay);this.overlay=null;}}
 return {map:adapter,lib:{Marker},raw};
}
