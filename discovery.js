(() => {
  'use strict';
  const tools = document.querySelector('.catalogue-tools');
  if (!tools) return;
  const grid = document.getElementById('catalogue-results');
  const search = document.getElementById('book-search');
  const sort = document.getElementById('book-sort');
  const cards = [...grid.querySelectorAll('.book-card')];
  const normalise = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const entries = cards.map((card, order) => ({ card, order, text: normalise(card.textContent) }));
  function update() {
    const words = normalise(search.value.trim()).split(/\s+/).filter(Boolean);
    const ordered = [...entries].sort((a, b) => sort.value === 'title'
      ? a.card.dataset.title.localeCompare(b.card.dataset.title, 'en')
      : sort.value === 'newest' ? b.card.dataset.added.localeCompare(a.card.dataset.added) || a.order - b.order
      : a.order - b.order);
    let count = 0;
    for (const entry of ordered) {
      entry.card.hidden = !words.every(word => entry.text.includes(word));
      if (!entry.card.hidden) count++;
      grid.appendChild(entry.card);
    }
    document.getElementById('book-result-count').textContent = `${count} of ${cards.length} books`;
    document.getElementById('book-no-results').hidden = count !== 0;
  }
  search.addEventListener('input', update);
  sort.addEventListener('change', update);
  document.getElementById('clear-search').addEventListener('click', () => {
    search.value = ''; sort.value = 'featured'; update(); search.focus();
  });
  tools.hidden = false;
  update();
  // Search queries are neither stored nor sent to analytics.
})();
