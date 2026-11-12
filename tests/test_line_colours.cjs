const test=require('node:test'),assert=require('node:assert/strict');
const colours=require('../line-colours.js');
test('official background and text are preserved, including black and white',()=>{
 assert.deepEqual(colours.palette({route_color:'ffbe00',route_text_color:'000000'}),{background:'#FFBE00',text:'#000000'});
 assert.deepEqual(colours.palette({route_color:'0055C8',route_text_color:'ffffff'}),{background:'#0055C8',text:'#FFFFFF'});
});
test('missing or malformed values cannot become CSS and keep the mode fallback',()=>{
 for(const value of [undefined,null,'','red','123','000000;position:fixed','url(x)','var(--theme)'])assert.equal(colours.palette({route_color:value}),null);
 assert.deepEqual(colours.palette({route_color:'ffffff'}),{background:'#FFFFFF',text:'#000000'});
 assert.deepEqual(colours.palette({route_color:'000000',route_text_color:'invalid'}),{background:'#000000',text:'#FFFFFF'});
});
test('badges resist theme colours while missing official colours remain untouched',()=>{
 const properties=new Map(),badge={dataset:{},style:{setProperty:(key,value,priority)=>properties.set(key,[value,priority])}};
 colours.apply(badge,null);assert.equal(properties.size,0);
 colours.apply(badge,colours.palette({route_color:'6e6e00',route_text_color:'ffffff'}));
 assert.deepEqual(properties.get('background-color'),['#6E6E00','important']);assert.deepEqual(properties.get('color'),['#FFFFFF','important']);assert.deepEqual(properties.get('background-image'),['none','important']);
});
