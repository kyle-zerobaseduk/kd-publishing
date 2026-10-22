"""Moderated website feedback. Never publish raw provider submissions or PII."""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(settings, reviews, book_ids):
    if settings['enabled']:
        if not all(settings.get(k) is True for k in ('ownerApproved', 'liveSubmissionVerified', 'spamProtectionVerified')):
            raise ValueError('Review activation requires owner approval and live submission/spam checks')
        if not re.fullmatch(r'https://formspree\.io/f/[a-zA-Z0-9]{6,32}', settings.get('endpoint', '')):
            raise ValueError('Use only a verified Formspree form endpoint')
    seen, duplicates = set(), set()
    allowed = {'id', 'bookId', 'rating', 'text', 'displayName', 'date', 'consentToPublish', 'moderated'}
    for r in reviews:
        if set(r) != allowed or r['consentToPublish'] is not True or r['moderated'] is not True:
            raise ValueError('Only explicitly moderated, consented public fields may be published')
        if r['bookId'] not in book_ids or type(r['rating']) is not int or not 1 <= r['rating'] <= 5:
            raise ValueError('Unknown book or invalid rating')
        if not isinstance(r['text'], str) or not 20 <= len(r['text'].strip()) <= 2000:
            raise ValueError('Review text must be 20–2000 characters')
        if not isinstance(r['displayName'], str) or len(r['displayName']) > 60:
            raise ValueError('Display name must be optional text up to 60 characters')
        if not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}', r['id']) or r['id'] in seen:
            raise ValueError('Unique opaque review ID required')
        if date.fromisoformat(r['date']) > date.today():
            raise ValueError('Review date cannot be in the future')
        key = (r['bookId'], ' '.join(r['text'].casefold().split()))
        if key in duplicates:
            raise ValueError('Duplicate review text for this book')
        seen.add(r['id']); duplicates.add(key)


def load():
    settings = json.loads((ROOT/'catalogue/review-settings.json').read_text())
    reviews = json.loads((ROOT/'catalogue/reader-reviews.json').read_text())
    ids = {b['id'] for b in json.loads((ROOT/'catalogue/books.json').read_text())}
    validate(settings, reviews, ids)
    return settings, reviews


def render(book, pre, settings=None, reviews=None):
    if settings is None:
        settings, reviews = load()
    rows = [r for r in reviews if r['bookId'] == book['id']]
    if not settings['enabled'] and not rows:
        return ''  # No dead form, invented stars or empty review badge.
    e = lambda s: html.escape(str(s), quote=True)
    body = '<section class="container section reader-reviews" id="reader-reviews"><h2>Reader feedback</h2><p>Feedback submitted to this website. These are not verified Amazon purchase reviews.</p>'
    if rows:
        average = sum(r['rating'] for r in rows) / len(rows)
        body += f'<p class="review-summary"><strong>{average:.1f} out of 5</strong> · {len(rows)} reader {"review" if len(rows) == 1 else "reviews"}</p>'
        for r in sorted(rows, key=lambda r: (r['date'], r['id']), reverse=True):
            body += f'<article class="reader-review"><h3>{e(r["displayName"].strip() or "Anonymous reader")}</h3><p><span aria-hidden="true">{"★"*r["rating"]}{"☆"*(5-r["rating"])}</span> {r["rating"]} out of 5 · <time datetime="{r["date"]}">{r["date"]}</time></p><p class="review-text">{e(r["text"])}</p></article>'
    else:
        body += '<p>No reader reviews have been published yet.</p>'
    if settings['enabled']:
        body += f'''<form class="reader-review-form" action="{e(settings['endpoint'])}" method="post" data-review-form>
<h3>Share your experience of this book</h3><p>All ratings are welcome. Submissions are checked for spam, personal information and abuse before publication; critical feedback is welcome. Please submit once per book.</p>
<input type="hidden" name="book_id" value="{e(book['id'])}"><input type="hidden" name="_subject" value="K.D.Publishing reader feedback">
<fieldset><legend>Your rating (required)</legend><div class="rating-options">{''.join(f'<label><input type="radio" name="rating" value="{n}" required> {n} {"star" if n == 1 else "stars"}</label>' for n in range(1,6))}</div></fieldset>
<label for="review-text">Your review (required, 20–2,000 characters)</label><textarea id="review-text" name="review" rows="6" minlength="20" maxlength="2000" required aria-describedby="review-privacy"></textarea>
<label for="review-name">Public display name (optional)</label><input id="review-name" name="display_name" maxlength="60" autocomplete="off" aria-describedby="review-privacy">
<label class="review-consent"><input type="checkbox" name="reader_confirmation" value="yes" required> I have read or used this book and this is my own honest feedback.</label>
<label class="review-consent"><input type="checkbox" name="consent_to_publish" value="yes" required> I agree that my rating, review and chosen display name may be published on this website.</label>
<p id="review-privacy">Leave the name blank to appear as “Anonymous reader”. Do not include email addresses, order details, medical information or information about children. Formspree processes your submission and technical data for spam prevention. <a href="{pre}privacy/#reader-feedback">Reader feedback privacy</a>.</p>
<div hidden aria-hidden="true"><label>Leave blank<input name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
<button class="button" type="submit">Send for moderation ↗</button><p>You will continue to Formspree to complete any spam check and confirm receipt. Sending a review does not publish it immediately.</p></form>'''
    return body + '</section>'


def privacy():
    settings, rows = load()
    if not settings['enabled'] and not rows:
        return ''
    return '''<section id="reader-feedback"><h2>Reader feedback privacy</h2><p>Reviews are optional and separate from analytics consent. We collect a book identifier, rating, review, optional display name and confirmation of permission to publish. You do not need to supply an email address. If you submit, Formspree receives the content and technical request information for delivery and abuse prevention under its <a href="https://formspree.io/legal/privacy-policy/">privacy policy</a>.</p><p>We publish only moderated feedback with permission, including legitimate critical reviews. Public reviews are stored in the website’s public GitHub repository and may be indexed, cached or retained in repository history. Avoid identifying information; a nickname or no name is best. We aim to review submissions weekly and remove rejected submissions from our working records within 30 days. We retain published feedback while relevant.</p><p>To request correction or removal from the current website, contact kdpublishingkyle@gmail.com with the book title, review date and display name. We cannot guarantee removal of copies already stored in search caches or public repository history. Website feedback does not verify an Amazon purchase.</p></section>'''
