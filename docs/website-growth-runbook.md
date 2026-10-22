# Website growth and conversion release — 22 October 2026

Baseline: main `08cba49ab9b06880121adb9bf7f3259407655537`, PR #12 merged, successful Pages run `39763424920`. 26 live catalogue records, 44 indexed page candidates, five categories, 87 genuine interior previews, three approved resources and three A4 downloads. These are website inventory facts, not proof of Google indexing or current Amazon stock.

## Audit and changes

| Journey step | Baseline finding / business impact | Implementation |
| --- | --- | --- |
| 1. Homepage | Editorial design already strong; broad copy omits the buying route and free-resource offer | Clear publisher identity, book types, Amazon route, free-printable CTA and approved resource cards |
| 2. Catalogue | 26 cards with category navigation but no title/topic search or sorting | Progressive local search, A–Z/recently-added sorting, reset, accessible live result count; full catalogue remains with JS off |
| 3. Book page | Real covers, metadata and samples already present; no reason to invent new specifications | All product claims, subtitles, descriptions, facts, metadata and previews preserved |
| 4. Sample-to-purchase | After samples, the page leads into related books without an Amazon purchase action | A second direct Amazon button follows the sample grid; same destination and a placement parameter |
| 5. Continued exploration | Related puzzle recommendations largely follow catalogue order | Dementia/British/American nostalgia grouped by reader interest; football companions kept together; free-resource links on matching category pages |
| 6. Mobile imagery | Most cover placements download the original derivative even at small widths | 26 additional 370px WebP derivatives; originals unchanged; responsive srcset/sizes |
| 7. Trust/reviews | No submission/moderation backend | Safe, tested but disabled review preparation; no invented social proof; separate owner activation instructions |
| 8. Social landing pages | Category/resource share metadata lacks relevant images | Category and individual resource previews use an existing relevant cover; existing book share images retained |

Nosy Crow's catalogue/resource pathways and Chronicle Books' topic/gift navigation were inspected as comparative references. The relevant lessons are discovery by reader interest and helpful resources, not copying their visual systems or adding ecommerce checkout to an Amazon-linked catalogue.

- https://nosycrow.com/books/
- https://www.chroniclebooks.com/collections/all

## Preservation and security

The dedicated growth preservation gate permits shared-template changes while still comparing catalogue bytes, every book's title/subtitle/copy/facts/previews/structured data/Amazon destination, original asset bytes, Search Console token, resource sources/downloads, sitemap and base CSS against the base commit. Existing page routes are unchanged. No raw source PDF, credentials, customer data, new service account, paid infrastructure, Railway change or KDP edit is part of this release.

GA4 remains opt-in. No search query is stored or transmitted. The new purchase button uses the existing handler once per click. The optional review form is absent from generated pages until approved and verified. Build-time escaping prevents visitor markup from becoming executable HTML. Tests use synthetic fixtures only, never public review records.

## Weekly reporting framework

Use the existing GA4 property and **filter hostname to `kyle-zerobaseduk.github.io` plus page path beginning `/kd-publishing/`**. Exclude all preview/local hostnames. Separate owner/development traffic where it can be identified without collecting more personal data. Do not compare property-wide totals with production-only totals. Existing enhanced-measurement/admin settings have not been changed; verify them before diagnosing duplicate Google-side events.

| Question | Measure | How to interpret |
| --- | --- | --- |
| Are relevant readers arriving? | Sessions and engaged sessions by source/medium + landing page, filtered to production | Compare 28-day periods; separate search, Pinterest, other social, direct and development referrals |
| Which pages attract searchers? | GSC impressions, clicks, CTR and queries by canonical page | Requires authenticated Search Console; sitemap inclusion is not indexing |
| Do readers inspect a book? | `book_page_view`, `preview_open`; distinct users/sessions where available | Repeat opens are not distinct readers |
| Do samples lead to Amazon? | Sessions with `amazon_click` / sessions with `book_page_view`; by book and source | Purchase intent only, not sales; raw event ratio is a diagnostic, not a unique conversion rate |
| Does the new button help? | `amazon_click` by `placement=product_top` / `after_preview` | Register `placement` as an event-scoped dimension if needed; no retroactive data |
| Do free resources help? | `resource_page_view`, `printable_download`, `related_book_click`, then book/Amazon intent | Do not gate downloads behind signup |
| Are reviews working? | Provider received submissions, moderation decisions, published counts | The site event `review_submit_attempt` alone cannot prove receipt |
| Is the business earning? | Separate KDP orders, net royalties, costs and tax provision | Amazon clicks are never booked as sales; no attribution without supporting evidence |

Record release date, exclusions, consent limitations and denominators. Review after 28 days, retaining low-volume uncertainty. Do not interpret tiny changes as statistically established improvements. No automatic reporting schedule or external sheet has been created.

## Three next acquisition actions

1. Publish useful Pinterest creatives linking to the approved British nostalgia free printable and matching book page. Use existing approved cover/interior artwork and a clear sample promise. Never imply clinical benefit for the dementia title.
2. Share the free small-squad U8 session with relevant grassroots coaching audiences, respecting group rules. Lead with the useful session; its contextual link leads to the coaching book and genuine samples.
3. Use the approved Secret Santa resource and workplace-humour preview for seasonal organic posts. Match the audience and landing page; avoid bulk unsolicited messages.

Campaign conventions: use lowercase `utm_source=pinterest`, `utm_medium=social`, `utm_campaign=nostalgia_printable_2026`, and a distinct `utm_content=pin_01` on **inbound website links only**. Existing historic `pinterest / organic` is left intact; group both variants when comparing. No UTM tags on internal links or Amazon buttons. No Pinterest automation/account changes were made.

Example ready-to-use links:
- https://kyle-zerobaseduk.github.io/kd-publishing/resources/puzzles/british-nostalgia-word-search-printable/?utm_source=pinterest&utm_medium=social&utm_campaign=nostalgia_printable_2026&utm_content=pin_01
- https://kyle-zerobaseduk.github.io/kd-publishing/resources/football/u8-small-squad-training-session/?utm_source=facebook&utm_medium=social&utm_campaign=small_squad_session_2026&utm_content=coach_tip_01
- https://kyle-zerobaseduk.github.io/kd-publishing/resources/workplace-humour/secret-santa-gifts-work-colleagues-uk/?utm_source=pinterest&utm_medium=social&utm_campaign=secret_santa_2026&utm_content=pin_01

## Evidence limits

Automated Amazon clients can be refused even when the owner's ordinary session works. All 26 website destinations are validated against preserved catalogue records; that does not freshly verify 26 product titles, paperback selection or stock. Book 26 is owner-confirmed. The cloud browser rejected the Amazon session on this audit, so no repeated requests were made.

Local static/data/tracking tests run in the workspace. Headless browser launch was blocked by workspace socket permissions, so rendered browser tests and Lighthouse run in the existing GitHub Actions public runner. Lighthouse is simulated mobile lab evidence, not real-user Core Web Vitals. Full iPhone Safari/Android-device testing and screen-reader certification are not claimed. Search Console data is not exposed through the connected analytics source in this run; no indexing status or repair is asserted.
