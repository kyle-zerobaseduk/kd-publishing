# K.D.Publishing: 30-day acquisition campaign

Prepared 22 October 2026. All social copy and Pins are drafts. Website deployment does not approve social publication. No live queue, account, token or automation is changed by these files.

## What is ready

- `calendar.md`: 30 distinct daily Pins with titles, descriptions, alt text, image URLs and tagged destination links.
- `queue.json`: machine-readable handoff with image hashes, stable IDs and duplicate keys. Every item has `approvedForPublishing: false`, no board ID and no scheduled date.
- `brief.json`: editable copy source. `scripts/build_campaign.py` generates 1000 × 1500 JPEGs using approved covers, real samples and exact vector layouts. It makes no external API calls.
- `social-copy.md`: additional organic drafts for the owner or Grok Manager.
- Three resource sharing images at 1200 × 630, deployed through the website. Visitors receive the existing free resources and genuine book previews.

## Priority and audience

This is an editorial test order, not a proven sales ranking. Traffic is too small and current KDP orders are unavailable. The September commercial strategy prioritised testing the existing football books before Book 3. Preserve that direction: use suitable coaching communities for football discovery, with Pinterest as an additional test. Do not commission another manuscript as part of this campaign.

| Priority | Book | Best first route | Reason for testing | Pins |
| --- | --- | --- | --- | ---: |
| 1 | The First-Time U7 & U8 Football Coach | Free small-squad session, then real book samples | Specific parent-coach problem; useful approved resource and existing commercial priority | 6 |
| 2 | British Nostalgia Word Search | Free original nostalgia printable, then book previews | Existing recorded sample engagement and an immediately useful free activity; evidence still tiny | 8 |
| 3 | I Deleted the Honest Version | Secret Santa guide or genuine excerpts | Seasonal colleague-gift angle with a clear sample-before-buy route | 6 |
| 4 | Cozy Christmas Word Search | Existing book page and real samples | Seasonal test using an existing finished product; no new seasonal article required | 5 |
| 5 | Easy Word Search for Dementia | Real samples of levels and answer page | Newly live paperback with a specific format; suitability must be judged from actual pages | 5 |

The Season Planner remains the football companion on the site. Do not change existing product facts, Amazon destinations or prices. Do not claim any dementia treatment, prevention, memory improvement or suitability for every person. The free nostalgia sheet is separate from the 100-puzzle paperback. The free Secret Santa guide is not a free humour book.

## Release steps for the owner-approved publisher

1. Review the image, copy and destination for each selected `KD30-xx` item. The current owner instruction holds social publishing until separate approval. Approve the specific items/account and intended cadence before any import, upload or posting.
2. Establish one authoritative live account and one scheduler. Read both existing queues and publication history. Do not delete, merge or reset them automatically. Compare canonical destination + image SHA-256 + normalised title; compare visually similar variants as well. Different UTM values alone do not make a Pin new.
3. Confirm actual Pinterest account, granted publishing permissions and the real board IDs. `boardTheme` is a suggested subject, not a real board. The JSON is a planning handoff, **not a native PinBot importer file**. The inspected PinBot product-list import cannot ingest this full Pin queue as-is.
4. If using the existing bot, map approved copy, image and tagged link to individual draft controls. Preserve the pinned image/copy pairing; do not run AI rewriting. Do not enable a second scheduler. Native manual Pinterest publication is an alternative only after account access and approval.
5. Check every public image and destination is reachable after Pages deployment. Verify the selected Pin's preview, correct account/board and link. Start with one individually approved Pin; confirm its returned public Pin ID and destination before continuing. A draft save or simulation is not a published Pin.
6. Day 1 is the first actual approved posting day. Use one distinct Pin per day for 30 days, not three near-duplicate posts per day. This is a manageable experiment, not a Pinterest rule or evidence of an optimal cadence. Suggested operational time: 19:00 Europe/London, adjustable to native audience data. Schedule in the named timezone, not a fixed UTC offset; UK daylight saving ends during late October.
7. If existing approved content already occupies a day, reconcile the calendar rather than stacking blindly. Avoid missed-date backfilling, automatic publication of all overdue drafts or unreviewed text generation.

## Measurement and decisions

Use the existing GA4 property and measurement ID; do not install another tag. Report hostname `kyle-zerobaseduk.github.io` AND page path beginning `/kd-publishing/` (also include the exact no-trailing-slash root). Exclude known owner/test visits only when identifiable. Use separate aggregate queries; do not sum distinct users or sessions across books or days.

Inbound tags use `utm_source=pinterest`, `utm_medium=social`, an existing topic-specific campaign, and `utm_content=growth30_pin_XX`. Retain historical `pinterest / organic` as a separately labelled series and group with `pinterest / social` only for channel-level comparisons. Never put UTMs on internal links or Amazon buttons. No email/name or other personal data in tags.

| Measure | Definition | Source |
| --- | --- | --- |
| Qualified sessions | Engaged production sessions that reach a relevant resource/book page, excluding positively identified testing | GA4 session segment; do not infer by multiplying aggregate figures |
| Amazon-click sessions | Distinct production sessions containing `amazon_click` | GA4 session segment/funnel; event count is a separate diagnostic |
| Sequential book-to-Amazon rate | Sessions that view a book and subsequently click Amazon, divided by eligible book-view sessions in the same scope | GA4 sequential funnel; not an Amazon sales conversion rate |
| Pin discovery and traffic | Impressions, saves, outbound clicks, outbound click rate using the platform's matching definitions | Native Pinterest export; saves are not website sessions |
| Search discovery | Clicks, impressions, query/page CTR and position, with consistent period and property scope | Search Console; sitemap inclusion is not proof of indexing |
| Business result | Actual units, royalties and costs, separately from website intent | KDP and cost records; do not attribute sales to a Pin without supporting evidence |

The earlier proposed 100 qualified sessions and 20 Amazon-click sessions are **stretch test goals**, not forecasts or promised results. The £350 after-tax monthly profit goal remains the business objective. Do not estimate progress from click counts or gross customer spend.

Review days 7, 14, 21 and 30 relative to launch. Day 7: check actual publication and link/measurement integrity. Day 14: compare counts by creative and destination; change one variable where there is useful evidence. Day 21: devote future variants to topics generating relevant engagement, while retaining low-volume uncertainty. Day 30: reconcile publishing, traffic, search and KDP records, then continue or change the test. Do not declare a niche failed if approved posts were never published, account access failed or exposure remained negligible.

If impressions appear but no outbound clicks, inspect the creative promise and destination relevance. If clicks appear but GA4 does not, check dates, redirects, consent and report scope before assuming lost traffic. If Amazon intent appears but sales do not, inspect the live Amazon listing and price with current evidence. These are diagnostic hypotheses, not causal conclusions.

`placement` supports the existing top/after-preview button comparison. Admin registration and enhanced-measurement settings need authorised account inspection; no new custom definitions or key events are activated here. Keep consent gating and free downloads working for people who decline analytics.

## Search Console handoff

Reuse the existing verified property and sitemap. The historical strategy's 35-page count is superseded: the site currently has 44 canonical routes and 26 books. Read property scope first; a root-host property requires filtering to `/kd-publishing/`. Do not create another property, replace the verification token or submit all URLs repeatedly.

Inspect the homepage, five priority books and three approved resources. Record Page indexing exclusions, last crawl, user canonical and Google-selected canonical, plus 28-day Performance exports by query and page. Fix only demonstrated technical issues. Export access is currently required before indexing or ranking outcomes can be verified. The three deferred resource articles and five deferred PDFs remain withheld.

## Sources and validation

- Product facts: the preserved `catalogue/books.json`, approved published resource records, real covers and samples in this repository. No prices, review counts or clinical benefits were added.
- Pinterest recommends 2:3 images, such as 1000 × 1500: https://create.pinterest.com/en-gb/faq/ . This is format guidance, not a posting-frequency rule.
- Google's people-first content guidance: https://developers.google.com/search/docs/fundamentals/creating-helpful-content . Descriptive internal links: https://developers.google.com/search/docs/crawling-indexing/links-crawlable .
- Run `python scripts/check_campaign.py` plus the existing validation workflow. The campaign check covers exact asset dimensions, unique IDs/images/copy, reachable repository routes, UTM structure, file hashes and the disabled publishing gates. It does not prove account publication or sales.
