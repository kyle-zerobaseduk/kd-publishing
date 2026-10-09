// Local or CI Lighthouse measurement. No deployments, account writes or consented analytics.
// Dependencies are installed outside this repository; use the workflow's documented environment.
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const baseline = path.resolve(process.env.KD_BASELINE_DIR);
const output = path.resolve(process.env.KD_REPORT_DIR);
const modules = path.resolve(process.env.KD_LIGHTHOUSE_MODULE_DIR);
const { default: lighthouse } = await import(pathToFileURL(path.join(modules, 'lighthouse/core/index.js')));
const { launch } = await import(pathToFileURL(path.join(modules, 'chrome-launcher/dist/index.js')));
fs.mkdirSync(output, { recursive: true });
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript', '.webp': 'image/webp', '.xml': 'application/xml', '.txt': 'text/plain' };
const server = http.createServer((req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    const parts = decodeURIComponent(url.pathname).split('/').filter(Boolean);
    const mount = parts.shift();
    const selected = mount === 'baseline' ? baseline : mount === 'branch' ? root : null;
    if (!selected || parts.some(x => x.startsWith('.'))) { res.writeHead(404).end(); return; }
    let file = path.resolve(selected, ...parts);
    if (!file.startsWith(selected + path.sep) && file !== selected) { res.writeHead(404).end(); return; }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file) || !types[path.extname(file)]) { res.writeHead(404).end(); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] });
    fs.createReadStream(file).pipe(res);
  } catch { res.writeHead(400).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const chrome = await launch({ chromePath: process.env.CHROME_PATH, chromeFlags: ['--headless', '--no-sandbox', '--disable-dev-shm-usage'] });
const targets = ['', 'books/first-time-football-coach/', 'books/season-planner/', 'books/british-nostalgia/', 'books/i-deleted-the-honest-version/', 'books/cozy-christmas-word-search/'];
const summaries = [];
try {
  for (const mount of ['baseline', 'branch']) {
    for (const target of targets) {
      const url = `http://127.0.0.1:${server.address().port}/${mount}/${target}`;
      const result = await lighthouse(url, { port: chrome.port, output: ['json', 'html'], logLevel: 'error', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] });
      const lhr = result.lhr;
      if (lhr.runtimeError) throw Error(JSON.stringify(lhr.runtimeError));
      const name = `${mount}-${target.split('/')[1] || 'home'}-mobile`;
      fs.writeFileSync(path.join(output, name + '.json'), result.report[0]);
      fs.writeFileSync(path.join(output, name + '.html'), result.report[1]);
      const screenshot = lhr.audits['final-screenshot']?.details?.data;
      if (screenshot) fs.writeFileSync(path.join(output, name + '.jpg'), Buffer.from(screenshot.split(',')[1], 'base64'));
      const summary = { variant: mount, page: target || '/', lighthouse: lhr.lighthouseVersion, fetchedAt: lhr.fetchTime,
        performance: lhr.categories.performance.score, accessibility: lhr.categories.accessibility.score,
        bestPractices: lhr.categories['best-practices'].score, seo: lhr.categories.seo.score,
        lcpMs: lhr.audits['largest-contentful-paint'].numericValue, cls: lhr.audits['cumulative-layout-shift'].numericValue,
        tbtMs: lhr.audits['total-blocking-time'].numericValue, fcpMs: lhr.audits['first-contentful-paint'].numericValue,
        failedAudits: Object.values(lhr.audits).filter(a => a.score === 0).map(a => a.id) };
      summaries.push(summary);
      console.log('KD_MOBILE_RESULT ' + JSON.stringify(summary));
      if (screenshot) console.log('KD_MOBILE_SCREENSHOT ' + JSON.stringify({ variant: mount, page: target || '/', data: screenshot }));
    }
  }
  fs.writeFileSync(path.join(output, 'summary.json'), JSON.stringify({ limitation: 'Single mobile lab run per page from local static files on the CI runner; simulated throttling; analytics consent not accepted; not production network performance or Core Web Vitals field data.', settings: summaries.length ? 'Default Lighthouse mobile settings; see each JSON configSettings for precise values.' : '', results: summaries }, null, 2));
  if (process.env.GITHUB_STEP_SUMMARY) {
    const table = ['## Mobile lab measurements', '', 'Single runs on a local CI server. These are not production field Core Web Vitals or a traffic-growth result.', '', '| Variant | Page | Performance | LCP ms | CLS | TBT ms |', '| --- | --- | ---: | ---: | ---: | ---: |', ...summaries.map(s => `| ${s.variant} | ${s.page} | ${Math.round(s.performance * 100)} | ${Math.round(s.lcpMs)} | ${s.cls.toFixed(3)} | ${Math.round(s.tbtMs)} |`)];
    fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, table.join('\n') + '\n');
  }
} finally {
  await chrome.kill();
  await new Promise(resolve => server.close(resolve));
}
