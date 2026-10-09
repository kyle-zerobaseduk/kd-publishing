// Phase 2A release check. Uses the existing Lighthouse browser dependency.
// No analytics consent or external purchase navigation is performed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modules = path.resolve(process.env.KD_LIGHTHOUSE_MODULE_DIR);
const { default: puppeteer } = await import(pathToFileURL(path.join(modules, 'puppeteer-core/lib/esm/puppeteer/puppeteer-core.js')));
const targets = ['', 'books/first-time-football-coach/', 'books/season-planner/', 'books/british-nostalgia/', 'books/i-deleted-the-honest-version/', 'books/cozy-christmas-word-search/'];
const widths = [320, 360, 390, 768, 1024, 1440];
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp' };
const server = http.createServer((req, res) => {
  const relative = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\/+/, '');
  let file = path.resolve(root, relative || 'index.html');
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file) || !types[path.extname(file)]) { res.writeHead(404).end(); return; }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] });
  fs.createReadStream(file).pipe(res);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH, headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
let checked = 0;
try {
  for (const width of widths) {
    const page = await browser.newPage();
    await page.setViewport({ width, height: 900 });
    const errors = [], external = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setRequestInterception(true);
    page.on('request', request => {
      if (!request.url().startsWith(`http://127.0.0.1:${server.address().port}/`) && !request.url().startsWith('data:')) {
        external.push(request.url()); request.abort();
      } else request.continue();
    });
    for (const target of targets) {
      await page.goto(`http://127.0.0.1:${server.address().port}/${target}`, { waitUntil: 'networkidle0' });
      await page.evaluate(async () => {
        localStorage.removeItem('kd_analytics_consent');
        for (const image of document.images) { image.loading = 'eager'; await image.decode(); }
        await document.fonts.ready;
      });
      const issues = await page.evaluate(() => {
        const issues = [];
        if (document.documentElement.scrollWidth > innerWidth + 1) issues.push('horizontal overflow');
        for (const node of document.querySelectorAll('main h1, main p, main li, .button, .product-cover, .preview')) {
          const box = node.getBoundingClientRect();
          if (box.width && (box.left < -1 || box.right > innerWidth + 1)) issues.push(`${node.tagName}.${node.className} outside viewport`);
          if (node.matches('.button, .preview') && box.height < 43) issues.push('small touch target');
        }
        for (const image of document.images) if (!image.complete || !image.naturalWidth) issues.push('unloaded image');
        const consent = document.querySelector('#cookie-notice');
        if (['fixed', 'absolute'].includes(getComputedStyle(consent).position)) issues.push('consent overlays content');
        return issues;
      });
      assert.deepEqual(issues, [], `${target || '/'} at ${width}px`);
      assert.deepEqual(errors, [], 'browser errors');
      assert.deepEqual(external, [], 'external request before consent');
      if (width <= 800) {
        await page.click('.menu-toggle');
        assert.equal(await page.$eval('.menu-toggle', e => e.getAttribute('aria-expanded')), 'true');
        await page.click('.submenu-toggle');
        assert.equal(await page.$eval('.submenu-toggle', e => e.getAttribute('aria-expanded')), 'true');
        await page.click('.submenu-toggle');
        await page.click('.menu-toggle');
      }
      if (target) {
        await page.click('[data-preview]');
        assert.equal(await page.$eval('.preview-dialog', e => e.open), true);
        await page.keyboard.press('Escape');
        assert.equal(await page.$eval('.preview-dialog', e => e.open), false);
      }
      if (width === 390 || width === 1440) {
        await page.evaluate(() => scrollTo(0, 0));
        const data = await page.screenshot({ type: 'jpeg', quality: 40, fullPage: true, encoding: 'base64' });
        console.log('KD_RESPONSIVE_SCREENSHOT ' + JSON.stringify({ page: target || '/', width, data }));
      }
      await page.click('[data-consent="reject"]');
      assert.equal(await page.$eval('#cookie-notice', e => e.hidden), true);
      await page.evaluate(() => localStorage.removeItem('kd_analytics_consent'));
      checked++;
      console.log(`KD_RESPONSIVE_PASS ${target || '/'} ${width}px`);
    }
    await page.close();
  }
  console.log(`PASS: ${checked} priority page/viewport release checks; images, mobile navigation, previews and consent; no external requests`);
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
