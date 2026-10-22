"""Small progressive enhancements using existing, verified catalogue content."""

def resource_teasers(pre='', category=None):
    from build import e
    from build_resources import selected
    from resource_content import route
    clusters = {'guides': 'football', 'puzzles': 'puzzles', 'humour': 'workplace-humour'}
    rows = [r for r in selected() if category is None or r['cluster'] == clusters.get(category)]
    if not rows:
        return ''
    links = ''.join(f'<article class="resource-teaser"><span class="eyebrow">Free resource</span><h3><a href="{pre}{route(r).removesuffix("index.html")}">{e(r["title"])}</a></h3><p>{e(r["summary"])}</p></article>' for r in rows)
    return f'<section class="container section discovery-resources"><div class="section-heading"><div><span class="eyebrow">Try something today</span><h2>Free ideas, ready to use</h2></div><a class="text-link" href="{pre}resources/">All free resources ↗</a></div><div class="resource-teasers">{links}</div></section>'


def catalogue_controls():
    return '''<div class="catalogue-tools" hidden><div><label for="book-search">Find a book</label><input id="book-search" type="search" maxlength="100" placeholder="Try nostalgia, football or Christmas" aria-controls="catalogue-results" autocomplete="off"></div><div><label for="book-sort">Sort books</label><select id="book-sort" aria-controls="catalogue-results"><option value="featured">Collection order</option><option value="newest">Recently added</option><option value="title">Title A–Z</option></select></div><button class="button button-secondary" type="button" id="clear-search">Reset</button><p id="book-result-count" role="status" aria-live="polite" aria-atomic="true"></p></div><p id="book-no-results" hidden>No matching books. Try a different word or reset the search.</p>'''


def related_books(book, books):
    # Same subject/reader before the broader shelf; no popularity or sales claims.
    groups = [
        ['easy-word-search-for-dementia', 'british-nostalgia', 'nostalgic-word-search-1950s-1980s'],
        ['first-time-football-coach', 'season-planner'],
    ]
    preferred = next((g for g in groups if book['id'] in g), [])
    candidates = [b for b in books if b['id'] != book['id'] and b['category'] == book['category']]
    return sorted(candidates, key=lambda b: (b['id'] not in preferred, preferred.index(b['id']) if b['id'] in preferred else 99))[:3]
