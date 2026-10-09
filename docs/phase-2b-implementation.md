# Phase 2B branch implementation

Draft content for owner review. Do not merge or deploy until the owner approves the actual content, PDFs and release selection. Production remains PR #6 at `02f95ec6650e855664f467ca7b1cf98506c8dd2a`.

Six content records are under `content/resources/`; grid records are separate `*-grid.json` files. Eight limited original free printables live under `assets/resources/`. These are new resources, not book interiors. The original 24-record catalogue is unchanged.

## Build and validate

```sh
python3 scripts/generate_resource_printables.py
python3 scripts/build.py
python3 scripts/check_site.py
python3 scripts/check_seo.py --baseline-ref origin/main
python3 scripts/check_design.py
python3 scripts/check_resources.py
python3 scripts/test_resource_template.py
node scripts/test_tracking.js
```

The legacy unpublished template retains its approval guard. The new branch builder creates reviewable pages without setting `ownerApproved=true`; the required owner approval occurs before merge/deployment, never through a fabricated content flag.

`content/resource-release.json` selects `all` (six articles/eight PDFs) or `priority` (session, nostalgia puzzle, gift guide; three PDFs). Regenerate, build and validate the exact chosen mode before owner release approval. The build removes omitted HTML routes and PDFs and updates hubs, reciprocal book links and sitemap. Source records remain available for a later separately approved release. The environment override `KD_RESOURCE_RELEASE` is for temporary tests; persist the chosen production mode in the JSON file before committing a release.

No preview is deployed. Open the branch locally for actual HTML review. CI screenshot and Lighthouse artifacts are under the PR’s validation run. The supplied owner review PDF contains all six drafts and all eight printable sheets.

## Design and preservation

Shared HTML adds one Resources navigation item, nullable resource analytics configuration, a focusable skip-link target, eager-cover fetch hints and reciprocal resource links on the five matching books. Privacy copy describes the additional events. Original CSS stays byte-identical as the prefix; small appended resource rules and the exact hero-cover aspect ratio extend it. Original covers and 78 previews remain exact. Nostalgia has a separate 440-pixel responsive derivative; no approved master is overwritten.

Structural checks allow only those declared HTML changes, exact catalogue metadata and original asset preservation. PDF allowlisting is limited to these resource outputs; book interiors and ZIPs remain forbidden. Internal crawl checks include PDFs without treating downloads as HTML canonical pages.

## Measurement

`resource_page_view`: resource ID/cluster. `printable_download`: clicked asset ID and resource, not a completed save or print. `related_book_click`: resource/book IDs. These use the existing consent gate; explicit `page_view` remains once per page load, with automatic Google page-view sending disabled. Existing book/Amazon events and destination associations are preserved. No GA account setting or custom dimension was written.

## Evidence and limits

Successful validation run: https://github.com/kyle-zerobaseduk/kd-publishing/actions/runs/37913463432

60 Chromium page/viewport combinations and 24 axe scans passed. Keyboard, consent, PDF-response and event checks passed. Four focused Lighthouse runs measured only homepage and Nostalgia against production. Homepage CLS improved from 0.249 to zero in the single-run local lab comparison; Nostalgia LCP remained approximately 3.15 seconds. This is not production Core Web Vitals evidence. Final printable typography/checklist spacing refinements are validated separately on the latest commit.

Rule claims cite the official 2026/27 FA handbook, updated August 2026, reached through England Football FutureFit. Training plans are original editorial suggestions, not endorsed or claimed field-tested. Puzzle placement and PDF answers are independently checked; no health claims, invented rankings, product prices or search volumes are added. Physical printing and a real coaching trial remain sensible owner review steps. PDFs are vector/text outputs but not fully tagged PDF/UA.

The separate owner report supplies the search-intent inventory, claim/source table, editorial/originality assessment, internal-link/conversion report, release checklist, limits and 30/60/90-day growth roadmap. Coordinate social distribution with existing Grok/Pinterest workflows after approval; no schedule or marketing post is changed here.
