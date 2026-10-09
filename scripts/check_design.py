"""Structural design regressions. These checks do not replace rendered visual review.

python3 scripts/check_design.py [--baseline /path/to/unchanged/main]
"""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from build import BOOKS

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], ''

    def content(self):
        return self.text + ''.join(child.content() for child in self.children)


class Tree(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.root = self.current = Node()
        self.nodes = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.nodes.append(node)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_endtag(self, tag):
        assert self.current.tag == tag, f'Incorrectly nested {tag} in {self.current.tag}'
        self.current = self.current.parent

    def handle_data(self, data):
        self.current.text += data


def contrast(foreground, background):
    def luminance(colour):
        channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        return sum(v * w for v, w in zip(linear, [.2126, .7152, .0722]))
    low, high = sorted([luminance(foreground), luminance(background)])
    return (high + .05) / (low + .05)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path)
    baseline = parser.parse_args().baseline
    image_count = 0
    pages = list(ROOT.rglob('*.html'))
    for file in pages:
        source = file.read_text()
        tree = Tree(source)
        ids = [n.attrs['id'] for n in tree.nodes if 'id' in n.attrs]
        assert len(ids) == len(set(ids)), f'Duplicate ID: {file}'
        previous_heading = 0
        for node in tree.nodes:
            attrs = node.attrs
            if re.fullmatch('h[1-6]', node.tag):
                level = int(node.tag[1])
                assert level <= previous_heading + 1, f'Skipped heading level: {file}'
                previous_heading = level
            for attribute in ['aria-controls', 'aria-labelledby']:
                if attribute in attrs:
                    assert all(value in ids for value in attrs[attribute].split()), (file, attribute)
            if node.tag == 'button':
                assert attrs.get('type') == 'button', file
                assert attrs.get('aria-label') or node.content().strip(), f'Unnamed control: {file}'
            if node.tag == 'img' and 'src' in attrs:
                image = (file.parent / attrs['src']).resolve()
                with Image.open(image) as decoded:
                    assert (int(attrs['width']), int(attrs['height'])) == decoded.size, f'Incorrect image proportions: {image}'
                image_count += 1
            if node.tag == 'dl':
                assert attrs.get('class') == 'facts', file
                for group in node.children:
                    assert group.tag == 'div' and [n.tag for n in group.children] == ['dt', 'dd'], f'Invalid facts list: {file}'
        if file.parent.parent.name == 'books':
            book = next(b for b in BOOKS if b['id'] == file.parent.name)
            h1 = next(n for n in tree.nodes if n.tag == 'h1')
            assert h1.content() == book['title'], file
            lead = next(n for n in tree.nodes if n.attrs.get('class') == 'lead')
            assert lead.content() == book.get('productDescription', book['description']), file
            subtitles = [n for n in tree.nodes if n.attrs.get('class') == 'product-subtitle']
            assert [n.content() for n in subtitles] == ([book['subtitle']] if book.get('subtitle') else []), file
        if baseline:
            before = (baseline / file.relative_to(ROOT)).read_text()
            assert re.search(r'<head>.*?</head>', before, re.S).group() == re.search(r'<head>.*?</head>', source, re.S).group(), f'Metadata changed: {file}'
    if baseline:
        for file in [ROOT / 'catalogue/books.json', ROOT / 'site.js', ROOT / 'robots.txt', ROOT / 'sitemap.xml', *ROOT.glob('assets/**/*')]:
            if file.is_file():
                assert file.read_bytes() == (baseline / file.relative_to(ROOT)).read_bytes(), f'Protected file changed: {file}'
    contact = (ROOT / 'contact/index.html').read_text()
    assert 'href="mailto:kdpublishingkyle@gmail.com"' in contact
    assert 'id="reset-consent"' in (ROOT / 'privacy/index.html').read_text()
    css = (ROOT / 'styles.css').read_text()
    colours = dict(re.findall(r'--([\w-]+):\s*(#[\da-f]{6});', css))
    ratios = [contrast(colours[fg], colours[bg]) for fg, bg in [('ink', 'paper'), ('muted', 'paper'), ('muted', 'shelf'), ('teal', 'shelf'), ('white', 'teal'), ('brass', 'white')]]
    assert min(ratios) >= 4.5, f'Text contrast failed: {ratios}'
    assert contrast('#d0dad7', colours['ink']) >= 4.5
    assert '[hidden] { display: none !important; }' in css
    print(f'PASS: {len(pages)} pages; heading order, control names/IDs, semantic facts, {image_count} accurate image dimensions; text contrast >= {min(ratios):.2f}:1')
    if baseline:
        print('PASS: unchanged catalogue, analytics script, approved images, metadata, sitemap and robots')
    print('Rendered layouts, focus visibility and complete WCAG compliance remain separate browser checks.')


if __name__ == '__main__':
    main()
