"""Check the unpublished template's approval gate, safe text and book links."""
from copy import deepcopy
from datetime import date

from resource_template import render_resource

record = {'ownerApproved': True, 'cluster': 'football', 'slug': 'test-resource',
          'title': 'Template test', 'summary': 'Fixture content only', 'author': 'Template test author',
          'reviewedDate': date.today().isoformat(),
          'sections': [{'heading': 'Test heading', 'paragraphs': ['<script>alert(1)</script>']}],
          'relatedBookIds': ['season-planner'],
          'downloads': [{'path': 'assets/resources/test-sheet.pdf', 'label': 'Test sheet', 'printNotes': 'A4'}],
          'sources': [{'url': 'https://www.englandfootball.com/', 'label': 'England Football'}]}
body = render_resource(record)
assert '<script>' not in body and '&lt;script&gt;' in body
assert body.count('<h1>') == 1 and '<h2>Test heading</h2>' in body
assert 'href="../../../books/season-planner/"' in body
for change in [{'ownerApproved': False}, {'slug': '../unsafe'}, {'relatedBookIds': []},
               {'downloads': [{'path': 'assets/resources/../secret.pdf', 'label': 'Test', 'printNotes': 'A4'}]}]:
    candidate = deepcopy(record); candidate.update(change)
    try:
        render_resource(candidate)
    except (ValueError, KeyError):
        continue
    raise AssertionError(change)
print('PASS: unpublished resource template approval gate, safe text, valid route/download scope and related-book links')
