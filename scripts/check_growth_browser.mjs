// Exercise real browser behaviour on a local test server. External requests are intercepted.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modules = path.resolve(process.env.KD_LIGHTHOUSE_MODULE_DIR);
const pkg = JSON.parse(fs.readFileSync(path.join(modules,'puppeteer-core/package.json')));
const {default: puppeteer} = await import(pathToFileURL(path.join(modules,'puppeteer-core',pkg.main)));
const axe = fs.readFileSync(path.join(modules,'axe-core/axe.min.js'),'utf8');
const books = JSON.parse(fs.readFileSync(path.join(root,'catalogue/books.json')));
const reviewFixture = execFileSync('python3',['-c', `import sys; sys.path.insert(0,'scripts'); from reader_reviews import render; print(render({'id':'test-book'}, '/', {'enabled':True,'endpoint':'https://formspree.io/f/testonly'}, []))`],{cwd:root,encoding:'utf8'});
const types = {'.html':'text/html','.css':'text/css','.js':'application/javascript','.webp':'image/webp'};
const server = http.createServer((req,res) => {
  const file = path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if (file !== root && !file.startsWith(root+path.sep)) return res.writeHead(403).end();
  const resolved = fs.existsSync(file) && fs.statSync(file).isDirectory() ? path.join(file,'index.html') : file;
  if (!fs.existsSync(resolved)) return res.writeHead(404).end();
  res.writeHead(200,{'Content-Type':types[path.extname(resolved)] || 'application/octet-stream'});
  fs.createReadStream(resolved).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await puppeteer.launch({executablePath:process.env.CHROME_PATH,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try {
  const page = await browser.newPage();
  const errors=[], external=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.setRequestInterception(true);
  page.on('request', r=> {
    if(r.url().startsWith(base) || r.url().startsWith('data:')) return r.continue();
    external.push(r.url()); return r.abort();
  });
  await page.setViewport({width:390,height:844});
  await page.goto(base+'/books/',{waitUntil:'networkidle0'});
  assert.equal(await page.$eval('#book-result-count',e=>e.textContent),`${books.length} of ${books.length} books`);
  await page.type('#book-search','FOOTBALL');
  assert.equal(await page.$$eval('.book-card:not([hidden])',e=>e.length),2);
  await page.$eval('#book-search',e=>{e.value='NO-SUCH-BOOK'; e.dispatchEvent(new Event('input',{bubbles:true}));});
  assert.equal(await page.$eval('#book-no-results',e=>e.hidden),false);
  await page.click('#clear-search');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'book-search');
  await page.select('#book-sort','newest');
  const newest = [...books].sort((a,b)=>(b.catalogueAdded || b.released || '').localeCompare(a.catalogueAdded || a.released || ''))[0];
  assert.equal(await page.$eval('.book-card',e=>new URL(e.href).pathname),`/books/${newest.id}/`);
  await page.select('#book-sort','title');
  const titles = await page.$$eval('.book-card',nodes=>nodes.map(n=>n.dataset.title));
  assert.deepEqual(titles,[...titles].sort((a,b)=>a.localeCompare(b,'en')));
  assert.deepEqual(external,[]);
  assert.equal(await page.evaluate(()=>sessionStorage.length),0);
  await page.addScriptTag({content:axe});
  let violations = await page.evaluate(async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations);
  assert.deepEqual(violations.map(v=>v.id),[],'catalogue accessibility');
  await page.setJavaScriptEnabled(false);
  await page.reload({waitUntil:'networkidle0'});
  assert.equal(await page.$$eval('.book-card:not([hidden])',e=>e.length),books.length);
  assert.equal(await page.$eval('.catalogue-tools',e=>e.hidden),true);
  await page.setJavaScriptEnabled(true);
  for(const book of books){
    await page.goto(base+'/books/'+book.id+'/',{waitUntil:'networkidle0'});
    assert.equal(await page.$$eval('form',nodes=>nodes.length),0,'No inactive review form');
    const expected=book.amazonUrl || `https://www.amazon.co.uk/dp/${book.asin}`;
    const canBuy = book.status === 'live' && book.amazonLinkEnabled !== false;
    assert.deepEqual(await page.$$eval('.amazon-link',nodes=>nodes.map(n=>n.href)),canBuy ? [expected,expected] : []);
    assert.equal(await page.evaluate(()=>window.dataLayer===undefined),true);
    await page.click('[data-consent="accept"]');
    // Cancel external navigation only in the test; leave the click handler under test intact.
    await page.$$eval('.amazon-link',nodes=>nodes.forEach(n=>n.addEventListener('click',e=>e.preventDefault())));
    await page.click('[data-preview]');
    await page.keyboard.press('Escape');
    if(canBuy) await page.click('.amazon-link[data-placement="after_preview"]');
    const events=await page.evaluate(()=>window.dataLayer.filter(e=>e[0]==='event').map(e=>({name:e[1],params:e[2]})));
    assert.equal(events.filter(e=>e.name==='amazon_click').length,Number(canBuy));
    if(canBuy){
      assert.equal(events.find(e=>e.name==='amazon_click').params.placement,'after_preview');
      assert.equal(events.find(e=>e.name==='amazon_click').params.destination_url,expected);
    } else {
      assert.match(await page.$eval('.review-note',e=>e.textContent),/purchase link temporarily unavailable/);
    }
    const preview = events.filter(e=>e.name==='preview_open');
    assert.equal(preview.length,1);
    assert.equal(preview[0].params.book_id,book.id);
    assert.equal(preview[0].params.asin,book.asin);
    assert.equal(events.filter(e=>e.name==='book_page_view').length,1);
    await page.evaluate(()=>localStorage.clear());
    if(['easy-word-search-for-dementia','dinosaur-colouring-and-discovery'].includes(book.id)){
      await page.addScriptTag({content:axe});
      violations=await page.evaluate(async()=>(await axe.run(document)).violations);
      assert.deepEqual(violations.map(v=>v.id),[],`${book.id} accessibility`);
    }
  }
  // Isolated form fixture: validation/layout only. No actual submission or external data.
  await page.goto(base+'/books/easy-word-search-for-dementia/',{waitUntil:'networkidle0'});
  await page.evaluate(markup=>{document.querySelector('main').innerHTML=markup;},reviewFixture);
  assert.equal(await page.$eval('form',f=>f.checkValidity()),false);
  await page.click('input[name="rating"][value="1"]');
  await page.type('#review-text','Synthetic browser validation text. Never submitted or published.');
  await page.click('input[name="reader_confirmation"]');
  await page.click('input[name="consent_to_publish"]');
  assert.equal(await page.$eval('form',f=>f.checkValidity()),true);
  assert.equal(await page.$eval('#review-name',e=>e.required),false);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  assert.deepEqual(errors,[]);
  console.log(`PASS: catalogue search/sort/reset/no-JS, ${books.filter(b=>b.status==='live' && b.amazonLinkEnabled!==false).length} purchase destinations, disabled purchase gates, one consented event per click for all ${books.length} books, disabled review gate and isolated form validation`);
} finally {await browser.close(); await new Promise(r=>server.close(r));}
