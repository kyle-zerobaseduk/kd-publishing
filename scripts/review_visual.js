// Optional development check; no browser code or dependencies are shipped to visitors.
// NODE_PATH=/path/to/node_modules node scripts/review_visual.js --baseline /path/to/main --output /tmp/kd-review
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const args = process.argv.slice(2);
function option(name, fallback) { const i = args.indexOf(name); return i < 0 ? fallback : args[i + 1]; }
const root = path.resolve(__dirname, '..');
const output = path.resolve(option('--output', '/tmp/kd-publishing-review'));
assert(!output.startsWith(root + path.sep), 'Keep review artifacts outside the website tree.');
const baseline = option('--baseline');
const widths = [320, 360, 390, 768, 1024, 1440];
const captures = new Set(['index.html', 'books/index.html', 'books/high-fantasy-realms/index.html', 'books/british-nostalgia/index.html', 'books/season-planner/index.html', 'books/80-day-mindfulness/index.html', 'categories/puzzles/index.html', 'categories/colouring/index.html', 'categories/guides/index.html', 'categories/journals/index.html', 'categories/humour/index.html', 'latest/index.html', 'about/index.html', 'contact/index.html', 'privacy/index.html']);
function pages(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() && !entry.name.startsWith('.') ? pages(path.join(dir, entry.name)) : entry.isFile() && entry.name.endsWith('.html') ? [path.join(dir, entry.name)] : []);
}
function serve(dir) {
  const server = http.createServer((req, res) => {
    const relative = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\/+/, '');
    let file = path.resolve(dir, relative || 'index.html');
    if (file !== dir && !file.startsWith(dir + path.sep)) { res.writeHead(403); res.end(); return; }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    res.setHeader('Content-Type', ({ '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp' })[path.extname(file)] || 'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve({ server, url: `http://127.0.0.1:${server.address().port}` })));
}
(async () => {
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch { throw Error('Playwright is required for this optional review. See docs/DESIGN_REVIEW.md.'); }
  const browser = await chromium.launch({ headless: true, ...(option('--browser') ? { executablePath: option('--browser') } : {}) });
  const servers = [], results = [];
  fs.mkdirSync(output, { recursive: true });
  try {
    for (const [label, dir] of [['after', root], ...(baseline ? [['before', path.resolve(baseline)]] : [])]) {
      const endpoint = await serve(dir); servers.push(endpoint.server);
      for (const width of widths) {
        const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
        // Review never sends analytics or clicks through to Amazon.
        const blockedRequests = [];
        await context.route(/googletagmanager\.com|google-analytics\.com/, route => { blockedRequests.push(route.request().url()); return route.abort(); });
        await context.addInitScript(() => localStorage.removeItem('kd_analytics_consent'));
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        const paths = pages(dir).map(file => path.relative(dir, file).split(path.sep).join('/'));
        for (const file of paths.filter(file => label === 'after' || captures.has(file))) {
          await page.goto(`${endpoint.url}/${file}`, { waitUntil: 'networkidle' });
          // Load all lazy images, then return to the top before capturing.
          await page.evaluate(async () => {
            for (const image of document.images) {
              if (image.getAttribute('src')) { image.loading = 'eager'; try { await image.decode(); } catch {} }
            }
            await document.fonts.ready;
          });
          if (label === 'after') {
            const issues = await page.evaluate(() => {
              const issues = [], width = innerWidth;
              if (document.documentElement.scrollWidth > width + 1) issues.push('horizontal overflow');
              for (const node of document.querySelectorAll('.button, .text-link, .contact-email, .book-art, .product-cover, .preview')) {
                const box = node.getBoundingClientRect();
                if (box.width && (box.left < -1 || box.right > width + 1)) issues.push(`${node.className}: outside viewport`);
                if (node.matches('a, button') && box.height < 43) issues.push(`${node.className}: touch target below 44px`);
              }
              for (const image of document.images) if (image.getAttribute('src') && !image.naturalWidth) issues.push(`image failed: ${image.getAttribute('src')}`);
              const consent = document.querySelector('#cookie-notice');
              if (['fixed', 'absolute'].includes(getComputedStyle(consent).position)) issues.push('consent overlays content');
              for (const action of document.querySelectorAll('.book-copy .text-link')) {
                if (action.getBoundingClientRect().width >= action.parentElement.getBoundingClientRect().width - 2) issues.push('stretched card action');
              }
              return issues;
            });
            assert.deepEqual(issues, [], `${file} at ${width}px: ${issues.join(', ')}`);
            assert.equal(blockedRequests.length, 0, 'Analytics requested before consent');
            assert.deepEqual(errors, [], 'Browser script error');
            if (width <= 800) {
              await page.locator('.menu-toggle').click();
              assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'), 'true');
              assert(await page.locator('#primary-nav').isVisible());
              await page.locator('.submenu-toggle').click();
              assert(await page.locator('#book-categories').isVisible());
              await page.locator('.submenu-toggle').click();
              assert(!(await page.locator('#book-categories').isVisible()));
              await page.locator('.menu-toggle').click();
            }
            if (file === 'books/high-fantasy-realms/index.html') {
              await page.locator('[data-preview]').first().click();
              assert(await page.locator('.preview-dialog').isVisible());
              await page.keyboard.press('Escape');
              assert(!(await page.locator('.preview-dialog').isVisible()));
            }
            results.push({ file, width, result: 'pass' });
          }
          if (captures.has(file)) {
            await page.screenshot({ path: path.join(output, `${label}-${file.replace(/\//g, '-')}-${width}.png`), fullPage: true });
          }
          if (label === 'after') {
            await page.locator('[data-consent="reject"]').click();
            assert(!(await page.locator('#cookie-notice').isVisible()));
          }
        }
        await context.close();
      }
    }
    fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify(results, null, 2));
    console.log(`PASS: ${results.length} page/viewport checks. Screenshots: ${output}`);
    console.log('Human visual and keyboard review remains required; these checks are not WCAG certification.');
  } finally {
    for (const server of servers) server.close();
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
