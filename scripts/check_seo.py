"""Validate SEO output and preservation against the approved deployment.

Run after the build: python3 scripts/check_seo.py --baseline-ref origin/main
"""
import argparse
import json
import re
import subprocess
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from build import BOOKS, CATS, ORIGIN, ROOT, full_title, verification_tag

PRIORITY = {'first-time-football-coach', 'season-planner', 'british-nostalgia',
            'i-deleted-the-honest-version', 'cozy-christmas-word-search'}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.meta, self.ids = [], {}, set()
        self.title, self.canonical, self.h1 = '', '', ''
        self.capture = None
        self.feed(source)
        self.schemas = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source)]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a['href']
        if tag in ('title', 'h1'): self.capture = tag

    def handle_endtag(self, tag):
        if tag == self.capture: self.capture = None

    def handle_data(self, value):
        if self.capture == 'title': self.title += value
        if self.capture == 'h1': self.h1 += value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref')
    baseline = parser.parse_args().baseline_ref
    pages = {p: Page(p.read_text()) for p in ROOT.rglob('index.html')}
    assert len({p.title for p in pages.values()}) == len(pages)
    assert len({p.meta['description'] for p in pages.values()}) == len(pages)
    assert len({p.canonical for p in pages.values()}) == len(pages)
    for path, page in pages.items():
        assert not re.search(r'noindex|nofollow', page.meta.get('robots', ''), re.I), path
        assert page.canonical == ORIGIN + '/' + path.relative_to(ROOT).as_posix().removesuffix('index.html')
        for href in page.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc: continue
            target = (path.parent / parsed.path).resolve() if parsed.path else path
            if target.is_dir(): target /= 'index.html'
            assert target in pages, (path, href)
            if parsed.fragment: assert parsed.fragment in pages[target].ids, (path, href)
    reached, queue = set(), deque([ROOT / 'index.html'])
    while queue:
        current = queue.popleft()
        if current in reached: continue
        reached.add(current)
        for href in pages[current].links:
            target = urlsplit(href)
            if target.scheme or target.netloc: continue
            local = (current.parent / target.path).resolve() if target.path else current
            if local.is_dir(): local /= 'index.html'
            queue.append(local)
    assert reached == set(pages), 'Orphan pages'
    for book in BOOKS:
        path = ROOT / 'books' / book['id'] / 'index.html'
        page = pages[path]
        assert page.h1 == book['title']
        assert page.title == book['seoTitle'] + ' | K.D.Publishing'
        # A review guard, not a Google character limit or ranking promise.
        assert len(page.title) <= 65
        data, trail = page.schemas
        assert data['@type'] == 'Book' and trail['@type'] == 'BreadcrumbList'
        assert data['name'] == full_title(book)
        assert data['url'] == page.canonical and data['@id'] == page.canonical + '#book'
        assert data['identifier'] == {'@type': 'PropertyValue', 'propertyID': 'ASIN', 'value': book['asin']}
        assert data['description'] == book.get('productDescription', book['description'])
        assert data['author'] == {'@type': 'Person', 'name': 'Kyle Dyer'}
        assert data['bookFormat'] == 'https://schema.org/Paperback'
        assert (ROOT / data['image'].removeprefix(ORIGIN + '/')).is_file()
        assert not {'offers', 'review', 'aggregateRating', 'isbn', 'numberOfPages', 'datePublished'} & data.keys()
        assert [x['position'] for x in trail['itemListElement']] == [1, 2, 3]
        assert [x['item'] for x in trail['itemListElement']] == [ORIGIN + '/', ORIGIN + '/categories/' + book['category'] + '/', page.canonical]
        assert trail['itemListElement'][1]['name'] == CATS[book['category']][0]
        if book['id'] in PRIORITY:
            assert page.meta['description'] == book['metaDescription']
    assert verification_tag('index.html', '') == ''
    assert verification_tag('index.html', 'owner_supplied-test-token') == '<meta name="google-site-verification" content="owner_supplied-test-token">'
    assert verification_tag('books/index.html', 'owner_supplied-test-token') == ''
    try:
        verification_tag('index.html', '<meta name="google-site-verification">')
        raise AssertionError('Full HTML tag should be rejected')
    except ValueError:
        pass
    if baseline:
        def old(path):
            return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)
        before = json.loads(old('catalogue/books.json'))
        assert len(before) == len(BOOKS) == 24
        allowed = {'seoTitle', 'metaDescription', 'productDescription', 'features', 'companion'}
        for previous, book in zip(before, BOOKS):
            assert {k: v for k, v in previous.items() if k not in allowed} == {k: v for k, v in book.items() if k not in allowed}, book['id']
            if book['id'] not in PRIORITY:
                assert re.search(r'<body>.*</body>', old(f'books/{book["id"]}/index.html').decode(), re.S).group() == re.search(r'<body>.*</body>', (ROOT / f'books/{book["id"]}/index.html').read_text(), re.S).group()
        for path in [ROOT/'styles.css', ROOT/'site.js', ROOT/'sitemap.xml', ROOT/'robots.txt', *ROOT.glob('assets/**/*.webp')]:
            assert path.read_bytes() == old(path.relative_to(ROOT).as_posix()), path
        for path in pages:
            if path.parent.parent != ROOT / 'books':
                current, previous = path.read_bytes(), old(path.relative_to(ROOT).as_posix())
                if path == ROOT / 'index.html':
                    pattern = rb'<meta name="google-site-verification" content="[A-Za-z0-9_-]+">'
                    current, previous = re.sub(pattern, b'', current), re.sub(pattern, b'', previous)
                assert current == previous, path
        print('PASS: all 24 book identities, ASINs, Amazon destinations, previews, assets, CSS and tracking preserved; non-book pages preserved apart from optional homepage verification token')
    print(f'PASS: {len(pages)} unique canonicals, titles and descriptions; all pages reachable; fragments valid; 24 Book and BreadcrumbList objects; optional verification hook')
    print('JSON syntax and expected schema fields validated locally. Google rich-result eligibility and indexed canonicals require external Google validation.')


if __name__ == '__main__': main()
