// Branch-only rendered checks. Dependencies installed in CI, never shipped with site.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
const previousCss=execFileSync('git',['show','e48b4d7ddf89eda003002417159ba3b9c9121b4f:styles.css'],{encoding:'utf8'});
const root=process.cwd(), modules=process.env.KD_LIGHTHOUSE_MODULE_DIR, out=process.env.KD_REPORT_DIR;
fs.mkdirSync(out,{recursive:true});
const pkg=JSON.parse(fs.readFileSync(path.join(modules,'puppeteer-core/package.json')));
const {default:puppeteer}=await import(pathToFileURL(path.join(modules,'puppeteer-core',pkg.main)));
const records=fs.readdirSync('content/resources').filter(n=>n.endsWith('.json')&&!n.endsWith('-grid.json')).map(n=>JSON.parse(fs.readFileSync('content/resources/'+n))).filter(r=>fs.existsSync(`resources/${r.cluster}/${r.slug}/index.html`));
const targets=['','books/british-nostalgia/','resources/','resources/football/','resources/puzzles/','resources/workplace-humour/',...records.map(r=>`resources/${r.cluster}/${r.slug}/`)];
const types={'.html':'text/html','.css':'text/css','.js':'application/javascript','.webp':'image/webp','.pdf':'application/pdf'};
const server=http.createServer((req,res)=>{let file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+'/'))file=path.join(root,'index.html');if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');if(!fs.existsSync(file)){res.writeHead(404).end();return;}res.writeHead(200,{'Content-Type':types[path.extname(file)]||'text/plain'});fs.createReadStream(file).pipe(res);});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await puppeteer.launch({executablePath:process.env.CHROME_PATH,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
const results=[],a11y=[],consent=[];
try{
 for(const width of [320,390,768,1024,1440])for(const target of targets){
  const context=await browser.createBrowserContext();const page=await context.newPage();await page.setViewport({width,height:900});const errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));await page.setRequestInterception(true);
  page.on('request',req=>{if(!req.url().startsWith(origin)&&!req.url().startsWith('data:')){external.push(req.url());req.abort();}else req.continue();});
  await page.evaluateOnNewDocument(()=>{window.kdLayoutShift=0;new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.kdLayoutShift+=e.value;}).observe({type:'layout-shift',buffered:true});});
  await page.goto(origin+'/'+target,{waitUntil:'networkidle0'});await page.evaluate(()=>document.fonts.ready);const initialLayoutShift=await page.evaluate(()=>window.kdLayoutShift);assert.ok(initialLayoutShift<.01,`${target} ${width}px initial shift ${initialLayoutShift}`);
  const issues=await page.evaluate(()=>{const a=[];if(document.documentElement.scrollWidth>innerWidth+1)a.push('overflow');for(const n of document.querySelectorAll('main h1,main p,main li,main svg')){const b=n.getBoundingClientRect();if(b.width&&(b.left< -1||b.right>innerWidth+1))a.push('content outside viewport');}return a;});
  assert.deepEqual(issues,[],target+' '+width);assert.deepEqual(errors,[]);assert.deepEqual(external,[],'requests before consent');
  if(width<=768){await page.click('.menu-toggle');assert.equal(await page.$eval('.menu-toggle',e=>e.getAttribute('aria-expanded')),'true');assert.equal(await page.$eval('.nav a[href$="resources/"]',e=>e.getBoundingClientRect().height>=44),true);await page.click('.menu-toggle');}
  const record=records.find(r=>target.includes('/'+r.slug+'/'));
  if(width<=390){
   const layout=await page.evaluate(css=>{
    function measure(){const banner=document.querySelector('.cookie-notice'),p=banner.querySelector('p');return {height:banner.getBoundingClientRect().height,fontSize:getComputedStyle(p).fontSize,buttons:Array.from(banner.querySelectorAll('button'),b=>{const r=b.getBoundingClientRect(),s=getComputedStyle(b);return {width:r.width,height:r.height,left:r.left,right:r.right,color:s.color,background:s.backgroundColor};}),privacyVisible:banner.querySelector('a').getBoundingClientRect().height>0};}
    const current=measure(),link=document.querySelector('link[rel="stylesheet"]'),style=document.createElement('style');link.disabled=true;style.textContent=css;document.head.appendChild(style);const previous=measure();style.remove();link.disabled=false;return {current,previous};
   },previousCss);
   assert.ok(layout.current.height<layout.previous.height);
   assert.equal(layout.current.fontSize,layout.previous.fontSize);
   assert.equal(layout.current.privacyVisible,true);
   assert.ok(layout.current.buttons.every(b=>b.height>=44&&b.left>=0&&b.right<=width));
   assert.ok(Math.abs(layout.current.buttons[0].width-layout.current.buttons[1].width)<1);
   assert.equal(layout.current.buttons[0].background,layout.current.buttons[1].background);
   assert.equal(layout.current.buttons[0].color,layout.current.buttons[1].color);
   consent.push({target:target||'/',width,...layout});
  }

  if(record){
   const downloads=await page.$$eval('[data-resource-download]',nodes=>nodes.map(n=>n.href));
   for(const href of downloads){const response=await page.evaluate(async u=>{const r=await fetch(u);return {status:r.status,type:r.headers.get('content-type'),magic:(await r.text()).slice(0,4)};},href);assert.equal(response.status,200);assert.equal(response.type,'application/pdf');assert.equal(response.magic,'%PDF');}
  }
  if(width===390||width===1440){
   await page.addScriptTag({path:path.join(modules,'axe-core/axe.min.js')});
   const report=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
   a11y.push({target:target||'/',width,violations:report.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});
   assert.equal(report.violations.length,0,JSON.stringify(a11y.at(-1)));
   // Keyboard focus: first Tab reaches the skip link with a visible outline.
   await page.reload({waitUntil:'networkidle0'});await page.keyboard.press('Tab');
   const focus=await page.evaluate(()=>{const e=document.activeElement,s=getComputedStyle(e);return {name:e.className,outline:s.outlineStyle};});
   assert.equal(focus.name,'skip-link');assert.notEqual(focus.outline,'none');
   await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'main');
   await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,(target.replaceAll('/','_')||'home')+width+'.png'),fullPage:true});
  }
  if(record&&width===390){
   // Decline: interactions still work and produce no analytics requests.
   await page.focus('#cookie-notice a');await page.keyboard.press('Tab');
   assert.equal(await page.evaluate(()=>document.activeElement.dataset.consent),'reject');
   assert.notEqual(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle),'none');
   await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>localStorage.getItem('kd_analytics_consent')),'no');
   await page.$$eval('[data-resource-download],[data-related-book]',nodes=>nodes.forEach(n=>n.addEventListener('click',e=>e.preventDefault())));
   await page.$eval('[data-related-book]',e=>e.click());
   if(record.downloads.length)await page.$eval('[data-resource-download]',e=>e.click());
   assert.deepEqual(external,[]);
   await page.reload({waitUntil:'networkidle0'});assert.equal(await page.$eval('#cookie-notice',e=>e.hidden),true);assert.deepEqual(external,[]);
   await page.evaluate(()=>localStorage.removeItem('kd_analytics_consent'));await page.reload({waitUntil:'networkidle0'});
   await page.focus('[data-consent="reject"]');await page.keyboard.press('Tab');
   assert.equal(await page.evaluate(()=>document.activeElement.dataset.consent),'accept');
   assert.notEqual(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle),'none');
   await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>localStorage.getItem('kd_analytics_consent')),'yes');
   const initial=await page.evaluate(()=>Array.from(window.dataLayer,a=>Array.from(a)));
   assert.equal(initial.filter(a=>a[0]==='event'&&a[1]==='page_view').length,1);
   assert.equal(initial.filter(a=>a[0]==='event'&&a[1]==='resource_page_view').length,1);
   assert.equal(initial.find(a=>a[0]==='config')[2].send_page_view,false);
   await page.$$eval('[data-resource-download],[data-related-book]',nodes=>nodes.forEach(n=>n.addEventListener('click',e=>e.preventDefault())));
   await page.$eval('[data-related-book]',e=>e.click());
   if(record.downloads.length)await page.$eval('[data-resource-download]',e=>e.click());
   const events=await page.evaluate(()=>Array.from(window.dataLayer,a=>Array.from(a)));
   assert.equal(events.filter(a=>a[1]==='related_book_click').length,1);
   assert.equal(events.filter(a=>a[1]==='printable_download').length,record.downloads.length?1:0);
   await page.goto(origin+'/privacy/',{waitUntil:'networkidle0'});
   assert.equal(await page.$eval('#cookie-notice',e=>e.hidden),true);
   await page.evaluate(()=>{document.cookie='_ga_TEST=example; path=/';sessionStorage.setItem('kd_campaign','{}');});external.length=0;
   await Promise.all([page.waitForNavigation({waitUntil:'networkidle0'}),page.click('#reset-consent')]);
   assert.equal(await page.evaluate(()=>localStorage.getItem('kd_analytics_consent')),null);
   assert.equal(await page.evaluate(()=>sessionStorage.getItem('kd_campaign')),null);
   assert.equal(await page.evaluate(()=>document.cookie.includes('_ga_TEST')),false);
   assert.equal(await page.$eval('#cookie-notice',e=>e.hidden),false);assert.deepEqual(external,[]);
  }
  results.push({target:target||'/',width,status:'pass',initialLayoutShift});await context.close();console.log(`PASS ${target||'/'} ${width}px`);
 }
}finally{fs.writeFileSync(path.join(out,'resource-browser.json'),JSON.stringify({results,a11y,consent},null,2));await browser.close();await new Promise(r=>server.close(r));}
console.log(`PASS ${results.length} rendered combinations; ${a11y.length} axe WCAG A/AA scans; download MIME, consent and resource events; keyboard focus.`);
