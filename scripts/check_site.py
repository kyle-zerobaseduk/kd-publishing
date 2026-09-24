"""Check generated pages, catalogue links and reduced preview assets."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
books = json.loads((ROOT / 'catalogue/books.json').read_text())


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.h1 = 0
        self.title = 0
        self.description = 0
        self.amazon = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if tag == 'meta' and a.get('name') == 'description': self.description += 1
        if tag == 'img': self.images.append(a)
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
            if 'amazon.co.uk/dp/' in a['href']: self.amazon.append(a['href'])
        if tag == 'button' and 'data-preview' in a:
            self.images.append({'src': a['data-preview'], 'alt': 'Preview button'})


def check():
    assert len({b['id'] for b in books}) == len(books)
    live = sum(b['status'] == 'live' for b in books)
    assert len({b['asin'] for b in books if b['asin']}) == live
    all_pages = list(ROOT.rglob('index.html'))
    category_count = len({b['category'] for b in books})
    assert len(all_pages) == len(books) + category_count + 6, len(all_pages)
    for page in all_pages:
        parsed = Inspect(); parsed.feed(page.read_text())
        assert (parsed.h1,parsed.title,parsed.description) == (1,1,1), page
        for target in parsed.links + [x['src'] for x in parsed.images if x.get('src')]:
            if not target or target.startswith(('https://','mailto:','#')): continue
            local = (page.parent / unquote(urlsplit(target).path)).resolve()
            if target.endswith('/') or local.is_dir():
                local /= 'index.html'
            assert local.is_file(), f'{page.relative_to(ROOT)} → {target}'
        assert all(x.get('alt') for x in parsed.images), page
        if page.parent.parent.name == 'books' and page.parent.name != 'books':
            b = next(b for b in books if b['id'] == page.parent.name)
            assert parsed.amazon == ([f'https://www.amazon.co.uk/dp/{b["asin"]}'] if b['status'] == 'live' else []), b['id']
            assert len([x for x in parsed.images if '/previews/' in x.get('src','') and x['alt'] != 'Preview button']) == len(b['previewPages'])
    assert not list(ROOT.rglob('*.pdf')) and not list(ROOT.rglob('*.zip'))
    for asset in (ROOT/'assets').rglob('*'):
        if not asset.is_file(): continue
        assert asset.suffix == '.webp' and asset.stat().st_size < 500_000, asset
        with Image.open(asset) as image:
            assert max(image.size) <= 1300 and image.width <= 850, asset
    assert len(list((ROOT/'assets/previews').glob('*.webp'))) == sum(len(b['previewPages']) for b in books)
    print(f'PASS: {len(all_pages)} pages, {len(books)} listings, {live} ASIN destinations, {sum(len(b["previewPages"]) for b in books)} preview images, reduced assets only')


if __name__ == '__main__': check()
