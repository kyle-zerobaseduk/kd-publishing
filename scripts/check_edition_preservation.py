"""Bound a Sleep edition update while preserving the other 24 books."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = '80-day-sleep'
CARD = re.compile(r'<a class="book-card".*?</a>', re.S)


def check(baseline):
    def old(path):
        return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)

    before = json.loads(old('catalogue/books.json'))
    after = json.loads((ROOT / 'catalogue/books.json').read_text())
    assert len(before) == len(after) == 25
    assert [b['id'] for b in before] == [b['id'] for b in after]
    assert [b for b in before if b['id'] != BOOK] == [b for b in after if b['id'] != BOOK]
    sleep = next(b for b in after if b['id'] == BOOK)
    assert sleep['asin'] == 'B0HN65B19G'
    assert sleep['amazonUrl'] == 'https://www.amazon.co.uk/dp/B0HN65B19G'
    assert sleep['assetVersion'] == '20261015' and sleep['previewPages'] == [8, 9, 19]
    for name in ['site.js', 'styles.css', 'sitemap.xml', 'robots.txt', 'catalogue/search-console.json']:
        assert (ROOT / name).read_bytes() == old(name), name
    originals = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline, '--', 'assets'], cwd=ROOT).decode().splitlines()
    for name in originals:
        if Path(name).name.startswith(BOOK + '.') or Path(name).name.startswith(BOOK + '-'):
            continue
        assert (ROOT / name).read_bytes() == old(name), name

    def card_id(card):
        return re.search(r'href="(?:../)*books/([^/]+)/"', card)[1]

    for page in ROOT.rglob('index.html'):
        relative = page.relative_to(ROOT).as_posix()
        if relative == f'books/{BOOK}/index.html':
            continue
        previous, current = old(relative).decode(), page.read_text()
        before_cards = CARD.findall(previous)
        after_cards = CARD.findall(current)
        before_other = {card_id(c): c for c in before_cards if card_id(c) != BOOK}
        after_other = {card_id(c): c for c in after_cards if card_id(c) != BOOK}
        assert all(c == before_other.get(k) for k, c in after_other.items()), relative
        if relative in ('index.html', 'latest/index.html'):
            # Bringing Sleep to the front can displace only the last existing card.
            assert card_id(after_cards[0]) == BOOK
            expected = [card_id(c) for c in before_cards if card_id(c) != BOOK]
            actual = [card_id(c) for c in after_cards if card_id(c) != BOOK]
            assert actual == expected[:len(actual)], relative
            assert len(before_cards) == len(after_cards), relative
        else:
            assert [card_id(c) for c in before_cards] == [card_id(c) for c in after_cards], relative
        assert CARD.sub('<BOOK-CARD>', current) == CARD.sub('<BOOK-CARD>', previous), relative
    print('PASS: 24 other records, purchase destinations, page content and assets exact; only Sleep assets/cards and release ordering changed')
