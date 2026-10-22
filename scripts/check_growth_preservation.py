"""Protect existing content and destinations while allowing authorised template changes."""
import json
import subprocess
from pathlib import Path
from check_design import Tree
from check_seo import Page

ROOT = Path(__file__).resolve().parents[1]

def check(baseline):
    def old(path):
        return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT)
    assert (ROOT/'catalogue/books.json').read_bytes() == old('catalogue/books.json')
    assert (ROOT/'sitemap.xml').read_bytes() == old('sitemap.xml')
    books = json.loads(old('catalogue/books.json'))
    for book in books:
        path = f'books/{book["id"]}/index.html'
        before, after = old(path).decode(), (ROOT/path).read_text()
        a, b = Page(before), Page(after)
        assert (a.title, a.meta['description'], a.canonical, a.h1, a.schemas) == (b.title, b.meta['description'], b.canonical, b.h1, b.schemas), path
        def protected(source):
            nodes = Tree(source).nodes
            classes = {'lead', 'product-subtitle', 'product-details', 'facts'}
            text = [(n.attrs.get('class'), n.content()) for n in nodes if n.attrs.get('class') in classes]
            previews = [(n.attrs['data-preview'], n.attrs['data-page']) for n in nodes if 'data-preview' in n.attrs]
            purchases = {n.attrs['href'] for n in nodes if 'amazon-link' in n.attrs.get('class','').split()}
            return text, previews, purchases
        assert protected(before) == protected(after), path
    # Resources, downloads and private verification settings must remain intact.
    for name in subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'--','content','assets/resources','catalogue/search-console.json'],cwd=ROOT).decode().splitlines():
        assert (ROOT/name).read_bytes() == old(name), name
    for path in ROOT.glob('resources/**/index.html'):
        relative = path.relative_to(ROOT).as_posix()
        def main(s): return s.split('<main',1)[1].split('</main>',1)[0]
        assert main(path.read_text()) == main(old(relative).decode()), relative
    print('PASS growth preservation: 26 catalogue records, product copy/specs/previews/schema/Amazon destinations, all resources/downloads, sitemap and Search Console token unchanged')
