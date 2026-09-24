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
function run({ choice, id = 'G-TEST123', failEvent = false }) {
  const menu = element(), submenu = element(), banner = element(), amazon = element();
  const reject = element(), accept = element();
  reject.dataset.consent = 'reject'; accept.dataset.consent = 'accept';
  banner.querySelectorAll = () => [reject, accept];
  const scripts = [], stored = new Map(), session = new Map(), events = [];
  if (choice) stored.set('kd_analytics_consent', choice);
  const document = {
    title: 'Football book', head: { appendChild(script) { scripts.push(script.src); } },
    createElement() { return {}; },
    getElementById(key) { return key === 'site-config' ? { textContent: JSON.stringify({ ga4: id, book: { id: 'first-time-football-coach', title: 'Football Coach', category: 'guides', asin: 'B0HJDH6831' } }) } : key === 'cookie-notice' ? banner : null; },
    querySelector(key) { return ({ '.menu-toggle': menu, '#primary-nav': element(), '.submenu-toggle': submenu, '.preview-dialog': null })[key] || null; },
    querySelectorAll(key) { return key === '.amazon-link' ? [amazon] : []; },
  };
  const context = {
    document, location: { search: '?utm_source=pinterest&utm_campaign=launch', href: 'https://example.test/books/first-time-football-coach/' },
    localStorage: { getItem: k => stored.get(k), setItem: (k, v) => stored.set(k, v), removeItem: k => stored.delete(k) },
    sessionStorage: { getItem: k => session.get(k), setItem: (k, v) => session.set(k, v), removeItem: k => session.delete(k) },
    URLSearchParams, Date, window: { dataLayer: { push(args) { if (failEvent && args[0] === 'event') throw Error('analytics unavailable'); events.push(args); } } },
  };
  vm.runInNewContext(source, context);
  return { banner, accept, reject, amazon, menu, submenu, scripts, stored, session, events };
}

let state = run({});
assert.equal(state.banner.hidden, false);
assert.equal(state.scripts.length, 0);
assert.equal(state.session.size, 0);
state.amazon.handlers.click();
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

state = run({}); state.reject.handlers.click(); state.amazon.handlers.click();
assert.equal(state.scripts.length, 0); assert.equal(state.events.length, 0);
assert.equal(state.session.size, 0);

state = run({ choice: 'yes', failEvent: true });
assert.equal(state.scripts.length, 1);
assert.doesNotThrow(() => state.amazon.handlers.click());

state = run({ id: '' });
assert.equal(state.scripts.length, 0);
assert.equal(state.banner.hidden, true);
console.log('PASS: opt-in, rejection, campaign attribution, Amazon click, analytics failure, unconfigured state');
