"""Unpublished Phase 2B resource body template using the approved design.

Not imported by build.py and never writes a page. Future publishing must also
integrate canonical metadata, sitemap/count checks and an approved navigation link.
All text fields are plain text, not raw HTML. Approval records belong outside the
public repository; ownerApproved is a publication gate, not factual validation.
"""
import re
from datetime import date

from build import BOOKS, cards, e, titleblock

CLUSTERS = {'football': 'Grassroots football coaching', 'puzzles': 'Word searches & puzzles',
            'workplace-humour': 'Workplace humour & gifts'}


def render_resource(record):
    """Return an approved resource's main content without publishing it."""
    if record.get('ownerApproved') is not True:
        raise ValueError('Owner approval of content and source claims is required')
    cluster = record['cluster']
    if cluster not in CLUSTERS or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', record['slug']):
        raise ValueError('Invalid resource route')
    reviewed = date.fromisoformat(record['reviewedDate'])
    if reviewed > date.today():
        raise ValueError('Review date cannot be in the future')
    if not record['author'].strip() or not record['sections']:
        raise ValueError('An accountable author and useful HTML content are required')
    pre = '../../../'
    body = f'<nav class="breadcrumbs container" aria-label="Breadcrumb"><a href="{pre}">Home</a> / <a href="{pre}resources/">Resources</a> / <a href="../">{e(CLUSTERS[cluster])}</a> / <span>{e(record["title"])}</span></nav>'
    body += titleblock(CLUSTERS[cluster], record['title'], record['summary'])
    body += f'<article class="container prose section"><p>By {e(record["author"])} · Reviewed <time datetime="{reviewed.isoformat()}">{reviewed.strftime("%d %B %Y")}</time></p>'
    for section in record['sections']:
        body += f'<section><h2>{e(section["heading"])}</h2>'
        body += ''.join(f'<p>{e(paragraph)}</p>' for paragraph in section['paragraphs'])
        body += '</section>'
    downloads = record.get('downloads', [])
    if downloads:
        body += '<section><h2>Printable resources</h2>'
        for item in downloads:
            if not re.fullmatch(r'assets/resources/[a-z0-9/-]+\.pdf', item['path']) or '..' in item['path']:
                raise ValueError('Download must be an approved PDF under assets/resources/')
            body += f'<p><a class="text-link" href="{pre}{e(item["path"])}">{e(item["label"])}</a> · PDF · {e(item["printNotes"])}</p>'
        body += '</section>'
    sources = record.get('sources', [])
    if sources:
        body += '<section><h2>Sources and further reading</h2><ul>'
        for source in sources:
            if not source['url'].startswith('https://'):
                raise ValueError('Source must have a secure absolute URL')
            body += f'<li><a href="{e(source["url"])}">{e(source["label"])}</a></li>'
        body += '</ul></section>'
    body += '</article>'
    selected = record['relatedBookIds']
    if not 1 <= len(selected) <= 2 or len(selected) != len(set(selected)):
        raise ValueError('Choose one or two genuinely relevant books')
    by_id = {b['id']: b for b in BOOKS}
    related = [by_id[book_id] for book_id in selected]
    body += '<section class="container section"><div class="section-heading"><div><span class="eyebrow">Explore further</span><h2>Related books</h2></div></div>' + cards(related, pre) + '</section>'
    return body
