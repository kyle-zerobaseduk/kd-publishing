# K.D.Publishing website

Static publishing catalogue built from `catalogue/books.json`. The 24 September 2026 KDP Bookshelf screenshots were transcribed into 23 listings: 22 live paperbacks and British Nostalgia in review. The live ASINs come from those screenshots, not the former site. The screenshot evidence is kept outside the public repository.

## Build and add a book

1. Verify the exact title, publication status and ASIN against the current KDP Bookshelf. Add one record to `catalogue/books.json` with a unique slug. Mark a book `in-review` and leave `asin` null if it has no published identifier.
2. Identify the approved wrap cover and finished interior PDF. Record their filenames as `coverSource` and `interiorSource`. Set real 1-based `previewPages`; do not create fictitious page samples.
3. With those private PDFs in a directory outside this repository, run `python scripts/generate_assets.py /path/to/private/source/directory`. The script creates only reduced WebP front covers and page previews. **Never commit source PDFs, print-quality images or production masters.**
4. Add a short catalogue card name in `SHORT` in `scripts/build.py`. Run `python scripts/build.py`, `python scripts/check_site.py`, and `node scripts/test_tracking.js`. Open the output locally with `python -m http.server` before proposing a deployment.

Static files require no paid hosting or runtime service. For a deployment at a known public base URL, set `KD_SITE_URL=https://your-domain.example` during the build. This emits canonical URLs, absolute Open Graph URLs and a sitemap. Without a confirmed public URL, those are deliberately omitted; `robots.txt` remains valid. Do not publish a guessed canonical domain.

## Analytics

Set `KD_GA4_ID=G-XXXXXXXXXX` at build time to add a real Google Analytics 4 measurement ID to all pages. The site shows an opt-in choice and **does not load Google Analytics or store campaign parameters before consent**. Consent persists in the browser. The privacy page lets visitors reopen the choice. When no ID is supplied, no GA requests or analytics cookies are created.

Events (only after consent):

| Event | Meaning | Parameters |
| --- | --- | --- |
| `page_view` | A page loaded | GA4 page title/location; acquisition handled by GA4 |
| `book_page_view` | A product page loaded | `book_id`, `book_title`, `category`, `asin` |
| `preview_open` | A sample enlarged | same book fields plus `page_number` |
| `amazon_click` | The Amazon UK button clicked | same book fields plus `destination` |

Available `utm_source`, `utm_medium`, `utm_campaign`, and `utm_content` are carried in the visitor's session **after consent**. Use tagged links such as `?utm_source=pinterest&utm_medium=social&utm_campaign=high_fantasy_launch`. In GA4, compare `amazon_click` event count with `book_page_view` event count for the same `book_id`. This is website-to-Amazon click-through rate, **not sales attribution**. Configure GA4 custom dimensions for book fields and relevant UTM fields if you need them in standard reports. GA4 acquisition reports also provide source/medium data. Users who decline analytics are not measured.

## Release checks still required

- Supply the actual public site URL and GA4 measurement ID for the final build, if analytics is wanted.
- Confirm a public contact address or contact form endpoint. The contact page currently says details are pending.
- Independently open all 22 Amazon UK pages in a normal supported browser and compare the titles and ASINs. Amazon rejected automated sessions during this rebuild; the links are built from Bookshelf ASINs but product page reachability was not confirmed.
- Check the four journal cover placeholders (Calm, Self-Care, Gratitude and Mindfulness) against the live KDP versions before replacing them. No final approved files were identified for these covers.
- Confirm the High Fantasy Realms cover correction is complete before promoting that source as final. The available `HFR_KDP_COVER_FINAL.pdf` predates the requested removal of a dark lower band.
- Recheck the latest KDP status of British Nostalgia. It was in review and had no ASIN in the supplied screenshot; it has no purchase button.
- Inspect desktop and mobile rendering in a real browser. The local browser binary and cloud-to-local preview were unavailable in this execution environment. Structural/link/asset and simulated browser-script checks passed, but this visual gate is outstanding.

No changes to the separate Pinterest automation repository are part of this project.
