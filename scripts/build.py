"""Build static, linkable catalogue pages. Run `python scripts/build.py`."""
import html
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = json.loads((ROOT / 'catalogue/books.json').read_text())
ORIGIN = os.environ.get('KD_SITE_URL', '').rstrip('/')
GA_ID = os.environ.get('KD_GA4_ID', '')
CATS = {
    'puzzles': ('Word Search & Puzzle Books', 'Find a puzzle for a quiet moment, a favourite subject or a thoughtful gift.'),
    'colouring': ('Colouring & Activity Books', 'Detailed scenes and creative places to make your own.'),
    'guides': ('Football Coaching Books', 'Practical support for first-time U7 and U8 grassroots coaches.'),
    'journals': ('Planners & Journals', 'Space for reflection, routines and the things worth recording.'),
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
    return f'{ORIGIN}/{path}' if ORIGIN else ''


def cover(book, pre, loading='lazy'):
    image = ROOT / 'assets/covers' / f"{book['id']}.webp"
    if image.exists():
        return f'<img src="{pre}assets/covers/{book["id"]}.webp" alt="Front cover of {e(short_title(book))}" width="740" height="970" loading="{loading}">'
    return f'<div class="cover-pending" role="img" aria-label="Cover artwork pending for {e(short_title(book))}"><span>K.D.PUBLISHING</span><strong>{e(short_title(book))}</strong><small>Cover image pending</small></div>'


def card(book, pre):
    name = short_title(book)
    status = '<span class="pill">In review</span>' if book['status'] != 'live' else ''
    return f'''<a class="book-card" href="{pre}books/{book['id']}/" aria-label="View {e(name)} and its interior preview">
      <div class="book-art">{cover(book, pre)}</div><div class="book-copy"><span class="eyebrow">{e(CATS[book['category']][0])}</span>
      <h3>{e(name)}</h3><p>{e(book['description'])}</p>{status}<span class="text-link">See inside <span aria-hidden="true">↗</span></span></div></a>'''


def cards(books, pre):
    return '<div class="book-grid">' + ''.join(card(b, pre) for b in books) + '</div>'


def shell(path, title, description, main, image=None, book=None):
    pre = prefix(path)
    canonical = f'<link rel="canonical" href="{e(url(path))}">' if ORIGIN else ''
    ogurl = f'<meta property="og:url" content="{e(url(path))}">' if ORIGIN else ''
    ogimage = f'<meta property="og:image" content="{e(url(image) if ORIGIN else pre + image)}">' if image else ''
    structured = ''
    if book:
        data = {'@context':'https://schema.org','@type':'Book','name':full_title(book),'author':{'@type':'Person','name':'Kyle Dyer'}}
        if ORIGIN:
            data['url'] = url(path)
        if book['asin']:
            data['identifier'] = {'@type':'PropertyValue','propertyID':'ASIN','value':book['asin']}
        structured = '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False).replace('<','\\u003c') + '</script>'
    nav = f'''<header class="header"><div class="container header-inner"><a class="brand" href="{pre}" aria-label="K.D.Publishing home"><span class="brand-mark">K<span>.</span>D<span>.</span></span><span class="brand-type">PUBLISHING</span></a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Open navigation"><span></span><span></span><span></span></button>
      <nav id="primary-nav" class="nav" aria-label="Primary"><a href="{pre}">Home</a><div class="nav-group"><a href="{pre}books/">Books</a><button class="submenu-toggle" type="button" aria-expanded="false" aria-label="Show book categories">⌄</button><div class="submenu">{''.join(f'<a href="{pre}categories/{key}/">{e(label)}</a>' for key,(label,_) in CATS.items())}</div></div><a href="{pre}latest/">Latest releases</a><a href="{pre}about/">About</a><a href="{pre}contact/">Contact</a></nav></div></header>'''
    footer = f'''<footer class="footer"><div class="container footer-inner"><div><a class="footer-brand" href="{pre}">K.D.PUBLISHING</a><p>Books for curiosity, creativity and everyday life.</p></div><div><a href="{pre}books/">All books</a><a href="{pre}about/">About</a><a href="{pre}contact/">Contact</a><a href="{pre}privacy/">Privacy & analytics</a></div><small>© {date.today().year} K.D.Publishing</small></div></footer>'''
    consent = '<div class="cookie-notice" id="cookie-notice" hidden><p>May we use optional analytics to understand which books and previews people view? <a href="'+pre+'privacy/">Privacy details</a></p><div><button type="button" data-consent="reject">No thanks</button><button type="button" class="button button-small" data-consent="accept">Allow analytics</button></div></div>'
    config = json.dumps({'ga4':GA_ID,'book':({'id':book['id'],'title':full_title(book),'category':book['category'],'asin':book['asin']} if book else None)}).replace('<','\\u003c')
    out = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>{e(title)} | K.D.Publishing</title><meta name="description" content="{e(description)}">{canonical}<meta property="og:type" content="{'book' if book else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">{ogurl}{ogimage}<meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="{pre}styles.css"><script type="application/json" id="site-config">{config}</script><script defer src="{pre}site.js"></script>{structured}</head><body><a class="skip-link" href="#main">Skip to content</a>{nav}<main id="main">{main}</main>{footer}{consent}</body></html>'''
    destination = ROOT / path
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(out,encoding='utf-8')


def titleblock(kicker, title, text=''):
    return f'<div class="page-head container"><span class="eyebrow">{e(kicker)}</span><h1>{e(title)}</h1><p>{e(text)}</p></div>'


def home():
    pre=''
    hero=next(b for b in BOOKS if b['id']=='high-fantasy-realms')
    latest=sorted((b for b in BOOKS if b['status']=='live'),key=lambda b:b['released'],reverse=True)[:4]
    categorytiles=''.join(f'<a class="category-tile" href="categories/{key}/"><span class="eyebrow">{str(sum(b["category"]==key for b in BOOKS))} {"title" if sum(b["category"]==key for b in BOOKS)==1 else "titles"}</span><h3>{e(label)}</h3><span aria-hidden="true">↗</span></a>' for key,(label,_) in CATS.items())
    main=f'''<section class="hero"><div class="container hero-grid"><div class="hero-copy"><span class="eyebrow">Independent publishing · Est. 2026</span><h1>Books made to <em>take you somewhere.</em></h1><p>From imaginative colouring and themed puzzles to practical coaching guides and thoughtful journals, explore the growing K.D.Publishing collection.</p><div class="actions"><a class="button" href="books/">Explore all books <span aria-hidden="true">↗</span></a><a class="quiet-link" href="latest/">What’s new</a></div></div><a class="hero-book" href="books/high-fantasy-realms/" aria-label="Explore High Fantasy Realms"><span class="hero-book-image">{cover(hero,pre,'eager')}</span><span>Featured release <strong>High Fantasy Realms</strong><span class="text-link">See the artwork ↗</span></span></a></div></section>
      <section class="section container"><div class="section-heading"><div><span class="eyebrow">Browse the collection</span><h2>Follow your curiosity</h2></div><p>Explore four collections of published books.</p></div><div class="category-grid">{categorytiles}</div></section>
      <section class="section section-tint"><div class="container"><div class="section-heading"><div><span class="eyebrow">Recently released</span><h2>Fresh from K.D.Publishing</h2></div><a class="text-link" href="latest/">See all recent releases ↗</a></div>{cards(latest,pre)}</div></section>
      <section class="feature container"><div><span class="eyebrow">A closer look</span><h2>See what’s inside before you shop.</h2><p>Every available sample on this site comes from the actual finished interior. Explore genuine pages, then follow the book’s link to Amazon when you’re ready.</p><a class="button button-dark" href="books/">Browse books</a></div><img src="assets/previews/high-fantasy-realms-3.webp" alt="A detailed waterfall kingdom colouring illustration from High Fantasy Realms" loading="lazy" width="850" height="1100"></section>'''
    shell('index.html','Books for curiosity, creativity and everyday life','Explore K.D.Publishing colouring books, word searches, practical guides and journals. See genuine interior previews before you shop.',main,'assets/covers/high-fantasy-realms.webp')


def catalogue():
    main=titleblock('The collection','Books to explore','Browse by category, open a book and see genuine interior pages before visiting Amazon.')
    main+='<section class="container section"><div class="filter-row" aria-label="Book categories">' + ''.join(f'<a href="../categories/{key}/">{e(label)}</a>' for key,(label,_) in CATS.items())+'</div>'+cards(BOOKS,'../')+'</section>'
    shell('books/index.html','All books',f'Browse {len(BOOKS)} K.D.Publishing book listings, including genuine interior previews.',main)
    for key,(name,desc) in CATS.items():
        subset=[b for b in BOOKS if b['category']==key]
        content=titleblock('Browse by category',name,desc)+'<section class="container section">'+cards(subset,'../../')+'</section>'
        shell(f'categories/{key}/index.html',name,desc,content)


def products():
    for b in BOOKS:
        pre='../../';name=short_title(b); image=f'assets/covers/{b["id"]}.webp' if b['coverSource'] else None
        purchase=(f'<a class="button amazon-link" href="https://www.amazon.co.uk/dp/{b["asin"]}" target="_blank" rel="noopener noreferrer" data-book-id="{b["id"]}" data-asin="{b["asin"]}">Buy on Amazon UK <span aria-hidden="true">↗</span></a><small>Amazon handles your order. Prices and availability may change there.</small>' if b['status']=='live' else '<p class="review-note">Paperback in review. An Amazon purchase link will be added after publication.</p>')
        specs=f'<div class="facts"><div><dt>Format</dt><dd>Paperback</dd></div><div><dt>Author</dt><dd>Kyle Dyer</dd></div><div><dt>Collection</dt><dd>{e(CATS[b["category"]][0])}</dd></div>'+(f'<div><dt>ASIN</dt><dd>{b["asin"]}</dd></div>' if b['asin'] else '')+'</div>'
        samples=''.join(f'<button class="preview" type="button" data-preview="{pre}assets/previews/{b["id"]}-{p}.webp" data-page="{p}" aria-label="Enlarge interior sample page {p} of {e(name)}"><img src="{pre}assets/previews/{b["id"]}-{p}.webp" alt="Actual interior page {p} from {e(name)}" width="850" height="1100" loading="lazy"><span>Page {p} · Enlarge ↗</span></button>' for p in b['previewPages'])
        related=[x for x in BOOKS if x['category']==b['category'] and x['id']!=b['id']][:3]
        main=f'''<section class="container product"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{pre}">Home</a> / <a href="{pre}categories/{b['category']}/">{e(CATS[b['category']][0])}</a> / <span>{e(name)}</span></nav><div class="product-grid"><div class="product-cover">{cover(b,pre,'eager')}</div><div class="product-info"><span class="eyebrow">{e(CATS[b['category']][0])} {'· In review' if b['status']!='live' else ''}</span><h1>{e(full_title(b))}</h1><p class="lead">{e(b['description'])}</p><dl>{specs}</dl><div class="purchase">{purchase}</div><a class="text-link" href="#inside">Look inside ↓</a></div></div></section><section class="section section-tint" id="inside"><div class="container"><div class="section-heading"><div><span class="eyebrow">Actual book pages</span><h2>Look inside</h2></div><p>Reduced-size samples from the finished interior. Tap a page for a closer look.</p></div><div class="preview-grid">{samples}</div></div></section><section class="section container"><div class="section-heading"><div><span class="eyebrow">Keep exploring</span><h2>More from this shelf</h2></div><a class="text-link" href="{pre}categories/{b['category']}/">View category ↗</a></div>{cards(related,pre)}</section><dialog class="preview-dialog" aria-label="Enlarged interior preview"><button type="button" class="dialog-close" aria-label="Close preview">Close ×</button><img alt="Enlarged book interior sample"><p></p></dialog>'''
        shell(f'books/{b["id"]}/index.html',full_title(b),b['description']+' See actual interior pages and book information.',main,image,b)


def simple():
    latest=sorted((b for b in BOOKS if b['status']=='live'),key=lambda b:b['released'],reverse=True)[:8]
    main=titleblock('New on the shelf','Latest releases','Recent paperback releases from the current K.D.Publishing catalogue.')+'<section class="container section">'+cards(latest,'../')+'</section>'
    shell('latest/index.html','Latest releases','The latest K.D.Publishing book releases, with genuine page previews.',main)
    shell('about/index.html','About K.D.Publishing','K.D.Publishing is an independent publishing brand creating puzzle, colouring, practical and reflective books.',titleblock('Who we are','Independent books, many ways to explore','K.D.Publishing creates books for curiosity, creativity and everyday life.')+'<section class="container prose section"><h2>A growing collection</h2><p>Our books range from themed word searches and detailed colouring scenes to practical grassroots football guides and guided journals. Each book has its own purpose, while care with the finished pages ties the collection together.</p><p>Explore a book’s page to see genuine samples from its interior before visiting Amazon.</p><a class="button button-dark" href="../books/">Browse the collection</a></section>')
    shell('contact/index.html','Contact','How to get in touch with K.D.Publishing.',titleblock('Get in touch','Contact K.D.Publishing','For book and publishing enquiries.')+'<section class="container prose section"><h2>Contact details coming soon</h2><p>A public contact address has not yet been confirmed. Please check back for the verified contact route. For an existing Amazon order, use the help options in your Amazon account.</p></section>')
    shell('privacy/index.html','Privacy & analytics','Learn how optional website analytics and Amazon links work on K.D.Publishing.',titleblock('Your choices','Privacy & analytics','How we measure interest in our books.')+'''<section class="container prose section"><h2>Optional analytics</h2><p>The site is prepared for Google Analytics 4, but no analytics service loads until a measurement ID is configured and you choose “Allow analytics”. If enabled, Google may set analytics cookies and receive page URLs, referrers, campaign tags, book identifiers and interaction events, including page views, book views, preview opens and outbound Amazon-button clicks. You can decline and still use every part of the site.</p><p>A decision is stored in your browser so the choice remains in effect. You can change it below. Measurement cannot prove that a purchase occurred on Amazon.</p><button class="button button-dark" type="button" id="reset-consent">Change analytics choice</button><h2>Amazon links</h2><p>Clicking “Buy on Amazon UK” opens Amazon in a new tab. Amazon handles its own site, checkout and privacy choices. This website does not collect payment details.</p></section>''')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {ORIGIN}/sitemap.xml\n' if ORIGIN else ''),encoding='utf-8')
    if ORIGIN:
        paths=['index.html','books/index.html','latest/index.html','about/index.html','contact/index.html','privacy/index.html']+[f'categories/{k}/index.html' for k in CATS]+[f'books/{b["id"]}/index.html' for b in BOOKS]
        (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(url(p.replace("index.html","")))}</loc></url>' for p in paths)+'</urlset>',encoding='utf-8')


if __name__ == '__main__':
    assert len({b['id'] for b in BOOKS})==len(BOOKS)
    assert all(b['category'] in CATS and b['status'] in ('live','in-review') for b in BOOKS)
    assert all(bool(b['asin']) == (b['status']=='live') for b in BOOKS)
    assert len({b['asin'] for b in BOOKS if b['asin']})==sum(b['status']=='live' for b in BOOKS)
    home();catalogue();products();simple()
    print(f'Built {len(BOOKS)} product pages')
