# Reader feedback: preparation and activation

Status: **disabled**, no submissions accepted and no reviews published. Do not call this a live review service. The site emits no form, placeholder stars, average or review count while there are no published reviews and the service is disabled.

## Proposed no-cost service

Use one Formspree Free form for the catalogue, with a book identifier in each submission. Official pricing checked 22 October 2026 states 50 submissions per month; verify eligibility and current limits during setup. Do not enter payment details or upgrade automatically. This is limited capacity, not unlimited free infrastructure.

Compared with giscus (GitHub-account comments and reactions, not a native 1–5 review system), a moderated form better fits ordinary readers. A custom database/worker adds authentication, abuse handling and maintenance. Formspree has built-in filtering, optional hosted CAPTCHA, domain restrictions and rate limits; it does **not** establish that someone bought or used a book.

Sources:
- https://formspree.io/plans
- https://help.formspree.io/articles/form-and-project-settings/recaptcha-settings
- https://help.formspree.io/articles/form-and-project-settings/system-limits
- https://help.formspree.io/articles/form-and-project-settings/restrict-to-domain
- https://help.formspree.io/articles/building-your-form/honeypot-spam-filtering/
- https://formspree.io/legal/privacy-policy/
- https://formspree.io/security/
- https://giscus.app/

## Exact owner decision and setup still needed

Approve Formspree as the processor of optional book identifier, 1–5 rating, written feedback, optional public nickname, publication permission and technical request data used for abuse prevention. Approve the privacy text in `scripts/reader_reviews.py`, including public GitHub history/caching and the moderation/retention plan. Formspree may process data outside the UK; review its terms, privacy policy and applicable processing arrangements. No account or agreement has been created/accepted for this project.

After approval, the owner creates/signs in to a Free account, verifies the receiving address and creates one form. Supply only its public `https://formspree.io/f/<form-id>` endpoint. No private API key is required in this website. Keep notifications/private submission history out of the public repository.

Enable provider spam filtering and hosted reCAPTCHA. Restrict the form to `kyle-zerobaseduk.github.io`. Domain restrictions rely on referrers and are not authentication; check the spam folder for genuine privacy-browser submissions. Do not require email, order numbers or upload fields. Native HTML POST keeps hosted CAPTCHA and provider receipt/error pages available without injecting third-party scripts before submission.

Before activation, use an isolated temporary test page and verify:
1. A consenting test submission reaches the private provider inbox; never publish it as a genuine review.
2. Missing rating, short/oversized text and missing consent cannot be published. Client validation is usability only; moderation/build validation is authoritative.
3. Provider CAPTCHA, honeypot, domain restriction, quota/error messages and rate limits behave as documented. Do not load-test the provider.
4. Test on Android Chrome and iPhone Safari; verify assistive-technology labels and provider return/error flow. Local rendering tests do not verify a remote backend.
5. Duplicate, forged book IDs, personal data and HTML payloads are rejected or safely handled in moderation.
6. Confirm Free plan capacity and that no paid plan/auto-upgrade is selected. If capacity is exhausted, disable new submissions until capacity returns or the owner selects a different no-cost solution.

Then set the real endpoint and the three verification/approval flags in `catalogue/review-settings.json`. Set `enabled` to true only after all evidence is recorded. Update activation-specific tests, run the full suite, review the live privacy notice, and deploy in a separate controlled PR. Do not set flags merely to make the build pass.

## Fair moderation and publication

Review weekly, in arrival order. Apply the same rules to every rating. Publish relevant, first-hand, lawful criticism as well as praise. Reject only spam, duplicate submissions, unrelated content, impersonation, abuse, personal/medical information, or submissions without permission. Do not condition publication on positive sentiment, offer incentives for favourable ratings or imply Amazon verification.

Keep a private moderation log with provider submission ID, date, decision and objective reason. Compare repeated text and suspicious patterns; one submission per reader/book is a policy, not a verified identity guarantee. Without accounts or proof of purchase, this system cannot guarantee the uniqueness or truthfulness of each visitor. Never label it “verified purchase”.

Copy **only approved public fields** into `catalogue/reader-reviews.json`: opaque unique `id`, known `bookId`, integer `rating` 1–5, `text` (20–2000 characters), optional `displayName` (empty string permitted, max 60), ISO `date`, `consentToPublish: true`, `moderated: true`. Do not bulk-import raw exports. An unknown field, duplicate ID/text, invalid rating or missing permission fails the build. The renderer escapes all visitor text. Average and count are calculated only from these approved records, and every rating is displayed in date order. No aggregateRating/Review search markup is emitted.

Public GitHub history is durable: use nicknames or anonymous publication, never private email/IP/technical metadata. Aim to delete rejected working submissions within 30 days. A removal request removes the current page entry, but historic copies and search caches may remain; investigate a history-purge request separately if necessary.

## Measurement

`review_submit_attempt` is consent-controlled and contains only `book_id`. Native POST leaves the site for provider verification; the event is **not successful receipt or publication**. Use provider inbox counts for accepted submissions and the public JSON count for published reviews. Never send review text, display names, ratings or private contact details to GA4.
