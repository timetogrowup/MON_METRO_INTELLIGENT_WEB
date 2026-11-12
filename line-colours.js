/* Official line colours. Only six-digit hexadecimal source values become CSS. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.WenareLineColours=api})(typeof globalThis!=='undefined'?globalThis:this,function(){'use strict';
function hex(value){if(typeof value!=='string')return null;const colour=value.trim().replace(/^#/,'');return /^[0-9a-f]{6}$/i.test(colour)?'#'+colour.toUpperCase():null;}
function contrastText(background){const channels=background.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4),light=.2126*channels[0]+.7152*channels[1]+.0722*channels[2];return (light+.05)/.05>=1.05/(light+.05)?'#000000':'#FFFFFF';}
function palette(line){const background=hex(line?.route_color);if(!background)return null;return {background,text:hex(line?.route_text_color)||contrastText(background)};}
function apply(element,colours){if(!colours)return element;element.dataset.officialColour=colours.background;element.style.setProperty('background-color',colours.background,'important');element.style.setProperty('background-image','none','important');element.style.setProperty('color',colours.text,'important');return element;}
return {hex,palette,apply};
});

