# Phase 2B final editorial refinement and priority release

9 October 2026. Continue PR #7; do not merge or deploy without separate owner authorisation.

## Changes

- Small-squad lead now recognises only five/six children arriving; no full 5v5 needed. Timetable, exact headcounts, safety and all instructions stay exact.
- Nostalgia lead uses familiar everyday details and immediately states free A4 puzzle/separate answers. Decade caveat and original-resource distinction retained.
- Secret Santa lead recognises drawing an unfamiliar colleague and a vague request for something funny. Publisher disclosure and price/availability boundaries remain exact.
- Rotation lead introduces the touchline problem before the existing arithmetic. Arithmetic, tables, rules and caveats remain exact.
- First-session checklist and Christmas openings reviewed and retained because they already give concrete, reader-focused starts.
- CSS-only mobile consent refinement: smaller vertical padding/gap, unchanged text/font size, equal-width neutral buttons. Privacy link, 44px targets, preferences, withdrawal and consent-first script are preserved. Desktop stays unchanged.

## Release selection

`content/resource-release.json` is now `priority`.

| Article path (under /kd-publishing/) | Download path (under /kd-publishing/) |
| --- | --- |
| resources/football/u8-small-squad-training-session/ | assets/resources/u8-small-squad-session-card.pdf |
| resources/puzzles/british-nostalgia-word-search-printable/ | assets/resources/british-nostalgia-puzzle.pdf; assets/resources/british-nostalgia-solution.pdf |
| resources/workplace-humour/secret-santa-gifts-work-colleagues-uk/ | None |

Four non-empty hubs: `resources/`, `resources/football/`, `resources/puzzles/`, `resources/workplace-humour/`. Exactly 42 canonical HTML pages and sitemap URLs including the 35 existing pages. No links or sitemap entries for the withheld articles. Only three PDFs in the release output.

The other three JSON article records, original grid data and deterministic printable generator remain in the draft project at their stable future URLs. Their generated HTML and five PDFs are deliberately removed from the priority output; they were not discarded as editorial work. All eight unchanged sheets are included in the owner pack and available from PR history at e48b4d7. Regenerate all eight before selecting a subsequent release:

```
python scripts/generate_resource_printables.py
KD_RESOURCE_RELEASE=all python scripts/build.py
KD_RESOURCE_RELEASE=all python scripts/check_resources.py
```

Then rebuild with the approved persisted mode. Current mechanism supports `priority` or `all`, not arbitrary incremental selections. A Christmas-only second release needs a small separately reviewed selection extension; do not switch to `all` assuming that publishes Christmas alone.

## Printable and physical review

All eight current PDF bytes and both grid JSON files remain unchanged. Eight final renders visually reviewed: A4 portrait, body margins approximately 15.5mm, black type/white background, 20pt grids, 18pt word lists and 12pt answer coordinates. No clipping or alignment defect. Checklist boxes and notes lines have space; rotation writing rows are approximately 11mm high. Attribution/source-page URLs accurate; lower footer baseline is 6.35mm from paper edge and needs a printer-specific check. Not fully tagged PDF/UA. No physical print test performed.

Owner checklist:

- Print each sheet single-sided on A4 portrait, actual size/100%, black-and-white, with browser headers off; confirm settings before using Fit (which reduces type).
- Check all edges, attribution and full footer URLs survive the printer margins, especially the bottom edge.
- Read the session card at normal coaching distance and check the full 0-60 minute sequence; try the checklist boxes and notes with a pen.
- Read both grids and word lists at a comfortable distance. Find a few words independently and compare answer coordinates/highlights; check grey paths remain distinct from black letters.
- Write five player initials, resting initials, goalkeeper and actual time into a rotation row; try player-name/minutes lines. Check worked examples are readable.
- Record printer model, settings, sheet issues and the owner's pass/fail. Report any failed sheet for a targeted correction before its publication.

## Validation and approvals

Local priority build, site/design/SEO preservation, exact release scope, all 24 tracking funnels and selected PDF/puzzle checks passed. All-six/eight-sheet technical checks also passed before output pruning. GitHub browser evidence on this refinement must pass before final owner review; latest run/metrics will be recorded in the updated review report and PR.

Before release: approve final three article texts/disclosure/licence wording, mobile consent appearance and exact priority scope; complete physical proofs for the three launch sheets; then provide separate explicit merge/deploy authorisation. No approval is fabricated in article records.

Recommended later order: Christmas in October/November after physical proof and a separately reviewed selection change; then first-session checklist; then rotation guide with local-rule/worksheet review. Do not publish the withheld three just to increase page count. Keep existing Grok/Pinterest schedules intact.
