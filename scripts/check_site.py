"""Check generated pages, catalogue links and reduced preview assets."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image
from build import GA_ID, ORIGIN as PRODUCTION_URL

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
        self.amazon_buttons = []
        self.canonical = []
        self.og_urls = []
        self.og_images = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if tag == 'meta' and a.get('name') == 'description': self.description += 1
        if tag == 'meta' and a.get('property') == 'og:url': self.og_urls.append(a.get('content'))
        if tag == 'meta' and a.get('property') == 'og:image': self.og_images.append(a.get('content'))
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
        if tag == 'img': self.images.append(a)
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
            if 'amazon-link' in a.get('class', '').split():
                self.amazon.append(a['href'])
                self.amazon_buttons.append(a)
        if tag == 'button' and 'data-preview' in a:
            self.images.append({'src': a['data-preview'], 'alt': 'Preview button'})


def check():
    assert len({b['id'] for b in books}) == len(books)
    live = sum(b['status'] == 'live' for b in books)
    assert len({b['asin'] for b in books if b['asin']}) == live
    planner = next(b for b in books if b['id'] == 'season-planner')
    assert planner['asin'] == 'B0HJ6HGVC4'
    assert planner['amazonUrl'] == 'https://amzn.eu/d/09mIs6KH'
    assert all(urlsplit(b['amazonUrl']).scheme == 'https' and urlsplit(b['amazonUrl']).hostname in ('www.amazon.co.uk', 'amzn.eu') for b in books if b.get('amazonUrl'))
    all_pages = list(ROOT.rglob('index.html'))
    category_count = len({b['category'] for b in books})
    assert len(all_pages) == len(books) + category_count + 6, len(all_pages)
    for page in all_pages:
        markup = page.read_text()
        parsed = Inspect(); parsed.feed(markup)
        config = json.loads(re.search(r'<script type="application/json" id="site-config">([^<]+)</script>', markup).group(1))
        assert config['ga4'] == GA_ID, page
        assert (parsed.h1,parsed.title,parsed.description) == (1,1,1), page
        expected = PRODUCTION_URL + '/' + page.relative_to(ROOT).as_posix().removesuffix('index.html')
        assert parsed.canonical == [expected] and parsed.og_urls == [expected], page
        for image_url in parsed.og_images:
            assert image_url.startswith(PRODUCTION_URL + '/'), (page, image_url)
            assert (ROOT / image_url[len(PRODUCTION_URL)+1:]).is_file(), image_url
        for target in parsed.links + [x['src'] for x in parsed.images if x.get('src')]:
            if not target or target.startswith(('https://','mailto:','#')): continue
            local = (page.parent / unquote(urlsplit(target).path)).resolve()
            if target.endswith('/') or local.is_dir():
                local /= 'index.html'
            assert local.is_file(), f'{page.relative_to(ROOT)} → {target}'
        assert all(x.get('alt') for x in parsed.images), page
        if page.parent.parent.name == 'books' and page.parent.name != 'books':
            b = next(b for b in books if b['id'] == page.parent.name)
            assert config['book'] == {'id': b['id'], 'title': b.get('shortTitle') or b['title'], 'category': b['category'], 'asin': b['asin']}, b['id']
            can_buy = b['status'] == 'live' and b.get('amazonLinkEnabled', True)
            destination = b.get('amazonUrl') or f'https://www.amazon.co.uk/dp/{b["asin"]}'
            assert parsed.amazon == ([destination] if can_buy else []), b['id']
            assert len(parsed.amazon_buttons) == int(can_buy), b['id']
            if b['status'] == 'live' and not can_buy:
                assert 'Amazon UK purchase link temporarily unavailable.' in markup, b['id']
            if can_buy:
                button = parsed.amazon_buttons[0]
                assert (button.get('data-book-id'), button.get('data-asin')) == (b['id'], b['asin']), b['id']
                assert button.get('href') == parsed.amazon[0] and button.get('target') == '_blank', b['id']
            assert len([x for x in parsed.images if '/previews/' in x.get('src','') and x['alt'] != 'Preview button']) == len(b['previewPages'])
    assert not list(ROOT.rglob('*.pdf')) and not list(ROOT.rglob('*.zip'))
    for asset in (ROOT/'assets').rglob('*'):
        if not asset.is_file(): continue
        assert asset.suffix == '.webp' and asset.stat().st_size < 500_000, asset
        with Image.open(asset) as image:
            assert max(image.size) <= 1300 and image.width <= 850, asset
    assert len(list((ROOT/'assets/previews').glob('*.webp'))) == sum(len(b['previewPages']) for b in books)
    sitemap = ET.parse(ROOT/'sitemap.xml').getroot()
    listed = {item.text for item in sitemap.iter() if item.tag.endswith('loc')}
    assert listed == {PRODUCTION_URL + '/' + p.relative_to(ROOT).as_posix().removesuffix('index.html') for p in all_pages}
    assert f'Sitemap: {PRODUCTION_URL}/sitemap.xml' in (ROOT/'robots.txt').read_text()
    linked = sum(b['status'] == 'live' and b.get('amazonLinkEnabled', True) for b in books)
    print(f'PASS: {len(all_pages)} pages, {len(books)} listings, {live} verified ASINs, {linked} purchase links, {sum(len(b["previewPages"]) for b in books)} preview images, reduced assets only')


if __name__ == '__main__': check()
