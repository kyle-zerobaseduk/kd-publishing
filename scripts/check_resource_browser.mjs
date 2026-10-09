// Branch-only rendered checks. Dependencies installed in CI, never shipped with site.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
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
const results=[],a11y=[];
try{
 for(const width of [320,390,768,1024,1440])for(const target of targets){
  const page=await browser.newPage();await page.setViewport({width,height:900});const errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));await page.setRequestInterception(true);
  page.on('request',req=>{if(!req.url().startsWith(origin)&&!req.url().startsWith('data:')){external.push(req.url());req.abort();}else req.continue();});
  await page.goto(origin+'/'+target,{waitUntil:'networkidle0'});await page.evaluate(()=>document.fonts.ready);
  const issues=await page.evaluate(()=>{const a=[];if(document.documentElement.scrollWidth>innerWidth+1)a.push('overflow');for(const n of document.querySelectorAll('main h1,main p,main li,main svg')){const b=n.getBoundingClientRect();if(b.width&&(b.left< -1||b.right>innerWidth+1))a.push('content outside viewport');}return a;});
  assert.deepEqual(issues,[],target+' '+width);assert.deepEqual(errors,[]);assert.deepEqual(external,[],'requests before consent');
  if(width<=768){await page.click('.menu-toggle');assert.equal(await page.$eval('.menu-toggle',e=>e.getAttribute('aria-expanded')),'true');assert.equal(await page.$eval('.nav a[href$="resources/"]',e=>e.getBoundingClientRect().height>=44),true);await page.click('.menu-toggle');}
  const record=records.find(r=>target.includes('/'+r.slug+'/'));
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
   await page.evaluate(()=>document.activeElement?.blur());await page.keyboard.press('Tab');
   const focus=await page.evaluate(()=>{const e=document.activeElement,s=getComputedStyle(e);return {name:e.className,outline:s.outlineStyle};});
   assert.equal(focus.name,'skip-link');assert.notEqual(focus.outline,'none');
   await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'main');
   await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,(target.replaceAll('/','_')||'home')+width+'.png'),fullPage:true});
  }
  if(record&&width===390){
   // Decline: interactions still work and produce no analytics requests.
   await page.click('[data-consent="reject"]');
   await page.$$eval('[data-resource-download],[data-related-book]',nodes=>nodes.forEach(n=>n.addEventListener('click',e=>e.preventDefault())));
   await page.$eval('[data-related-book]',e=>e.click());
   if(record.downloads.length)await page.$eval('[data-resource-download]',e=>e.click());
   assert.deepEqual(external,[]);
   await page.evaluate(()=>localStorage.removeItem('kd_analytics_consent'));await page.reload({waitUntil:'networkidle0'});
   await page.click('[data-consent="accept"]');
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
  }
  results.push({target:target||'/',width,status:'pass'});await page.close();console.log(`PASS ${target||'/'} ${width}px`);
 }
}finally{fs.writeFileSync(path.join(out,'resource-browser.json'),JSON.stringify({results,a11y},null,2));await browser.close();await new Promise(r=>server.close(r));}
console.log(`PASS ${results.length} rendered combinations; ${a11y.length} axe WCAG A/AA scans; download MIME, consent and resource events; keyboard focus.`);
