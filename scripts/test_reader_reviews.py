"""Synthetic fixtures stay in tests, never in the public catalogue."""
import copy
import unittest
from datetime import date
from reader_reviews import load, render, validate


class ReaderFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.book = {'id': 'test-book'}
        self.settings = {'enabled': True, 'endpoint': 'https://formspree.io/f/testonly', 'ownerApproved': True, 'liveSubmissionVerified': True, 'spamProtectionVerified': True}
        self.review = {'id': 'test-only-001', 'bookId': 'test-book', 'rating': 1, 'text': 'Synthetic test text, never publish this review.', 'displayName': '', 'date': date.today().isoformat(), 'consentToPublish': True, 'moderated': True}

    def test_production_is_closed_and_empty(self):
        settings, rows = load()
        self.assertFalse(settings['enabled'])
        self.assertEqual(rows, [])
        self.assertEqual(render(self.book, '../../', settings, rows), '')

    def test_activation_requires_all_checks(self):
        for key in ['ownerApproved', 'liveSubmissionVerified', 'spamProtectionVerified']:
            with self.assertRaises(ValueError): validate(dict(self.settings, **{key: False}), [], {'test-book'})
        for endpoint in ['javascript:alert(1)', 'https://evil.test/f/testonly', 'https://formspree.io.evil.test/f/testonly']:
            with self.assertRaises(ValueError): validate(dict(self.settings, endpoint=endpoint), [], {'test-book'})

    def test_moderation_and_privacy(self):
        for row in [dict(self.review, consentToPublish=False), dict(self.review, moderated=False), dict(self.review, email='private@example.test'), dict(self.review, rating=0), dict(self.review, rating=6), dict(self.review, rating=True), dict(self.review, bookId='unknown')]:
            with self.assertRaises(ValueError): validate(self.settings, [row], {'test-book'})

    def test_duplicates(self):
        for row in [copy.deepcopy(self.review), dict(self.review, id='test-only-002', text=self.review['text'].upper())]:
            with self.assertRaises(ValueError): validate(self.settings, [self.review, row], {'test-book'})

    def test_all_ratings_and_exact_average(self):
        rows = [dict(self.review, id=f'test-only-{i}', rating=i, text=self.review['text']+str(i)) for i in range(1,6)]
        validate(self.settings, rows, {'test-book'})
        markup = render(self.book, '../../', self.settings, rows)
        self.assertIn('3.0 out of 5', markup)
        self.assertIn('5 reader reviews', markup)
        for i in range(1,6): self.assertIn(f'{i} out of 5', markup)

    def test_xss_is_plain_text(self):
        row = dict(self.review, displayName='<img src=x onerror=alert(1)>', text='<script>alert("test fixture")</script>')
        validate(self.settings, [row], {'test-book'})
        markup = render(self.book, '../../', self.settings, [row])
        self.assertNotIn('<script>', markup)
        self.assertNotIn('<img', markup)
        self.assertIn('&lt;script&gt;', markup)

    def test_empty_state_and_accessible_fields(self):
        markup = render(self.book, '../../', self.settings, [])
        self.assertNotIn('out of 5', markup)
        self.assertNotIn('★', markup)
        self.assertIn('<legend>Your rating', markup)
        self.assertEqual(markup.count('type="radio"'), 5)
        self.assertIn('name="display_name" maxlength="60"', markup)
        self.assertNotIn('type="email"', markup)
        self.assertIn('name="_gotcha"', markup)
        self.assertIn('not verified Amazon purchase reviews', markup)


if __name__ == '__main__': unittest.main()
