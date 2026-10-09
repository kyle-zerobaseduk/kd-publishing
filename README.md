# K.D.Publishing website

Static publishing catalogue built from `catalogue/books.json`. The 24 September 2026 KDP Bookshelf screenshots were transcribed into 23 listings: 22 live paperbacks and British Nostalgia in review. The live ASINs come from those screenshots, not the former site. The screenshot evidence is kept outside the public repository.

## Build and add a book

1. Verify the title, status, ASIN and category against the current KDP Bookshelf. Add or edit **one record** in `catalogue/books.json`: `id` (unique URL slug), `title`, `subtitle`, `shortTitle` (catalogue card), `category`, `status`, `released`, `asin` and `description`. Available categories are `puzzles`, `colouring`, `guides` and `journals`. A book in review has `status: "in-review"`, `asin: null` and `released: null`; only confirmed live books get an Amazon button. `title` and `subtitle` form the full book title on its page.
2. Identify the latest approved wrap cover and finished interior PDF. Record their exact filenames as `coverSource` and `interiorSource`. Set real 1-based `previewPages`; do not create fictitious page samples. If no approved cover is identified, leave `coverSource: null`, so the site clearly displays a pending cover.
3. With those private PDFs in a directory outside this repository, run `python scripts/generate_assets.py /path/to/private/source/directory`. The script creates only reduced WebP front covers and page previews. **Never commit source PDFs, print-quality images or production masters.**
4. Run `python scripts/build.py`, `python scripts/check_site.py`, and `node scripts/test_tracking.js`. The builder updates catalogue cards, category and book pages, latest releases, metadata, Amazon buttons and the sitemap from the same record. Open the output locally with `python -m http.server` before proposing a deployment. The `scripts/build.py` category labels and hand-picked home hero are optional editorial settings for a new category or featured book; ordinary book updates do not require editing templates.

For a live book whose Amazon UK destination has not been confirmed to work, set `amazonLinkEnabled: false` in its catalogue record. Its page and verified ASIN remain visible, while its Buy button is withheld. Remove that flag only after a normal browser confirms the exact UK product page opens to the matching title. For a confirmed book-specific destination, set `amazonUrl` in that same record; all other books use the normal `https://www.amazon.co.uk/dp/<ASIN>` URL. The Season Planner uses the Amazon Share link `https://amzn.eu/d/09mIs6KH`, supplied from the verified live Amazon UK listing with ASIN `B0HJ6HGVC4`.

Static files require no paid hosting or runtime service. The verified production address is `https://kyle-zerobaseduk.github.io/kd-publishing/` (the existing GitHub Pages site). The builder uses it for canonical URLs, absolute Open Graph URLs, the sitemap and `robots.txt`. Set `KD_SITE_URL` only if the production domain actually changes; rebuild and check every generated page before deployment. The separate owner-only ChatGPT Sites preview is not the production domain.

## October 2026 catalogue update

`i-deleted-the-honest-version` adds the Humour & Gift Books collection. `british-nostalgia` updates the existing in-review record to live. KDP Bookshelf screenshots dated 4 October confirm ASINs `B0HLSTBBL9` and `B0HLSNSY9N`. The owner supplied UK Share links `https://amzn.eu/d/0cXanCA3` (Honest Version) and `https://amzn.eu/d/0flnKdY0` (British Nostalgia). Their HTTP redirects were matched to the confirmed ASINs on amazon.co.uk; both purchase buttons are enabled and use these exact Share links. Amazon rejects the automated session after the redirect, so the final product-page rendering could not be independently checked.

Priority records can use the optional `features`, `giftNote`, `publisher`, `format`, `coverSize` and `coverTrim` fields. `coverTrim` specifies front-cover trim width/height in PDF points, excluding the wrap's 9-point bleed. `catalogueAdded` records the date the live title was added to the website, for recent-release ordering when the publication date is unverified; it is not a publication-date claim.

The new front-cover derivatives use the supplied final approved PDFs. Four workplace-humour samples use pages 5, 8, 14 and 55 of the supplied 62-page interior candidate. Existing British Nostalgia samples are retained. Source PDFs and listing screenshots stay outside the public repository. No prices, publication dates or book page counts are added to customer-facing pages.

## Analytics

**Configured stream: `G-64LMW6KFB7`.** The builder embeds this genuine GA4 Web Stream Measurement ID into each page by default. `KD_GA4_ID` remains an optional build-time override. This does not load Google Analytics until the visitor opts in. The site sends its own page views, preview and Amazon events. Read the Google-side Enhanced measurement settings and check for actual duplication before proposing an account change; do not switch off all enhanced features blindly. Do not paste a second Google tag or add Google Tag Manager. Check a consented test visit in GA4 Realtime before treating data collection as verified. Preview testing with the same ID can mix preview traffic into production reports; identify those test visits by their preview hostname or exclude them in reporting.

The site shows an opt-in choice and **does not load Google Analytics or store campaign parameters before consent**. The browser stores the choice; the privacy page lets visitors reopen it and clears this site's GA cookies when the choice is reset. Setting `KD_GA4_ID=''` for a test build disables GA requests entirely. People who decline are not measured.

Events (only after consent):

| Event | Meaning | Parameters |
| --- | --- | --- |
| `page_view` | A page loaded | page title/location/referrer; acquisition handled by GA4 |
| `book_page_view` | A product page loaded | `book_id`, short display `book_title`, `category`, `asin` |
| `preview_open` | A sample enlarged | same book fields plus `page_number` |
| `amazon_click` | The Amazon UK button clicked | same book fields plus `destination_url` |

Available `utm_source`, `utm_medium`, `utm_campaign`, and `utm_content` are carried in the visitor's session **after consent**. The landing page URL and referrer are preserved for GA4. For links posted by K.D.Publishing, use lowercase, consistent values such as `?utm_source=pinterest&utm_medium=social&utm_campaign=high_fantasy_realms_launch` (other sources: `instagram`, `facebook`, `x`; optional `utm_content=pin_01`). Use these tags on links **to this website**, never on internal site links or Amazon destinations. Ordinary Google search and other referrals can be identified automatically where a referrer is available; direct/unknown traffic may remain `(direct) / (none)`.

In GA4, use the Realtime report to confirm events; use Reports → Acquisition for source/medium and an Explore free-form report with `book_id` and event name to compare `book_page_view`, `preview_open` and `amazon_click`. Register `book_id`, `book_title`, `category`, `asin`, `destination_url` and `page_number` as event-scoped custom dimensions if you need them in GA4 reports; GA4's default event metrics provide counts. Divide a book's `amazon_click` event count by its `book_page_view` event count for its website-to-Amazon click-through rate. This tracks click interest, **not sales or Amazon conversions**; repeat clicks and visits affect the ratio. Traffic source depends on available campaign/referrer information and consent.

The event's `book_title` uses the concise `shortTitle` from the same catalogue record; the full title stays on the product page. This keeps the event value within GA4's 100-character parameter limit. Use stable `book_id` as the reporting key when titles change.

## Phase 2A SEO foundation (9 October 2026)

The dedicated SEO PR preserves the approved PR #5 appearance, all 24 books/ASINs/Amazon destinations, 78 previews, consent and tracking. It provides concise search titles, evidence-based descriptions for the five priority books, richer Book metadata, breadcrumb markup and an optional owner-supplied Search Console tag. The tag setting is empty until an exact Google token is supplied and an approved deployment makes it live.

Read [the implementation and claim evidence](docs/phase-2a-seo.md), [measurement and growth runbook](docs/measurement-and-growth-plan.md) and [unpublished resources architecture](docs/phase-2b-resources.md). Private analytics figures and KDP exports are kept outside this public repository. No resource article or download is published by the build.

Run these checks from the repository root:

```sh
python3 scripts/build.py
python3 scripts/check_site.py
node scripts/test_tracking.js
python3 scripts/check_design.py
python3 scripts/check_seo.py --baseline-ref origin/main
python3 scripts/test_resource_template.py
```

The read-only PR workflow repeats the checks and measures the homepage/five priority books against the base commit with Lighthouse 13.5.0 on a standard public-repository runner. Mobile reports are local lab measurements, not production Core Web Vitals. Measurement summaries and screenshots are recorded in job logs; no paid runner, storage artifact, deployment, Google write or marketing automation is used.

Before release: owner approves the PR and five book descriptions; resolve Search Console access/verification through the exact project-scoped runbook; review the mobile measurement evidence and Google account settings that remain unknown. Do not merge or deploy without explicit approval. Independently check live Amazon pages in a supported session when available; automated Amazon client rejection alone is not evidence of a broken purchase link.

No changes to the separate Pinterest automation repository are part of this project.

## Phase 2B draft resources

Six original resources and eight limited A4 free printables are developed for owner review in the Phase 2B branch. They are not deployed. Read [the implementation and controlled release instructions](docs/phase-2b-implementation.md). The earlier [Phase 2B architecture](docs/phase-2b-resources.md) records the Phase 2A planning checkpoint, not the current build state. Choose `all` or `priority` in `content/resource-release.json` before an approved release. Source content approval remains pending; no owner-approval flag is fabricated.
