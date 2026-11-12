/* Shared explicit theme selection. Restored before first paint. */
(function(){'use strict';
const themes=[
 ['pop','Pop','Joyeuse','#a51261','#fff0f6','#ffffff','#39142c','system-ui','saturate(1.3)'],
 ['funk','Funk / Disco','Funky','#813099','#fff4db','#fffdf5','#392544','system-ui','sepia(.25) saturate(1.6)'],
 ['reggae','Reggae','Décontractée','#216339','#fff8df','#fffdf3','#253f2c','system-ui','sepia(.35) saturate(1.15)'],
 ['rock','Rock','Audacieuse','#a92c32','#191c22','#262b33','#f9f1e9','system-ui','grayscale(.9) brightness(.65)'],
 ['jazz','Jazz vintage','Élégante','#855027','#f3e9d6','#fff9ee','#473322','Georgia,serif','sepia(.6)'],
 ['electro','Électro / Dance','Énergique','#824bdb','#141b30','#232d45','#f0edff','system-ui','invert(.86) hue-rotate(180deg) saturate(.7)'],
 ['bossa','Bossa nova','Sereine','#246c68','#e9f5ef','#fbfffa','#203c3b','system-ui','saturate(.65)'],
 ['soul','Soul','Romantique','#a02d55','#faeaf0','#fff7f9','#522a3d','Georgia,serif','sepia(.2) saturate(.8)'],
 ['folk','Folk','Aventureuse','#59662b','#f0efde','#fffdf2','#354127','Georgia,serif','sepia(.35)'],
 ['lofi','Lo-fi / Jazz instrumental','Concentrée','#52618d','#edf0f7','#fbfcff','#303b52','system-ui','saturate(.3)'],
 ['ambient','Ambient','Rêveuse','#73528f','#f0ebf7','#fcf9ff','#493657','system-ui','saturate(.45) hue-rotate(15deg)'],
 ['swing','Swing électro','Pétillante','#166a80','#e6f5f7','#faffff','#243e49','system-ui','saturate(1.4)']
];
const root=document.documentElement,key='wenare-theme';
function select(id,persist=true){const t=themes.find(t=>t[0]===id);if(!t)return false;root.dataset.wenareStyle=t[0];for(const [k,v]of Object.entries({accent:t[3],page:t[4],surface:t[5],ink:t[6],font:t[7],'map-filter':t[8]}))root.style.setProperty('--wenare-'+k,v);const meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.content=t[3];if(persist)try{localStorage.setItem(key,t[0]);}catch{}window.dispatchEvent(new CustomEvent('wenare:style',{detail:{id:t[0],name:t[1]}}));return true;}
window.WenareThemes={select,list:themes.map(t=>({id:t[0],name:t[1],accent:t[3],page:t[4],surface:t[5],ink:t[6]}))};
let saved;try{saved=localStorage.getItem(key);}catch{}if(!select(saved,false))select('pop',false);
})();
