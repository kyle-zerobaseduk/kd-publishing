# K.D.Publishing website

Static publishing catalogue built from `catalogue/books.json`. The 24 September 2026 KDP Bookshelf screenshots were transcribed into 23 listings: 22 live paperbacks and British Nostalgia in review. The live ASINs come from those screenshots, not the former site. The screenshot evidence is kept outside the public repository.

## Build and add a book

1. Verify the title, status, ASIN and category against the current KDP Bookshelf. Add or edit **one record** in `catalogue/books.json`: `id` (unique URL slug), `title`, `subtitle`, `shortTitle` (catalogue card), `category`, `status`, `released`, `asin` and `description`. Available categories are `puzzles`, `colouring`, `guides` and `journals`. A book in review has `status: "in-review"`, `asin: null` and `released: null`; only confirmed live books get an Amazon button. `title` and `subtitle` form the full book title on its page.
2. Identify the latest approved wrap cover and finished interior PDF. Record their exact filenames as `coverSource` and `interiorSource`. Set real 1-based `previewPages`; do not create fictitious page samples. If no approved cover is identified, leave `coverSource: null`, so the site clearly displays a pending cover.
3. With those private PDFs in a directory outside this repository, run `python scripts/generate_assets.py /path/to/private/source/directory`. The script creates only reduced WebP front covers and page previews. **Never commit source PDFs, print-quality images or production masters.**
4. Run `python scripts/build.py`, `python scripts/check_site.py`, and `node scripts/test_tracking.js`. The builder updates catalogue cards, category and book pages, latest releases, metadata, Amazon buttons and the sitemap from the same record. Open the output locally with `python -m http.server` before proposing a deployment. The `scripts/build.py` category labels and hand-picked home hero are optional editorial settings for a new category or featured book; ordinary book updates do not require editing templates.

Static files require no paid hosting or runtime service. The verified production address is `https://kyle-zerobaseduk.github.io/kd-publishing/` (the existing GitHub Pages site). The builder uses it for canonical URLs, absolute Open Graph URLs, the sitemap and `robots.txt`. Set `KD_SITE_URL` only if the production domain actually changes; rebuild and check every generated page before deployment. The separate owner-only ChatGPT Sites preview is not the production domain.

## Analytics

**Current status: unconfigured.** All committed pages have an empty GA4 Measurement ID, so no visitors or events are collected. Create a GA4 property called K.D.Publishing Website and one Web data stream for `https://kyle-zerobaseduk.github.io/kd-publishing/`. Turn Enhanced measurement **off**: this site sends its own page views, preview and Amazon events, so the automatic page-view and outbound-click options are unnecessary. Do not paste a second Google tag or add Google Tag Manager. Copy the stream's `G-...` Measurement ID, then rebuild with `KD_GA4_ID=G-XXXXXXXXXX python scripts/build.py` and commit the generated pages before deployment. Check a consented test visit in GA4 Realtime before treating it as active. Preview testing with the same ID can mix preview traffic into production reports; keep it out of the final reporting period or use a separate test stream if needed.

Once configured, the site shows an opt-in choice and **does not load Google Analytics or store campaign parameters before consent**. The browser stores the choice; the privacy page lets visitors reopen it and clears this site's GA cookies when the choice is reset. When no ID is supplied, no GA requests or analytics cookies are created. People who decline are not measured.

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

## Release checks still required

- Supply the GA4 Measurement ID for the final build. Analytics is currently **inactive**, and the site must be rebuilt with the ID for collection to work. The production URL has been verified and is configured already.
- Confirm a public contact address or contact form endpoint. The contact page currently says details are pending.
- Independently open all 22 Amazon UK pages in a normal supported browser and compare the titles and ASINs. Amazon rejected automated sessions during this rebuild; the links are built from Bookshelf ASINs but product page reachability was not confirmed.
- Check the four journal cover placeholders (Calm, Self-Care, Gratitude and Mindfulness) against the live KDP versions before replacing them. No final approved files were identified for these covers.
- Confirm the High Fantasy Realms cover correction is complete before promoting that source as final. The available `HFR_KDP_COVER_FINAL.pdf` predates the requested removal of a dark lower band.
- Recheck the latest KDP status of British Nostalgia. It was in review and had no ASIN in the supplied screenshot; it has no purchase button.
- Inspect desktop and mobile rendering in a real browser. The local browser binary and cloud-to-local preview were unavailable in this execution environment. Structural/link/asset and simulated browser-script checks passed, but this visual gate is outstanding.

No changes to the separate Pinterest automation repository are part of this project.
