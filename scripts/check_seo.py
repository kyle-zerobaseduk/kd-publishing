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

from build_resources import selected
from resource_content import route
from build import BOOKS, CATS, ORIGIN, ROOT, full_title, verification_tag, CONSENT_BOOTSTRAP

PRIORITY = {'first-time-football-coach', 'season-planner', 'british-nostalgia',
            'i-deleted-the-honest-version', 'cozy-christmas-word-search'}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.meta, self.ids = [], {}, set()
        self.title, self.canonical, self.h1 = '', '', ''
        self.capture = None
        self.in_svg = False
        self.feed(source)
        self.schemas = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source)]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a['href']
        if tag == 'svg': self.in_svg = True
        if tag in ('title', 'h1') and not self.in_svg: self.capture = tag

    def handle_endtag(self, tag):
        if tag == 'svg': self.in_svg = False
        if tag == self.capture: self.capture = None

    def handle_data(self, value):
        if self.capture == 'title': self.title += value
        if self.capture == 'h1': self.h1 += value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref')
    parser.add_argument('--growth-release', action='store_true', help='Authorised shared-template improvements; protect catalogue, assets and product content semantically')
    parser.add_argument('--updated-book', choices=['80-day-sleep'], help='Explicit edition update, with all other books protected')
    args = parser.parse_args()
    baseline = args.baseline_ref
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
            if target.suffix == '.pdf':
                assert target.is_file(), (path, href)
                continue
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
            if local in pages: queue.append(local)
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
    if baseline and args.updated_book:
        from check_edition_preservation import check
        check(baseline)
    if baseline and not args.updated_book:
        def old(path):
            return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)
        before = json.loads(old('catalogue/books.json'))
        # Catalogue updates may add records; every existing record stays exact.
        current = {b['id']: b for b in BOOKS}
        # Book 26's owner-confirmed purchase-link activation is the only
        # permitted change to an existing record in this controlled release.
        activated = {b['id'] for b in before
                     if b['id'] == 'easy-word-search-for-dementia'
                     and b.get('amazonLinkEnabled') is False
                     and b.get('asin') == 'B0HNTX86GX'
                     and b.get('amazonUrl') == 'https://www.amazon.co.uk/dp/B0HNTX86GX'
                     and current.get(b['id']) == dict(b, amazonLinkEnabled=True)}
        assert all(current.get(b['id']) == b or b['id'] in activated for b in before), 'Existing catalogue metadata changed'
        additions = [b for b in BOOKS if b['id'] not in {x['id'] for x in before}]
        assert len(BOOKS) == len(before) + len(additions)
        assert (ROOT/'catalogue/search-console.json').read_bytes() == old('catalogue/search-console.json')
        original_assets = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline, '--', 'assets/covers', 'assets/previews', 'assets/responsive'], cwd=ROOT).decode().splitlines()
        for name in ['robots.txt', *original_assets]:
            assert (ROOT/name).read_bytes() == old(name), name
        baseline_css=old('styles.css').decode()
        assert (ROOT/'styles.css').read_text().startswith(baseline_css), 'Existing design CSS altered'
        def protected(markup):
            markup=markup.replace(CONSENT_BOOTSTRAP, "")
            markup=markup.replace('<main id="main" tabindex="-1">', '<main id="main">')
            markup=re.sub(r'<a href="(?:../)*resources/">Resources</a>', '', markup)
            markup=re.sub(r', "resource": null', '', markup)
            markup=re.sub(r' fetchpriority="high"', '', markup)
            markup=re.sub(r' srcset="[^"]+" sizes="[^"]+"', '', markup)
            markup=re.sub(r'<section class="container section book-resources">.*?</section>', '', markup)
            markup=markup.replace('book views, resource views, printable download clicks, related-book clicks, preview opens', 'book views, preview opens')
            return markup
        for path in pages:
            if args.growth_release:
                continue  # Dedicated semantic preservation below replaces exact template bytes.
            if path.is_relative_to(ROOT/'resources'): continue
            relative = path.relative_to(ROOT).as_posix()
            if additions:
                new_pages = {f'books/{b["id"]}/index.html' for b in additions}
                collection_pages = {'index.html', 'books/index.html', 'latest/index.html'} | {f'categories/{b["category"]}/index.html' for b in additions}
                if relative in new_pages | collection_pages: continue
            previous=old(path.relative_to(ROOT).as_posix()).decode()
            if relative in {f'books/{ident}/index.html' for ident in activated}:
                unavailable = '<p class="review-note">Amazon UK purchase link temporarily unavailable. We’re checking this listing.</p>'
                button = '<a class="button amazon-link" href="https://www.amazon.co.uk/dp/B0HNTX86GX" target="_blank" rel="noopener noreferrer" data-book-id="easy-word-search-for-dementia" data-asin="B0HNTX86GX">Buy on Amazon UK <span aria-hidden="true">↗</span></a>'
                ending = '</div></div><div class="product-details">'
                purchase_note = '<small>Amazon handles your order. Prices and availability may change there.</small>'
                assert previous.count(unavailable) == previous.count(ending) == 1
                expected = previous.replace(unavailable, button).replace(ending, '</div>' + purchase_note + '</div><div class="product-details">')
                assert path.read_text() == expected, 'Book 26 changed beyond its purchase button and order note'
            elif additions:
                assert path.read_text() == previous, f'Existing page changed during catalogue addition: {path}'
            else:
                assert protected(path.read_text())==protected(previous), f'Protected HTML changed beyond declared nav/config/related links/cover hints/privacy additions: {path}'
        if args.growth_release:
            from check_growth_preservation import check
            check(baseline)
        else:
            print(f'PASS: all {len(before)} existing catalogue records, ASINs, Amazon destinations, original assets, verification token and base CSS exact; {len(additions)} added books; protected HTML unchanged outside declared additions')
        if activated:
            print('PASS: Book 26 owner-confirmed link activation only; all other record fields and page content exact')
    for r in selected():
        page=pages[ROOT/route(r)]
        article,trail=page.schemas
        assert article['@type']=='Article' and article['headline']==r['title']
        assert article['author']=={'@type':'Organization','name':'K.D.Publishing editorial'}
        assert article['url']==page.canonical and 'datePublished' not in article
        assert trail['@type']=='BreadcrumbList' and [x['position'] for x in trail['itemListElement']]==[1,2,3,4]
        assert trail['itemListElement'][-1]['item']==page.canonical
    print(f'PASS: {len(pages)} unique canonicals, titles and descriptions; all pages reachable; fragments valid; {len(BOOKS)} Book and BreadcrumbList objects; optional verification hook')
    print('JSON syntax and expected schema fields validated locally. Google rich-result eligibility and indexed canonicals require external Google validation.')


if __name__ == '__main__': main()
