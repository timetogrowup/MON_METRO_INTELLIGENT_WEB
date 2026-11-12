const {chromium,webkit}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{const name=process.env.MMI_BROWSER||'chromium',browser=await({chromium,webkit}[name]).launch({headless:true,...(process.env.MMI_EXECUTABLE?{executablePath:process.env.MMI_EXECUTABLE}:{})});try{
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const html=fs.readFileSync('index.html','utf8'),base=html.match(/<style>([\s\S]*?)<\/style>/)[1];
 await page.setContent('<style>'+base+fs.readFileSync('theme-system.css','utf8')+fs.readFileSync('theme-motion.css','utf8')+'</style><main><span id="compact" class="line-badge compact-line mode-metro">1</span><span id="detail" class="line-badge mode-metro">Métro 1</span><span id="fallback" class="line-badge mode-bus">Bus</span></main>');
 await page.addScriptTag({path:'themes.js'});await page.addScriptTag({path:'line-colours.js'});
 const themes=await page.evaluate(()=>WenareThemes.list.map(t=>t.id));assert.equal(themes.length,12);
 for(const theme of themes){
  const styles=await page.evaluate(theme=>{
   WenareThemes.select(theme,false);for(const id of ['compact','detail'])WenareLineColours.apply(document.getElementById(id),WenareLineColours.palette({route_color:'FFBE00',route_text_color:'000000'}));
   WenareLineColours.apply(document.getElementById('fallback'),WenareLineColours.palette({route_color:'invalid'}));
   return ['compact','detail'].map(id=>{const s=getComputedStyle(document.getElementById(id));return [s.backgroundColor,s.color,s.backgroundImage]});
  },theme);
  assert.deepEqual(styles,[['rgb(255, 190, 0)','rgb(0, 0, 0)','none'],['rgb(255, 190, 0)','rgb(0, 0, 0)','none']],theme);
  assert.equal(await page.locator('#fallback').getAttribute('data-official-colour'),null);
 }
 console.log(name+' OFFICIAL_LINE_COLOURS_OK: summary/detail backgrounds and text preserved under all 12 themes, missing data keeps fallback');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
