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
  // Opt-in internal flag for the owner's own browsers: ?kd_internal=1 sets it, ?kd_internal=0 clears it.
  try {
    if (params.get('kd_internal') === '1') localStorage.setItem('kd_internal', '1');
    else if (params.get('kd_internal') === '0') localStorage.removeItem('kd_internal');
  } catch {}
  let internal = false;
  try { internal = localStorage.getItem('kd_internal') === '1'; } catch {}
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
    window.gtag('config', config.ga4, internal ? { send_page_view: false, traffic_type: 'internal' } : { send_page_view: false });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(config.ga4);
    document.head.appendChild(script);
    event('page_view', { page_title: document.title, page_location: location.href, page_referrer: document.referrer });
    if (config.resource) event('resource_page_view', { resource_id: config.resource.id, resource_cluster: config.resource.cluster });
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
    active = false;
    try { localStorage.removeItem('kd_analytics_consent'); sessionStorage.removeItem('kd_campaign'); } catch {}
    // Remove analytics cookies set on this site when a visitor changes their choice.
    try {
      document.cookie.split(';').forEach(part => {
        const name = part.trim().split('=')[0];
        if (/^_ga(?:_|$)|^_gid$|^_gat(?:_|$)/.test(name)) {
          document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax';
        }
      });
    } catch {}
    location.reload();
  });

  document.querySelectorAll('.amazon-link').forEach(link => link.addEventListener('click', () => {
    event('amazon_click', {
      book_id: config.book.id,
      book_title: config.book.title,
      category: config.book.category,
      asin: config.book.asin,
      destination_url: link.href,
      placement: link.dataset.placement || 'product_top'
    });
  }));
  document.querySelector('[data-review-form]')?.addEventListener('submit', () => {
    // Native POST continues through the provider's spam check. This is an
    // attempt, never a claim of successful receipt, moderation or publication.
    event('review_submit_attempt', { book_id: config.book.id });
  });
  document.querySelectorAll('[data-resource-download]').forEach(link => link.addEventListener('click', () => {
    event('printable_download', { resource_id: link.dataset.resourceDownload, asset_id: link.dataset.assetId, destination_url: link.href });
  }));
  document.querySelectorAll('[data-related-book]').forEach(link => link.addEventListener('click', () => {
    event('related_book_click', { resource_id: link.dataset.resourceId, book_id: link.dataset.relatedBook });
  }));
  const dialog = document.querySelector('.preview-dialog');
  if (dialog) {
    document.querySelectorAll('[data-preview]').forEach(button => button.addEventListener('click', () => {
      dialog.querySelector('img').src = button.dataset.preview;
      dialog.querySelector('img').alt = button.querySelector('img').alt;
      dialog.querySelector('p').textContent = 'Actual interior sample · Page ' + button.dataset.page;
      dialog.showModal();
      event('preview_open', { book_id: config.book.id, book_title: config.book.title, category: config.book.category, asin: config.book.asin || '', page_number: Number(button.dataset.page), preview_source: 'thumbnail' });
    }));
    document.querySelectorAll('a[href="#inside"]').forEach(link => link.addEventListener('click', () => {
      event('preview_open', { book_id: config.book.id, book_title: config.book.title, category: config.book.category, asin: config.book.asin || '', page_number: 0, preview_source: 'look_inside_link' });
    }));
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
  }
})();
