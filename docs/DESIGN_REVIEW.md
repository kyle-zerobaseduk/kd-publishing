# Editorial design review

This draft refines the existing static website. It is not deployed. Review the rendered site before approving a merge.

## Direction and implementation

The previous design used heavy card borders, gradients and rotated covers. Card actions inherited flex-column stretching, product subtitles appeared at headline size, mobile descriptions disappeared at narrow widths, and category menus could open through CSS while their accessible state remained closed.

The refinement uses warm paper, deep ink, restrained teal and brass, system sans-serif text and Georgia editorial headings. No remote fonts or new production dependencies are required.

- A compact introduction and genuine featured cover lead the homepage; fine rules and real catalogue counts organise category discovery.
- Uncropped cover shelves replace boxed cards. Single-book collections receive a larger presentation; two-book and related-book collections have deliberate layouts.
- Card actions, ordinary text links and buttons have separate styles. `width: fit-content`, `max-width: 100%` and explicit flex alignment prevent stretched actions. Desktop purchase buttons fit their labels; the primary purchase button fills the available width only below 600px. Long labels can wrap.
- Product titles and existing subtitles are separately typeset. Buying and preview actions appear together before the facts, with one unchanged tracked Amazon destination per book.
- Preview frames, contact, privacy, navigation and footer share the spacing and typography system. Narrow-screen descriptions remain available.
- Category menus use the existing button-controlled state, with an explicit `aria-controls` relationship. Card headings follow their surrounding heading level. Facts use valid definition-list groups.
- Image width/height attributes now match the actual WebP dimensions. Images themselves are unchanged. Cover stages and preview frames use containment, not cropping.
- Optional analytics consent is presented after the header in normal page flow. It cannot cover a book or action. Consent storage, opt-in, rejection and withdrawal logic are unchanged.

## Completed checks

Run these from the repository root:

```sh
python3 scripts/build.py
python3 scripts/check_site.py
python3 scripts/check_design.py
node scripts/test_tracking.js
```

The implementation environment passed the build, all 35-page link/metadata checks, all 24 book/ASIN/purchase-link checks and all 78 preview checks. Tracking tests now exercise every generated book configuration, alongside opt-in, rejection, withdrawal, campaign attribution and analytics failure handling.

Structural checks passed for heading order, control names and ID references, semantic facts and 226 generated image references with accurate dimensions. The tested text colour pairs exceed 4.5:1 (lowest 5.14:1). These are structural and token checks, not a complete WCAG audit.

Against the starting main snapshot, the catalogue JSON, `site.js`, all 102 approved images, all 35 complete HTML metadata heads, sitemap and robots file are byte-identical. No image-generation or print-asset process was run.

The baseline was main commit `4f7c268ab8fb2227145d3bec3a4501eed1dcc562`.

## Browser limitation

Chromium could not launch: the execution sandbox rejected `setsockopt` and the process exited with SIGTRAP. The connected browser was also unavailable. No page was rendered for this redesign, no before/after screenshots were captured, and no viewport, visual, focus or browser interaction check is reported as passing.

CSS has safeguards for 320px through large desktop widths, including zero-minimum grid tracks, contained images, wrapping controls and breakpoints at 360, 600, 800 and 1100px. Their actual appearance needs browser verification. External Amazon availability and GA4 ingestion were not reverified; their destinations and implementation were preserved.

**Recommendation: FURTHER REFINEMENT REQUIRED until rendered visual and keyboard review is completed.**

## Local visual review without publishing

Check out this PR branch and serve its existing generated files:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. In browser responsive mode inspect 320, 360, 390, 768, 1024 and 1440px. Review the homepage, catalogue, all five categories, latest releases, About, Contact, Privacy and all 24 book pages. Pay particular attention to long titles, the two coaching subtitles, journal covers and the humour cover's different proportions.

Confirm no horizontal overflow, uncropped images, proportional card actions, natural title wrapping and usable consent controls. Use Tab/Shift+Tab and Enter/Space for navigation and previews; Escape should close a preview and restore focus. Verify the contact email and the privacy reset control. Test zoom to 200% and reduced motion. Inspect actual colour contrast and focus visibility, including over every background. Test iOS Safari and Android Chrome where available. Do not complete a purchase for this review.

## Optional repeatable screenshots and browser checks

`scripts/review_visual.js` checks every generated page at all six widths and captures 15 representative pages at each width. It also checks image loading, control boundaries/target height, card action width, navigation state, preview opening/closing, consent rejection and absence of pre-consent analytics requests. It blocks Google analytics network requests and never clicks Amazon links. Human review of the captures remains essential.

Use a local Playwright installation and Chromium. If neither is installed, an optional one-time development setup outside this repository is:

```sh
npm install --prefix /tmp/kd-browser-tools playwright
/tmp/kd-browser-tools/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/kd-browser-tools/node_modules node scripts/review_visual.js --output /tmp/kd-review
```

This introduces no website runtime dependency or subscription. An installed Chromium can be selected with `--browser /path/to/chromium`.

For matched before/after captures, create a separate baseline checkout and pass it to the script:

```sh
git worktree add --detach ../kd-publishing-before 4f7c268ab8fb2227145d3bec3a4501eed1dcc562
NODE_PATH=/tmp/kd-browser-tools/node_modules node scripts/review_visual.js --baseline ../kd-publishing-before --output /tmp/kd-review
python3 scripts/check_design.py --baseline ../kd-publishing-before
```

Keep screenshot output outside the website directory. A successful browser run writes `results.json` and PNGs to the chosen directory; failure exits non-zero. The browser script passed syntax checking here but its rendering checks could not run because of the launch restriction.
