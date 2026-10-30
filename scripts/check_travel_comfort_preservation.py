"""Verify the authorised two-book cover release against its deployment baseline."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {'travel-and-world-cities', 'comfort-food-and-baking'}
EDITABLE = {'coverImage', 'coverAlt', 'coverSource', 'publisher', 'format',
            'description', 'productDescription', 'features', 'metaDescription'}
CARD = re.compile(r'<a class="book-card".*?</a>', re.S)


def check(baseline):
    def old(path):
        return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)

    before = json.loads(old('catalogue/books.json'))
    after = json.loads((ROOT / 'catalogue/books.json').read_text())
    assert len(before) == len(after) == 26
    assert [b['id'] for b in before] == [b['id'] for b in after]
    for previous, current in zip(before, after):
        if current['id'] not in TARGETS:
            assert previous == current, current['id']
        else:
            assert {k: v for k, v in previous.items() if k not in EDITABLE} == {
                k: v for k, v in current.items() if k not in EDITABLE}, current['id']
            assert current['status'] == 'live' and current['format'] == 'Paperback'
            assert current['coverImage'] == f"assets/covers/{current['id']}-20261030.webp"
            assert current['coverSource'] is None  # PNG derivatives must not revert to old wrap PDFs.
            assert len(current['features']) == 3
            assert '100' in current['features'][0]

    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline], cwd=ROOT).decode().splitlines()
    mutable = {'catalogue/books.json', 'scripts/build.py', 'scripts/check_seo.py',
               '.github/workflows/seo-validation.yml', 'README.md'}
    product_pages = {f'books/{slug}/index.html' for slug in TARGETS}
    for name in tracked:
        current = (ROOT / name).read_bytes()
        previous = old(name)
        if name in mutable or name in product_pages:
            continue
        if name.endswith('index.html'):
            def protected(source):
                def card(match):
                    text = match.group()
                    ident = re.search(r'href="(?:../)*books/([^/]+)/"', text)[1]
                    return f'<TARGET-CARD:{ident}>' if ident in TARGETS else text
                return CARD.sub(card, source.decode())
            assert protected(current) == protected(previous), name
        else:
            assert current == previous, name

    for slug, asin in [('travel-and-world-cities', 'B0HDYP1JF2'),
                       ('comfort-food-and-baking', 'B0HFD1G62R')]:
        name = f'books/{slug}/index.html'
        current, previous = (ROOT / name).read_text(), old(name).decode()
        for pattern in [r'<div class="preview-grid">.*?</div>',
                        r'<script type="application/json" id="site-config">.*?</script>',
                        r'<a class="button amazon-link".*?</a>']:
            assert re.findall(pattern, current) == re.findall(pattern, previous), (slug, pattern)
        assert current.count(f'href="https://www.amazon.co.uk/dp/{asin}"') == 2
        assert current.count(f'data-asin="{asin}"') == 2
        assert '100' in current and 'Full Answer Key' in current
    print('PASS: only two authorised records/cards updated; other 24 books, every original image, previews, URLs, tracking, campaigns, styles and sitemap preserved')
