// Run with `node scripts/test_tracking.js`. Exercises the browser script without a network call.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('site.js', 'utf8');
function element() {
  const handlers = {};
  const attributes = { 'aria-expanded': 'false' };
  return {
    handlers, dataset: {}, hidden: true, href: 'https://www.amazon.co.uk/dp/B0HJDH6831',
    classList: { toggle() {} }, parentElement: { classList: { toggle() {} } },
    addEventListener(type, handler) { handlers[type] = handler; },
    getAttribute(key) { return attributes[key]; },
    setAttribute(key, value) { attributes[key] = value; },
    querySelectorAll() { return []; },
  };
}
function run({ choice, id = 'G-TEST123', failEvent = false, query = '?utm_source=pinterest&utm_campaign=launch', referrer = 'https://example.org/', initialCampaign } = {}) {
  const menu = element(), nav = element(), submenu = element(), banner = element(), amazon = element(), reset = element(), dialog = element(), preview = element();
  const reject = element(), accept = element();
  reject.dataset.consent = 'reject'; accept.dataset.consent = 'accept';
  preview.dataset.preview = '../../assets/previews/first-time-football-coach-16.webp';
  preview.dataset.page = '16';
  preview.querySelector = () => ({ alt: 'Actual interior page 16' });
  const dialogImage = { src: '', alt: '' }, dialogText = { textContent: '' };
  dialog.querySelector = selector => selector === 'img' ? dialogImage : selector === 'p' ? dialogText : element();
  dialog.showModal = () => { dialog.open = true; };
  dialog.close = () => { dialog.open = false; };
  banner.querySelectorAll = () => [reject, accept];
  const scripts = [], stored = new Map(), session = new Map(), events = [];
  if (initialCampaign) session.set('kd_campaign', JSON.stringify(initialCampaign));
  const cookies = new Map([['_ga', 'GA1.1.test'], ['_ga_TEST123', 'GA1.1.test'], ['needed', 'yes']]);
  if (choice) stored.set('kd_analytics_consent', choice);
  const document = {
    title: 'Football book', referrer, head: { appendChild(script) { scripts.push(script.src); } },
    get cookie() { return [...cookies].map(([k, v]) => `${k}=${v}`).join('; '); },
    set cookie(value) { const name = value.split('=')[0]; if (value.includes('Max-Age=0')) cookies.delete(name); },
    createElement() { return {}; },
    getElementById(key) { return key === 'site-config' ? { textContent: JSON.stringify({ ga4: id, book: { id: 'first-time-football-coach', title: 'Football Coach', category: 'guides', asin: 'B0HJDH6831' } }) } : key === 'cookie-notice' ? banner : key === 'reset-consent' ? reset : key === 'primary-nav' ? nav : null; },
    querySelector(key) { return ({ '.menu-toggle': menu, '#primary-nav': element(), '.submenu-toggle': submenu, '.preview-dialog': dialog })[key] || null; },
    querySelectorAll(key) { return key === '.amazon-link' ? [amazon] : key === '[data-preview]' ? [preview] : []; },
  };
  const location = { search: query, href: 'https://example.test/books/first-time-football-coach/' + query, reload() { location.reloaded = true; } };
  const context = {
    document, location,
    localStorage: { getItem: k => stored.get(k), setItem: (k, v) => stored.set(k, v), removeItem: k => stored.delete(k) },
    sessionStorage: { getItem: k => session.get(k), setItem: (k, v) => session.set(k, v), removeItem: k => session.delete(k) },
    URLSearchParams, Date, window: { dataLayer: { push(args) { if (failEvent && args[0] === 'event') throw Error('analytics unavailable'); events.push(args); } } },
  };
  vm.runInNewContext(source, context);
  return { banner, accept, reject, amazon, menu, submenu, preview, dialog, reset, scripts, stored, session, events, cookies, location };
}

let state = run({});
assert.equal(state.banner.hidden, false);
assert.equal(state.scripts.length, 0);
assert.equal(state.session.size, 0);
state.menu.handlers.click();
assert.equal(state.menu.getAttribute('aria-expanded'), 'true');
state.menu.handlers.click();
assert.equal(state.menu.getAttribute('aria-expanded'), 'false');
state.submenu.handlers.click();
assert.equal(state.submenu.getAttribute('aria-expanded'), 'true');
state.amazon.handlers.click();
state.preview.handlers.click();
assert.equal(state.events.length, 0);
state.accept.handlers.click();
assert.equal(state.scripts.length, 1);
assert.equal(state.stored.get('kd_analytics_consent'), 'yes');
assert.equal(JSON.parse(state.session.get('kd_campaign')).utm_source, 'pinterest');
state.amazon.handlers.click();
const click = state.events.find(args => args[0] === 'event' && args[1] === 'amazon_click');
assert.equal(click[2].book_id, 'first-time-football-coach');
assert.equal(click[2].asin, 'B0HJDH6831');
assert.equal(click[2].utm_campaign, 'launch');
assert.equal(click[2].destination_url, 'https://www.amazon.co.uk/dp/B0HJDH6831');
assert.equal(state.events.filter(args => args[0] === 'event' && args[1] === 'page_view').length, 1);
assert.equal(state.events.filter(args => args[0] === 'event' && args[1] === 'book_page_view').length, 1);
assert.equal(state.events.find(args => args[1] === 'page_view')[2].page_referrer, 'https://example.org/');
assert.equal(state.events.find(args => args[1] === 'page_view')[2].page_location, 'https://example.test/books/first-time-football-coach/?utm_source=pinterest&utm_campaign=launch');
state.preview.handlers.click();
assert.equal(state.events.find(args => args[1] === 'preview_open')[2].page_number, 16);
assert.equal(state.dialog.open, true);
state.reset.handlers.click();
const eventCountAfterWithdrawal = state.events.length;
state.amazon.handlers.click();
assert.equal(state.events.length, eventCountAfterWithdrawal);
assert.equal(state.stored.has('kd_analytics_consent'), false);
assert.equal(state.session.has('kd_campaign'), false);
assert.equal(state.cookies.has('_ga'), false);
assert.equal(state.cookies.has('_ga_TEST123'), false);
assert.equal(state.cookies.get('needed'), 'yes');
assert.equal(state.location.reloaded, true);

state = run({}); state.reject.handlers.click(); state.amazon.handlers.click(); state.preview.handlers.click();
assert.equal(state.scripts.length, 0); assert.equal(state.events.length, 0);
assert.equal(state.session.size, 0);
assert.equal(state.amazon.href, 'https://www.amazon.co.uk/dp/B0HJDH6831');

state = run({ choice: 'no' });
assert.equal(state.banner.hidden, true);
assert.equal(state.scripts.length, 0);
state.amazon.handlers.click();
assert.equal(state.events.length, 0);

state = run({ choice: 'yes', query: '', referrer: '', initialCampaign: { utm_source: 'instagram', utm_medium: 'social' } });
assert.equal(state.scripts.length, 1);
assert.equal(state.events.filter(args => args[1] === 'page_view').length, 1);
assert.equal(state.events.find(args => args[1] === 'book_page_view')[2].utm_source, 'instagram');
assert.equal(state.events.find(args => args[1] === 'page_view')[2].page_referrer, '');

state = run({ choice: 'yes', failEvent: true });
assert.equal(state.scripts.length, 1);
assert.doesNotThrow(() => state.amazon.handlers.click());

state = run({ id: '' });
assert.equal(state.scripts.length, 0);
assert.equal(state.banner.hidden, true);
console.log('PASS: pre-consent privacy, opt-in/rejection/withdrawal, navigation, book funnel, campaign/referrer, analytics failure, unconfigured state');
