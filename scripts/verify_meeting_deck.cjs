const {chromium}=require('C:/Users/zellh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'presentations/20260924/qa');
const url='http://127.0.0.1:4176/'+encodeURIComponent('AQUASKY_AIQA_客戶會議簡報_20260924.html');
(async()=>{
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto(url);await page.waitForTimeout(400);
if(errors.length){console.log(JSON.stringify({errors}));await browser.close();process.exit(1)}
const count=await page.evaluate(()=>deck.slides.length),overflow=[];
const notes=await page.evaluate(()=>deck.slides.map((s,i)=>`## ${i+1}. ${s.title}\n\n${s.notes}\n`).join('\n'));
fs.writeFileSync(path.join(root,'presentations/20260924/逐頁講稿.md'),'# AQUASKY 客戶會議講稿\n\n'+notes);
for(let i=0;i<count;i++){
 await page.evaluate(i=>deck.go(i),i);
 let dimensions=await page.locator('.slide.active').evaluate(s=>{
  const body=s.querySelector('.body'),foot=s.querySelector('.foot');
  const children=[...body.children];return {bodyHeight:body.clientHeight,scrollHeight:body.scrollHeight,
  overlap:children.some(c=>c.getBoundingClientRect().bottom>foot.getBoundingClientRect().top+1)};
 });
 if(dimensions.scrollHeight>dimensions.bodyHeight+2||dimensions.overlap)overflow.push({slide:i+1,...dimensions});
 await page.screenshot({path:path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`)});
}
await page.evaluate(()=>deck.openLibrary());
await page.selectOption('#stateFilter','plus');let plus=await page.locator('#libraryCount').innerText();
await page.selectOption('#stateFilter','intro');let intro=await page.locator('#libraryCount').innerText();
await page.selectOption('#stateFilter','wrong');let wrong=await page.locator('#libraryCount').innerText();
await page.click('#resetFilters');let all=await page.locator('#libraryCount').innerText();
await page.selectOption('#modelFilter','openai');let model=await page.locator('#libraryCount').innerText();
await page.selectOption('#modelFilter','');await page.selectOption('#questionFilter','A3');let question=await page.locator('#libraryCount').innerText();
await page.selectOption('#questionFilter','');await page.fill('#searchFilter','zzzzNOTMATCH999');let empty=await page.locator('#libraryCount').innerText();
await page.click('#resetFilters');await page.screenshot({path:path.join(out,'library.png')});
await page.evaluate(()=>deck.openAnswer('perplexity:B7'));await page.screenshot({path:path.join(out,'wrong-brand.png')});
const answerOnTop=await page.evaluate(()=>document.elementFromPoint(innerWidth/2,180).closest('#answerModal')!==null);
let original=await page.locator('.rawtext').textContent();let originalMatch=await page.evaluate(s=>s===deck.data.records.find(r=>r.id==='perplexity:B7').answer,original);
await page.keyboard.press('Escape');
const answerChecks=await page.evaluate(()=>{
 let failures=[];for(const r of deck.data.records){deck.openAnswer(r.id);if(document.querySelector('.rawtext').textContent!==r.answer)failures.push(r.id)}
 document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'));return {checked:deck.data.records.length,failures};
});
await page.evaluate(()=>deck.go(deck.slides.findIndex(s=>s.html.includes('class="matrix"'))));await page.click('.matrix-slide [data-evidence="openai:A2"]');
const matrixClick=await page.locator('#answerTitle').innerText();await page.keyboard.press('Escape');
const narrow=[];await page.setViewportSize({width:1280,height:720});
for(let i of [0,1,2,3,4,7,10,15,18,19,20,21]){await page.evaluate(i=>deck.go(i),i);await page.screenshot({path:path.join(out,`projector-${i+1}.png`)});}
await page.setViewportSize({width:390,height:844});await page.click('#readBtn');await page.evaluate(()=>deck.go(0));await page.waitForTimeout(650);await page.screenshot({path:path.join(out,'mobile-reading.png')});
const mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
const recordChecks=await page.evaluate(()=>({records:deck.data.records.length,questions:deck.data.questions.length,plus:deck.data.records.filter(r=>r.text_plus).map(r=>r.id),A:deck.data.records.filter(r=>r.group==='A'&&r.text_brand).length}));
const result={slides:count,errors,overflow,filters:{plus,intro,wrong,all,model,question,empty},originalMatch,answerOnTop,answerChecks,matrixClick,mobileOverflow,recordChecks};
fs.writeFileSync(path.join(out,'browser-verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));await browser.close();
if(errors.length||overflow.length||!originalMatch||!answerOnTop||mobileOverflow||plus!=='3 / 72'||all!=='72 / 72')process.exit(1);
})();
