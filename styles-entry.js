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
const root=document.documentElement,$=id=>document.getElementById(id),gate=$('styleEntry'),reel=$('styleReel'),track=$('styleTrack'),status=$('styleEntryStatus'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
let frame=0,started=performance.now(),selected=0,stopping=false,opened=false;
window.WenareEntry={get opened(){return opened;},selectStyle(id){const index=themes.findIndex(t=>t[0]===id);if(index>=0)apply(index);}};
for(let n=0;n<3;n++)for(const t of themes){const row=document.createElement('span');row.className='style-row';row.textContent=t[1];track.append(row);}
function apply(index){const t=themes[index];root.dataset.wenareStyle=t[0];for(const [key,value] of Object.entries({accent:t[3],page:t[4],surface:t[5],ink:t[6],font:t[7],'map-filter':t[8]}))root.style.setProperty('--wenare-'+key,value);$('styleChange').textContent=t[1]+' · Changer';document.querySelector('meta[name="theme-color"]').content=t[3];window.dispatchEvent(new CustomEvent('wenare:style',{detail:{id:t[0],name:t[1]}}));}
function paint(now){if(stopping||document.hidden)return;const position=((now-started)/65)%themes.length;selected=Math.floor(position+.5)%themes.length;track.style.transform='translateY('+(-(themes.length+position)*64)+'px)';frame=requestAnimationFrame(paint);}
function finish(){gate.hidden=true;document.querySelector('main').inert=false;document.body.classList.remove('style-locked');if(!opened){opened=true;window.dispatchEvent(new Event('wenare:enter'));}reel.disabled=false;$('styleChange').focus({preventScroll:true});}
function choose(){if(stopping)return;stopping=true;cancelAnimationFrame(frame);reel.disabled=true;apply(selected);track.style.transition=reduced.matches?'none':'transform 240ms ease-out';track.style.transform='translateY('+(-(themes.length+selected)*64)+'px)';status.textContent=themes[selected][2]+' · '+themes[selected][1];setTimeout(finish,reduced.matches?0:650);}
function launch(){stopping=false;gate.hidden=false;document.querySelector('main').inert=true;document.body.classList.add('style-locked');track.style.transition='none';status.textContent='Touchez le rouleau pour choisir votre ambiance et entrer.';started=performance.now();if(reduced.matches){selected=Math.floor(Math.random()*themes.length);track.style.transform='translateY('+(-(themes.length+selected)*64)+'px)';}else frame=requestAnimationFrame(paint);reel.focus({preventScroll:true});}
reel.addEventListener('click',choose);$('styleChange').addEventListener('click',launch);
document.addEventListener('visibilitychange',()=>{cancelAnimationFrame(frame);if(!document.hidden&&!stopping&&!gate.hidden&&!reduced.matches)frame=requestAnimationFrame(paint);});
launch();
})();
