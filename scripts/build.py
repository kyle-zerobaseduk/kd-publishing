"""Build static, linkable catalogue pages. Run `python scripts/build.py`."""
import html
import json
import os
import re
from datetime import date
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = json.loads((ROOT / 'catalogue/books.json').read_text())
# Verified GitHub Pages production address. Override only when the live domain changes.
ORIGIN = os.environ.get('KD_SITE_URL', 'https://kyle-zerobaseduk.github.io/kd-publishing').rstrip('/')
GA_ID = os.environ.get('KD_GA4_ID', 'G-64LMW6KFB7')
SEARCH_CONSOLE_TOKEN = json.loads((ROOT / 'catalogue/search-console.json').read_text())['verificationToken']
# Resolve presentation before main parses; reads a preference only, never activates GA.
CONSENT_BOOTSTRAP = '<script>(()=>{const c=JSON.parse(document.getElementById("site-config").textContent);if(!/^G-[A-Z0-9]+$/.test(c.ga4))return;let v;try{v=localStorage.getItem("kd_analytics_consent");}catch{}if(v!=="yes"&&v!=="no")document.getElementById("cookie-notice").hidden=false;})();</script>'

CATS = {
    'puzzles': ('Word Search & Puzzle Books', 'Find a puzzle for a quiet moment, a favourite subject or a thoughtful gift.'),
    'colouring': ('Colouring & Activity Books', 'Detailed scenes and creative places to make your own.'),
    'guides': ('Football Coaching Books', 'Practical support for first-time U7 and U8 grassroots coaches.'),
    'journals': ('Planners & Journals', 'Space for reflection, routines and the things worth recording.'),
    'humour': ('Humour & Gift Books', 'Dry humour for familiar moments, and small gifts for people who will recognise them.'),
}
def full_title(book):
    return book['title'] + (': ' + book['subtitle'] if book.get('subtitle') else '')


def short_title(book):
    return book.get('shortTitle') or book['title']


def e(s):
    return html.escape(str(s), quote=True)


def prefix(path):
    return '../' * (len(Path(path).parts) - 1)


def url(path):
    return f'{ORIGIN}/{path.removesuffix("index.html")}' if ORIGIN else ''


def verification_tag(path, token=SEARCH_CONSOLE_TOKEN):
    """Optional, owner-supplied URL-prefix verification; never emit a placeholder."""
    if not isinstance(token, str) or (token and not re.fullmatch(r'[A-Za-z0-9_-]+', token)):
        raise ValueError('Search Console verificationToken must be the content value from Google, not an HTML tag')
    return f'<meta name="google-site-verification" content="{e(token)}">' if token and path == 'index.html' else ''


def book_markup(book, path, image):
    """Describe the actual edition and the existing visible breadcrumb trail."""
    data = {'@context': 'https://schema.org', '@type': 'Book', 'name': full_title(book),
            'author': {'@type': 'Person', 'name': 'Kyle Dyer'},
            'description': book.get('productDescription', book['description']),
            'bookFormat': 'https://schema.org/Paperback', 'inLanguage': 'en-GB'}
    if book.get('publisher'):
        data['publisher'] = {'@type': 'Organization', 'name': book['publisher']}
    if book['asin']:
        data['identifier'] = {'@type': 'PropertyValue', 'propertyID': 'ASIN', 'value': book['asin']}
    items = [data]
    if ORIGIN:
        data['@id'] = url(path) + '#book'
        data['url'] = url(path)
        if image:
            data['image'] = url(image)
        crumbs = [('Home', url('')), (CATS[book['category']][0], url(f'categories/{book["category"]}/')),
                  (short_title(book), url(path))]
        items.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                      'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': name, 'item': link}
                                          for i, (name, link) in enumerate(crumbs, 1)]})
    return ''.join('<script type="application/ld+json">' + json.dumps(item, ensure_ascii=False).replace('<', '\\u003c') + '</script>' for item in items)


@cache
def webp_size(image):
    """Read exported WebP dimensions without a build-time imaging dependency."""
    with image.open('rb') as file:
        header = file.read(30)
    assert header[:4] == b'RIFF' and header[8:12] == b'WEBP', image
    kind = header[12:16]
    if kind == b'VP8 ' and header[23:26] == b'\x9d\x01\x2a':
        return (int.from_bytes(header[26:28], 'little') & 0x3fff,
                int.from_bytes(header[28:30], 'little') & 0x3fff)
    if kind == b'VP8X':
        return (1 + int.from_bytes(header[24:27], 'little'),
                1 + int.from_bytes(header[27:30], 'little'))
    if kind == b'VP8L' and header[20] == 0x2f:
        bits = int.from_bytes(header[21:25], 'little')
        return (1 + (bits & 0x3fff), 1 + ((bits >> 14) & 0x3fff))
    raise ValueError(f'Unsupported WebP header: {image}')


def preview(book, pre, page):
    image_path = f"assets/previews/{book['id']}-{page}.webp"
    width, height = webp_size(ROOT / image_path)
    name = e(short_title(book))
    return f'''<button class="preview" type="button" data-preview="{pre}{image_path}" data-page="{page}" aria-label="Enlarge interior sample page {page} of {name}"><img src="{pre}{image_path}" alt="Actual interior page {page} from {name}" width="{width}" height="{height}" loading="lazy"><span>Page {page}<span class="preview-action">Enlarge <span aria-hidden="true">↗</span></span></span></button>'''


def cover(book, pre, loading='lazy'):
    image_path = book.get('coverImage') or f"assets/covers/{book['id']}.webp"
    image = ROOT / image_path
    if image.exists():
        width, height = webp_size(image)
        responsive = (f' srcset="{pre}assets/responsive/british-nostalgia-440.webp 440w, {pre}{image_path} {width}w" sizes="(max-width: 600px) 65vw, (max-width: 800px) 35vw, 32vw"' if book['id'] == 'british-nostalgia' else '')
        return f'<img{responsive} src="{pre}{image_path}" alt="Front cover of {e(short_title(book))}" width="{width}" height="{height}" loading="{loading}"{(' fetchpriority="high"' if loading == 'eager' else '')}>'
    return f'<div class="cover-pending" role="img" aria-label="Cover artwork pending for {e(short_title(book))}"><span>K.D.PUBLISHING</span><strong>{e(short_title(book))}</strong><small>Cover image pending</small></div>'


def card(book, pre, heading=3):
    name = short_title(book)
    status = '<span class="pill">In review</span>' if book['status'] != 'live' else ''
    return f'''<a class="book-card" href="{pre}books/{book['id']}/" aria-label="View {e(name)} and its interior preview">
      <div class="book-art">{cover(book, pre)}</div><div class="book-copy"><span class="eyebrow">{e(CATS[book['category']][0])}</span>
      <h{heading}>{e(name)}</h{heading}><p>{e(book['description'])}</p>{status}<span class="text-link">See inside <span aria-hidden="true">↗</span></span></div></a>'''


def cards(books, pre, heading=3):
    layout = {1: ' book-grid-single', 2: ' book-grid-pair', 3: ' book-grid-trio'}.get(len(books), '')
    return f'<div class="book-grid{layout}">' + ''.join(card(b, pre, heading) for b in books) + '</div>'


def shell(path, title, description, main, image=None, book=None, resource=None, extra_structured=''):
    pre = prefix(path)
    canonical = f'<link rel="canonical" href="{e(url(path))}">' if ORIGIN else ''
    ogurl = f'<meta property="og:url" content="{e(url(path))}">' if ORIGIN else ''
    ogimage = f'<meta property="og:image" content="{e(url(image) if ORIGIN else pre + image)}">' if image else ''
    structured = ''
    structured += extra_structured
    if book:
        structured += book_markup(book, path, image)
    nav = f'''<header class="header"><div class="container header-inner"><a class="brand" href="{pre}" aria-label="K.D.Publishing home"><span class="brand-mark">K<span>.</span>D<span>.</span></span><span class="brand-type">PUBLISHING</span></a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Open navigation"><span></span><span></span><span></span></button>
      <nav id="primary-nav" class="nav" aria-label="Primary"><a href="{pre}">Home</a><div class="nav-group"><a href="{pre}books/">Books</a><button class="submenu-toggle" type="button" aria-expanded="false" aria-controls="book-categories" aria-label="Show book categories">⌄</button><div class="submenu" id="book-categories">{''.join(f'<a href="{pre}categories/{key}/">{e(label)}</a>' for key,(label,_) in CATS.items())}</div></div><a href="{pre}latest/">Latest releases</a><a href="{pre}resources/">Resources</a><a href="{pre}about/">About</a><a href="{pre}contact/">Contact</a></nav></div></header>'''
    current_href = pre + path.removesuffix('index.html')
    if path == 'index.html':
        current_href = pre
    nav = nav.replace(f'href="{current_href}"', f'href="{current_href}" aria-current="page"')
    footer = f'''<footer class="footer"><div class="container footer-inner"><div><a class="footer-brand" href="{pre}">K.D.PUBLISHING</a><p>Books for curiosity, creativity and everyday life.</p></div><div><a href="{pre}books/">All books</a><a href="{pre}about/">About</a><a href="{pre}contact/">Contact</a><a href="{pre}privacy/">Privacy & analytics</a></div><small>© {date.today().year} K.D.Publishing</small></div></footer>'''
    consent = '<aside class="cookie-notice" id="cookie-notice" aria-label="Optional analytics" hidden><div class="container consent-inner"><p>May we use optional analytics to understand which books and previews people view? <a href="'+pre+'privacy/">Privacy details</a></p><div class="consent-actions"><button class="button button-secondary button-small" type="button" data-consent="reject">No thanks</button><button type="button" class="button button-small" data-consent="accept">Allow analytics</button></div></div></aside>'
    config = json.dumps({'ga4':GA_ID,'book':({'id':book['id'],'title':short_title(book),'category':book['category'],'asin':book['asin']} if book else None), 'resource':resource}).replace('<','\\u003c')
    out = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{e(title)} | K.D.Publishing</title><meta name="description" content="{e(description)}">{canonical}<meta property="og:type" content="{'book' if book else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">{ogurl}{ogimage}<meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="{pre}styles.css"><script type="application/json" id="site-config">{config}</script><script defer src="{pre}site.js"></script>{structured}{verification_tag(path)}</head><body><a class="skip-link" href="#main">Skip to content</a>{nav}{consent}{CONSENT_BOOTSTRAP}<main id="main" tabindex="-1">{main}</main>{footer}</body></html>'''
    destination = ROOT / path
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(out,encoding='utf-8')


def titleblock(kicker, title, text=''):
    return f'<div class="page-head container"><span class="eyebrow">{e(kicker)}</span><h1>{e(title)}</h1><p>{e(text)}</p></div>'


def home():
    pre=''
    hero=next(b for b in BOOKS if b['id']=='high-fantasy-realms')
    latest=sorted((b for b in BOOKS if b['status']=='live'),key=lambda b:b.get('catalogueAdded') or b.get('released') or '',reverse=True)[:4]
    categorytiles=''.join(f'<a class="category-tile" href="categories/{key}/"><span class="eyebrow">{str(sum(b["category"]==key for b in BOOKS))} {"title" if sum(b["category"]==key for b in BOOKS)==1 else "titles"}</span><h3>{e(label)}</h3><span aria-hidden="true">↗</span></a>' for key,(label,_) in CATS.items())
    main=f'''<section class="hero"><div class="container hero-grid"><div class="hero-copy"><span class="eyebrow">Independent publishing</span><h1>Books made to <em>take you somewhere.</em></h1><p>From imaginative colouring and themed puzzles to practical coaching guides and thoughtful journals, explore the growing K.D.Publishing collection.</p><div class="actions"><a class="button" href="books/">Explore all books <span aria-hidden="true">↗</span></a><a class="quiet-link" href="latest/">What’s new</a></div></div><a class="hero-book" href="books/high-fantasy-realms/" aria-label="Explore High Fantasy Realms"><span class="hero-book-image">{cover(hero,pre,'eager')}</span><span class="hero-book-caption"><span class="eyebrow">From our collection</span><strong>High Fantasy Realms</strong><span class="text-link">See the artwork <span aria-hidden="true">↗</span></span></span></a></div></section>
      <section class="section container"><div class="section-heading"><div><span class="eyebrow">Browse the collection</span><h2>Follow your curiosity</h2></div><p>Explore the collections of published books.</p></div><div class="category-grid">{categorytiles}</div></section>
      <section class="section section-tint"><div class="container"><div class="section-heading"><div><span class="eyebrow">New on our shelves</span><h2>The latest additions</h2></div><a class="text-link" href="latest/">Explore the latest books <span aria-hidden="true">↗</span></a></div>{cards(latest,pre)}</div></section>
      <section class="feature container"><div><span class="eyebrow">A closer look</span><h2>See what’s inside before you shop.</h2><p>Every available sample on this site comes from the actual finished interior. Explore genuine pages, then follow the book’s link to Amazon when you’re ready.</p><a class="button button-dark" href="books/">Browse books</a></div><img src="assets/previews/high-fantasy-realms-3.webp" alt="A detailed waterfall kingdom colouring illustration from High Fantasy Realms" loading="lazy" width="{webp_size(ROOT / "assets/previews/high-fantasy-realms-3.webp")[0]}" height="{webp_size(ROOT / "assets/previews/high-fantasy-realms-3.webp")[1]}"></section>'''
    shell('index.html','Books for curiosity, creativity and everyday life','Explore K.D.Publishing colouring books, word searches, practical guides and journals. See genuine interior previews before you shop.',main,'assets/covers/high-fantasy-realms.webp')


def catalogue():
    main=titleblock('The collection','Books to explore','Browse by category, open a book and see genuine interior pages before visiting Amazon.')
    main+=f'<section class="container section"><div class="collection-meta"><span>{len(BOOKS)} books · {len(CATS)} collections</span></div><nav class="filter-row" aria-label="Book categories">' + ''.join(f'<a href="../categories/{key}/">{e(label)}</a>' for key,(label,_) in CATS.items())+'</nav>'+cards(BOOKS,'../',heading=2)+'</section>'
    shell('books/index.html','All books',f'Browse {len(BOOKS)} K.D.Publishing book listings, including genuine interior previews.',main)
    for key,(name,desc) in CATS.items():
        subset=[b for b in BOOKS if b['category']==key]
        count = f'{len(subset)} ' + ('book' if len(subset) == 1 else 'books')
        content=titleblock('Browse by category',name,desc)+f'<section class="container section"><div class="collection-meta"><span>{count} in this collection</span><a class="text-link" href="../../books/">All books <span aria-hidden="true">↗</span></a></div>'+cards(subset,'../../',heading=2)+'</section>'
        shell(f'categories/{key}/index.html',name,desc,content)


def products():
    from build_resources import book_resources
    for b in BOOKS:
        pre='../../';name=short_title(b); image=b.get('coverImage') or (f'assets/covers/{b["id"]}.webp' if b['coverSource'] else None)
        amazon_url=b.get('amazonUrl') or f'https://www.amazon.co.uk/dp/{b["asin"]}'
        purchase=(f'<a class="button amazon-link" href="{e(amazon_url)}" target="_blank" rel="noopener noreferrer" data-book-id="{b["id"]}" data-asin="{b["asin"]}">Buy on Amazon UK <span aria-hidden="true">↗</span></a>' if b['status']=='live' and b.get('amazonLinkEnabled',True) else '<p class="review-note">Amazon UK purchase link temporarily unavailable. We’re checking this listing.</p>' if b['status']=='live' else '<p class="review-note">Paperback in review. An Amazon purchase link will be added after publication.</p>')
        purchase_note = '<small>Amazon handles your order. Prices and availability may change there.</small>' if b['status']=='live' and b.get('amazonLinkEnabled',True) else ''
        specs=f'<dl class="facts"><div><dt>Format</dt><dd>{e(b.get("format","Paperback"))}</dd></div><div><dt>Author</dt><dd>Kyle Dyer</dd></div><div><dt>Collection</dt><dd>{e(CATS[b["category"]][0])}</dd></div>'+(f'<div><dt>Publisher</dt><dd>{e(b["publisher"])}</dd></div>' if b.get('publisher') else '')+(f'<div><dt>ASIN</dt><dd>{b["asin"]}</dd></div>' if b['asin'] else '')+'</dl>'
        details=('<ul>'+''.join(f'<li>{e(feature)}</li>' for feature in b['features'])+'</ul>' if b.get('features') else '')+(f'<p>{e(b["giftNote"])}</p>' if b.get('giftNote') else '')
        if b.get('companion'):
            companion = next(x for x in BOOKS if x['id'] == b['companion']['id'])
            details += f'<p>{e(b["companion"]["text"])} <a href="../{e(companion["id"])}/">{e(short_title(companion))}</a>.</p>'
        subtitle = f'<p class="product-subtitle">{e(b["subtitle"])}</p>' if b.get('subtitle') else ''
        samples=''.join(preview(b, pre, page) for page in b['previewPages'])
        related=[x for x in BOOKS if x['category']==b['category'] and x['id']!=b['id']][:3]
        related_section = f'''<section class="section container"><div class="section-heading"><div><span class="eyebrow">Keep exploring</span><h2>More from this shelf</h2></div><a class="text-link" href="{pre}categories/{b['category']}/">View category <span aria-hidden="true">↗</span></a></div>{cards(related,pre)}</section>''' if related else ''
        main=f'''<section class="container product"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{pre}">Home</a> / <a href="{pre}categories/{b['category']}/">{e(CATS[b['category']][0])}</a> / <span>{e(name)}</span></nav><div class="product-grid"><div class="product-cover">{cover(b,pre,'eager')}</div><div class="product-info"><span class="eyebrow">{e(CATS[b['category']][0])} {'· In review' if b['status']!='live' else ''}</span><h1>{e(b['title'])}</h1>{subtitle}<p class="lead">{e(b.get('productDescription', b['description']))}</p><div class="purchase" id="purchase"><div class="product-actions">{purchase}<a class="button button-secondary" href="#inside">Look inside <span aria-hidden="true">↓</span></a></div>{purchase_note}</div><div class="product-details">{details}</div>{specs}</div></div></section><section class="section section-tint" id="inside"><div class="container"><div class="section-heading"><div><span class="eyebrow">Actual book pages</span><h2>Look inside</h2></div><p>Reduced-size samples from the finished interior. Tap a page for a closer look.</p></div><div class="preview-grid">{samples}</div></div></section>{related_section}<dialog class="preview-dialog" aria-label="Enlarged interior preview"><button type="button" class="dialog-close" aria-label="Close preview">Close ×</button><img alt="Enlarged book interior sample"><p></p></dialog>'''
        main += book_resources(b["id"], pre)
        shell(f'books/{b["id"]}/index.html', b.get('seoTitle', full_title(b)), b.get('metaDescription', b['description']+' See actual interior pages and book information.'), main, image, b)


def simple():
    latest=sorted((b for b in BOOKS if b['status']=='live'),key=lambda b:b.get('catalogueAdded') or b.get('released') or '',reverse=True)[:8]
    main=titleblock('New on the shelf','Latest releases','Explore the books most recently added to our catalogue, with genuine interior pages to browse.')+'<section class="container section">'+cards(latest,'../',heading=2)+'</section>'
    shell('latest/index.html','Latest releases','The latest K.D.Publishing book releases, with genuine page previews.',main)
    shell('about/index.html','About K.D.Publishing','K.D.Publishing is an independent publishing brand creating puzzle, colouring, practical and reflective books.',titleblock('Who we are','Independent books, many ways to explore','K.D.Publishing creates books for curiosity, creativity and everyday life.')+'<section class="container prose section"><h2>A growing collection</h2><p>Our books range from themed word searches and detailed colouring scenes to practical grassroots football guides and guided journals. Each book has its own purpose, while care with the finished pages ties the collection together.</p><p>Explore a book’s page to see genuine samples from its interior before visiting Amazon.</p><a class="button button-dark" href="../books/">Browse the collection</a></section>')
    contact = titleblock('Here to help','Contact K.D.Publishing','Book enquiries, Amazon order help and your privacy choices.') + '''<div class="container section contact-grid">
      <section class="contact-card contact-enquiries" aria-labelledby="publisher-enquiries"><span class="eyebrow">K.D.Publishing</span><h2 id="publisher-enquiries">Book &amp; publishing enquiries</h2><p>For book questions, feedback or permission requests, email K.D.Publishing:</p><p><a class="contact-email" href="mailto:kdpublishingkyle@gmail.com">kdpublishingkyle@gmail.com</a></p><p>Include the book title and ASIN, if known. If your question concerns a particular interior page, include its page number.</p><a class="button button-dark" href="../books/">Explore the books</a></section>
      <section class="contact-card" aria-labelledby="amazon-orders"><span class="eyebrow">Order support</span><h2 id="amazon-orders">Help with an Amazon order</h2><p>Amazon handles purchases made through our book links. For delivery, returns, refunds or payment questions, use the help options for your order in your Amazon account.</p><p>K.D.Publishing does not take payments or manage Amazon orders.</p><a class="button button-dark" href="https://www.amazon.co.uk/gp/your-account/order-history">Your Orders on Amazon UK</a></section>
      <section class="contact-card" aria-labelledby="privacy-choices"><span class="eyebrow">Your choices</span><h2 id="privacy-choices">Privacy &amp; analytics</h2><p>You can browse our books and previews whether you allow optional analytics or decline.</p><p>Our privacy page explains how analytics and Amazon links work. You can also change your analytics choice there.</p><a class="button button-dark" href="../privacy/">Privacy &amp; analytics</a></section>
    </div>'''
    shell('contact/index.html','Contact','How to get in touch with K.D.Publishing.',contact)
    shell('privacy/index.html','Privacy & analytics','Learn how optional website analytics and Amazon links work on K.D.Publishing.',titleblock('Your choices','Privacy & analytics','How we measure interest in our books.')+'''<section class="container prose section"><h2>Optional analytics</h2><p>Google Analytics 4 is configured, but it does not load until you choose “Allow analytics”. If enabled, Google may set analytics cookies and receive page URLs, referrers, campaign tags, book identifiers and interaction events, including page views, book views, resource views, printable download clicks, related-book clicks, preview opens and outbound Amazon-button clicks. You can decline and still use every part of the site.</p><p>A decision is stored in your browser so the choice remains in effect. You can change it below. Measurement cannot prove that a purchase occurred on Amazon.</p><button class="button button-dark" type="button" id="reset-consent">Change analytics choice</button><h2>Amazon links</h2><p>Clicking “Buy on Amazon UK” opens Amazon in a new tab. Amazon handles its own site, checkout and privacy choices. This website does not collect payment details.</p></section>''')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {ORIGIN}/sitemap.xml\n' if ORIGIN else ''),encoding='utf-8')
    from build_resources import build_resources
    resource_paths = build_resources()
    if ORIGIN:
        paths=['index.html','books/index.html','latest/index.html','about/index.html','contact/index.html','privacy/index.html']+[f'categories/{k}/index.html' for k in CATS]+[f'books/{b["id"]}/index.html' for b in BOOKS]+resource_paths
        (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(url(p.replace("index.html","")))}</loc></url>' for p in paths)+'</urlset>',encoding='utf-8')


if __name__ == '__main__':
    assert len({b['id'] for b in BOOKS})==len(BOOKS)
    assert all(b['category'] in CATS and b['status'] in ('live','in-review') for b in BOOKS)
    assert all(len(short_title(b)) <= 100 for b in BOOKS)
    assert all(bool(b['asin']) == (b['status']=='live') for b in BOOKS)
    assert len({b['asin'] for b in BOOKS if b['asin']})==sum(b['status']=='live' for b in BOOKS)
    home();catalogue();products();simple()
    print(f'Built {len(BOOKS)} product pages')
