(() => {
  'use strict';
  const config = JSON.parse(document.getElementById('site-config').textContent);
  const menu = document.querySelector('.menu-toggle');
  const nav = document.getElementById('primary-nav');
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav.classList.toggle('open', open);
  });
  const submenu = document.querySelector('.submenu-toggle');
  submenu.addEventListener('click', () => {
    const open = submenu.getAttribute('aria-expanded') !== 'true';
    submenu.setAttribute('aria-expanded', String(open));
    submenu.parentElement.classList.toggle('open', open);
  });

  // No third-party request, GA cookie or campaign storage is created before consent.
  const params = new URLSearchParams(location.search);
  const campaign = {};
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'].forEach(k => {
    if (params.has(k)) campaign[k] = params.get(k).slice(0, 100);
  });
  const banner = document.getElementById('cookie-notice');
  const validId = /^G-[A-Z0-9]+$/.test(config.ga4);
  let active = false;
  function attribution() {
    try {
      const stored = JSON.parse(sessionStorage.getItem('kd_campaign') || '{}');
      return { ...stored, ...campaign };
    } catch { return campaign; }
  }
  function event(name, extra = {}) {
    if (!active) return;
    // Tracking is optional. A failed analytics API must never interrupt navigation.
    try {
      window.gtag?.('event', name, { ...attribution(), ...extra, transport_type: 'beacon' });
    } catch {}
  }
  function activate() {
    if (!validId || active) return;
    active = true;
    try { if (Object.keys(campaign).length) sessionStorage.setItem('kd_campaign', JSON.stringify(campaign)); } catch {}
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', config.ga4, { send_page_view: false });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(config.ga4);
    document.head.appendChild(script);
    event('page_view', { page_title: document.title, page_location: location.href });
    if (config.book) event('book_page_view', { book_id: config.book.id, book_title: config.book.title, category: config.book.category, asin: config.book.asin || '' });
  }
  if (validId) {
    let choice;
    try { choice = localStorage.getItem('kd_analytics_consent'); } catch {}
    if (choice === 'yes') activate();
    else if (choice !== 'no') banner.hidden = false;
    banner.querySelectorAll('[data-consent]').forEach(button => button.addEventListener('click', () => {
      const yes = button.dataset.consent === 'accept';
      try { localStorage.setItem('kd_analytics_consent', yes ? 'yes' : 'no'); } catch {}
      banner.hidden = true;
      if (yes) activate();
    }));
  }
  document.getElementById('reset-consent')?.addEventListener('click', () => {
    try { localStorage.removeItem('kd_analytics_consent'); sessionStorage.removeItem('kd_campaign'); } catch {}
    location.reload();
  });

  document.querySelectorAll('.amazon-link').forEach(link => link.addEventListener('click', () => {
    event('amazon_click', {
      book_id: config.book.id,
      book_title: config.book.title,
      category: config.book.category,
      asin: config.book.asin,
      destination: link.href
    });
  }));
  const dialog = document.querySelector('.preview-dialog');
  if (dialog) {
    document.querySelectorAll('[data-preview]').forEach(button => button.addEventListener('click', () => {
      dialog.querySelector('img').src = button.dataset.preview;
      dialog.querySelector('img').alt = button.querySelector('img').alt;
      dialog.querySelector('p').textContent = 'Actual interior sample · Page ' + button.dataset.page;
      dialog.showModal();
      event('preview_open', { book_id: config.book.id, book_title: config.book.title, category: config.book.category, asin: config.book.asin || '', page_number: Number(button.dataset.page) });
    }));
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  }
})();
