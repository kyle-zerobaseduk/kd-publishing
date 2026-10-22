"""Render the Sleep release locally or verify the actual public GitHub Pages site."""
import argparse
import hashlib
import http.server
import json
import os
import re
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = json.loads((ROOT / 'catalogue/books.json').read_text())
LATEST_BOOK = max((b for b in CATALOGUE if b['status'] == 'live'),
                  key=lambda b: b.get('catalogueAdded') or b.get('released') or '')['id']
TARGETS = ['', 'books/', 'categories/journals/', 'latest/', 'books/80-day-sleep/']
COVER = 'assets/covers/80-day-sleep-20261015.webp'
ASIN = 'B0HN65B19G'
AMAZON = f'https://www.amazon.co.uk/dp/{ASIN}'
PREVIEWS = [f'assets/previews/80-day-sleep-20261015-{n}.webp' for n in [8, 9, 19]]


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'KD-Publishing-release-verification', 'Cache-Control': 'no-cache'}), timeout=30) as response:
        assert response.status == 200, url
        return response.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Omit to serve the checked-out site locally')
    parser.add_argument('--wait-seconds', type=int, default=0)
    parser.add_argument('--report-dir', type=Path, required=True)
    args = parser.parse_args()
    args.report_dir.mkdir(parents=True, exist_ok=True)
    server = None
    if args.base_url:
        base = args.base_url.rstrip('/') + '/'
        deadline = time.monotonic() + args.wait_seconds
        while True:
            try:
                for target in TARGETS:
                    assert COVER.encode() in fetch(base + target), target
                break
            except Exception as error:
                if time.monotonic() >= deadline:
                    raise
                print(f'Waiting for Pages to serve the edition: {error}', flush=True)
                time.sleep(15)
        # Compare the public HTML, data, scripts and all web images with this commit.
        files = [*ROOT.rglob('index.html'), *ROOT.glob('assets/**/*.webp'), ROOT / 'styles.css', ROOT / 'site.js', ROOT / 'catalogue/books.json', ROOT / 'sitemap.xml', ROOT / 'robots.txt']
        def verify_file(file):
            relative = file.relative_to(ROOT).as_posix()
            remote = fetch(base + relative.removesuffix('index.html'))
            assert hashlib.sha256(remote).digest() == hashlib.sha256(file.read_bytes()).digest(), f'Public bytes differ: {relative}'
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(verify_file, files))
        print(f'PASS: {len(files)} live HTML/data/script/image files match the deployment commit', flush=True)
    else:
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *values):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}/'

    checks = []
    try:
        with sync_playwright() as playwright:
            executable = os.environ.get('CHROME_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
            browser = playwright.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            for width in [320, 360, 390, 768, 1024, 1440]:
                context = browser.new_context(viewport={'width': width, 'height': 900}, device_scale_factor=1, is_mobile=width < 768, has_touch=width < 768)
                page = context.new_page()
                errors, external = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                def route(request):
                    if not request.request.url.startswith(base):
                        external.append(request.request.url)
                        request.abort()
                    else:
                        request.continue_()
                page.route('**/*', route)
                for target in TARGETS:
                    context.clear_cookies()
                    page.goto(base + target, wait_until='networkidle')
                    page.evaluate("localStorage.removeItem('kd_analytics_consent')")
                    page.reload(wait_until='networkidle')
                    page.evaluate("""async () => {
                      for (const image of document.images) if (image.getAttribute('src')) { image.loading='eager'; await image.decode(); }
                      await document.fonts.ready;
                    }""")
                    assert not errors, errors
                    assert not external, f'External request before consent: {external}'
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (width, target)
                    for node in page.locator('.button, .preview, .product-cover, main h1').all():
                        box = node.bounding_box()
                        if box and box['width']:
                            assert box['x'] >= -1 and box['x'] + box['width'] <= width + 1, (width, target, box)
                    if target != TARGETS[-1]:
                        card = page.locator('a.book-card[href$="books/80-day-sleep/"]')
                        assert card.count() == 1, target
                        assert card.locator('img').get_attribute('src').endswith(COVER)
                        if target in ['', 'latest/']:
                            assert page.locator('a.book-card').first.get_attribute('href').endswith(f'books/{LATEST_BOOK}/')
                    else:
                        assert page.locator('h1').inner_text() == 'The 80-Day Sleep'
                        assert page.locator('.product-subtitle').inner_text() == 'A Daily Sleep Journal'
                        assert page.locator('.product-cover img').get_attribute('src').endswith(COVER)
                        assert page.locator('.amazon-link').count() == 2
                        for purchase in page.locator('.amazon-link').all():
                            assert purchase.get_attribute('href') == AMAZON
                        assert page.locator('meta[property="og:image"]').get_attribute('content').endswith(COVER)
                        schema = page.locator('script[type="application/ld+json"]').first.text_content()
                        assert json.loads(schema)['identifier']['value'] == ASIN
                        assert 'B0HFWPP2KJ' not in page.content()
                        samples = page.locator('[data-preview]')
                        assert samples.count() == 3
                        for index, image in enumerate(PREVIEWS):
                            assert samples.nth(index).get_attribute('data-preview').endswith(image)
                            samples.nth(index).click()
                            assert page.locator('dialog').evaluate('(d) => d.open')
                            page.locator('dialog img').evaluate('(i) => i.decode()')
                            page.keyboard.press('Escape')
                        assert page.evaluate('window.dataLayer === undefined')
                    if width < 768:
                        page.locator('.menu-toggle').click()
                        assert page.locator('.menu-toggle').get_attribute('aria-expanded') == 'true'
                        page.locator('.submenu-toggle').click()
                        assert page.locator('.submenu-toggle').get_attribute('aria-expanded') == 'true'
                        page.locator('.menu-toggle').click()
                    page.locator('[data-consent="reject"]').click()
                    assert page.locator('#cookie-notice').is_hidden()
                    assert page.evaluate('window.dataLayer === undefined')
                    if width == 390:
                        label = {'': 'home', 'books/': 'catalogue', 'categories/journals/': 'journals', 'latest/': 'latest', 'books/80-day-sleep/': 'book'}[target]
                        page.evaluate('scrollTo(0, 0)')
                        page.screenshot(path=args.report_dir / f'mobile-{label}-full.png', full_page=True)
                        if label == 'book':
                            page.screenshot(path=args.report_dir / 'mobile-book-cover.png')
                            page.locator('.product-info').scroll_into_view_if_needed()
                            page.screenshot(path=args.report_dir / 'mobile-book-purchase.png')
                            page.locator('[data-preview]').nth(1).click()
                            page.locator('dialog img').evaluate('(i) => i.decode()')
                            page.screenshot(path=args.report_dir / 'mobile-interior-preview.png')
                            page.keyboard.press('Escape')
                    checks.append({'page': target or '/', 'width': width, 'result': 'pass'})
                    print(f'PASS: {target or "/"} at {width}px', flush=True)
                context.close()

            # Record the actual event calls, intercepting Google so tests do not pollute GA4.
            context = browser.new_context(viewport={'width': 390, 'height': 900})
            page = context.new_page()
            page.route('https://www.googletagmanager.com/**', lambda route: route.fulfill(status=200, body=''))
            page.goto(base + TARGETS[-1], wait_until='networkidle')
            assert page.evaluate('window.dataLayer === undefined')
            page.locator('[data-consent="accept"]').click()
            page.locator('[data-preview]').nth(1).click()
            page.keyboard.press('Escape')
            page.locator('.amazon-link').evaluate("e => e.addEventListener('click', x => x.preventDefault())")
            page.locator('.amazon-link').click()
            events = page.evaluate("window.dataLayer.filter(x => x[0] === 'event').map(x => ({name:x[1],params:x[2]}))")
            for name in ['book_page_view', 'preview_open', 'amazon_click']:
                found = [e for e in events if e['name'] == name]
                assert len(found) == 1 and found[0]['params']['book_id'] == '80-day-sleep' and found[0]['params']['asin'] == ASIN, events
            assert next(e for e in events if e['name'] == 'preview_open')['params']['page_number'] == 9
            assert next(e for e in events if e['name'] == 'amazon_click')['params']['destination_url'] == AMAZON
            context.close()
            browser.close()
        result = {'base_url': base, 'live': bool(args.base_url), 'commit': os.environ.get('GITHUB_SHA'), 'catalogue_count': len(CATALOGUE), 'checks': checks, 'events': events, 'result': 'pass'}
        (args.report_dir / 'results.json').write_text(json.dumps(result, indent=2))
        print('PASS: 30 responsive page checks; blue cover, real previews, catalogue visibility, purchase URL, SEO, consent and three edition-specific GA4 events', flush=True)
    finally:
        if server:
            server.shutdown()


if __name__ == '__main__':
    main()
