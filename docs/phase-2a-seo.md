# Phase 2A implementation and factual-copy evidence

Prepared 9 October 2026 against the approved PR #5 deployment, commit `b0eca3e3f85d57dc41edd35811b84731e557ffd9`. The authoritative starting audit is `KD_Publishing_Phase_2_SEO_Growth_Audit_2026-10-09.md`. This branch is reviewable implementation, not a new design. No merge, deployment, article publication, advert installation, KDP change or Google account write is authorised by this document.

## Before and after

| Priority | Verified baseline / gap | Branch result / remaining limitation |
| --- | --- | --- |
| Critical | No verified critical crawl/indexability failures in the audit | No arbitrary URL, redirect, robots or canonical changes |
| High | Search Console ownership/indexing and search metrics unavailable | Exact URL-prefix runbook and optional static homepage verification tag; empty until owner supplies Google's exact token. Property verification and sitemap submission remain owner actions |
| High | Production property mapping needed confirmation | Read-only rows match property 555796140, stream 15838666263 and Measurement ID G-64LMW6KFB7. Tracking implementation preserved; account settings/custom definitions still require review |
| High | Little original non-branded content discovery | Three-cluster architecture, reusable unpublished template and 12-page prioritised backlog prepared. No resource routes or articles added |
| Medium | 22 of 24 product SEO titles exceeded 60 characters; very long subtitles crowded the search title | All product SEO titles now 42–60 characters including the brand; exact lengths in table below. Full visible titles/subtitles unchanged. The 60/65-character review guard is not a Google limit |
| Medium | Brief descriptions on guide/planner/Christmas; incomplete explanation of product fit | Five product-page descriptions expanded from verified materials; three receive contents bullets, with reciprocal contextual links between guide and companion |
| Medium | Minimal Book objects and no breadcrumb markup | 24 fuller Book objects and 24 BreadcrumbList objects reflecting the existing visible trail. No ratings, prices, stock promises, ISBNs, page counts, qualifications or unsupported publication dates |
| Medium | No mobile lab/field measurement in audit; PSI quota unavailable | Local Lighthouse attempted, but Chrome startup blocked by host socket permissions. PR workflow provides the next lab route; actual results must be read before claiming measured performance. No field CWV pass/fail asserted |
| Low | Image alt text and dimensions already accurate at catalogue level; 78 genuine previews | Images and all 226 image placements preserved. No keyword-stuffed alt rewrite or derivative asset churn |
| Low | 35 self-canonicals, working sitemap and all pages linked | Same 35 canonicals/sitemap entries/URLs; graph reachability and fragment checks added. Project robots file preserved; no shared host-root change |

Generated changes are justified: every changed public HTML file is one of the 24 book pages, with concise metadata and non-visible structured data; only the five priority product bodies change. Eleven non-book pages, CSS, JS, sitemap, robots and all assets remain byte-identical to the approved baseline with an empty verification token. No new public resource URL is generated.

## Source of product claims

Catalogue titles, ASINs, Amazon destinations, formats and preview references are existing approved records. New contents claims were checked against the exact catalogue-named interiors and visible samples. Private interiors/manuscripts are not committed. The owner should confirm during PR review that these source editions still match the current KDP interiors; no live Amazon edition/price change is proposed.

| Book | Checked material | Supported claims | Not added / owner review |
| --- | --- | --- | --- |
| Football guide | `The_First-Time_U7_U8_Football_Coach_8x10_KDP_Interior_CLEAN.pdf`, PDF pages 3–4, 16, 56; genuine site samples 16/56/101/201 | Parents/volunteers in England; preparation, coaching, match day, parents; 12 sessions; 20-tool toolkit; separate age formats | No qualification, FA endorsement or promise of player development. Confirm source edition matches current paperback |
| Season planner | `The_First-Time_U7_U8_Football_Coach_Season_Planner_8x10_KDP_Interior.pdf`, pages 1–8, 21–26, 141–150 | Separate companion; 24 fresh 60-minute sessions; six blocks; four-part weekly pages; rescue/number/format examples | No club-system or official rulebook replacement; no guarantees of equal minutes or season outcomes |
| British Nostalgia | `British_Nostalgia_Large_Print_Word_Search_KDP_Interior_FINAL.pdf`, pages 1–9 and existing answer preview | 100 puzzles, adult/senior audience, themes and prompts; existing 15×15/16-word/16-point-or-larger details retained | No memory-treatment, dementia-prevention or cognitive benefit claim |
| Honest Version | Existing approved catalogue/excerpts plus `I_Deleted_the_Honest_Version_Final_Developed_Manuscript.docx`, opening/Meetings/Email sections | Dry workplace humour; short pieces; emails, meetings and professional replies; dip-in reading | Manuscript is corroboration of themes, not proof of final pagination. Compact paperback comes from existing catalogue. No clean-language, HR-approved or independently reviewed claim |
| Cozy Christmas | `Cozy_Christmas_WordSearch_INTERIOR_LARGE_PRINT_FINAL.pdf`, pages 1–4 and existing puzzle/answer samples | 100 puzzles; adults/teens; easy→hard; 15 words per 15×15 grid; solutions | No invented paper quality, trim, health benefit or Amazon price. No unverified font-size promise |

The founder's U8 experience is reserved for future approved resources. No first-person coaching anecdote is published by this change.

## Priority copy and keyword intent

Keyword choices are qualitative relevance hypotheses informed by the observed result formats described in the resources plan. No monthly search volumes, difficulty scores or guaranteed rankings are available. Product pages target a relevant book purchase/consideration; free-session/printable intent belongs in future resources.

| Book | Primary product intent | Secondary phrases / distinction |
| --- | --- | --- |
| Football guide | First-time U7/U8 football coaching book | Parent volunteer coach guide; first season; ready-to-run sessions. Generic U8 drills have strong free-resource competition |
| Season planner | U7/U8 football season planner | Training session companion; 24 guided weeks; distinguish organiser from foundational guide |
| British Nostalgia | British nostalgia large-print word search book | Adults/seniors; British memory themes; preview legibility and included answers |
| Honest Version | Workplace/office humour book for a colleague | Email humour; colleague gift; Secret Santa relevance without inventing price suitability |
| Cozy Christmas | Christmas word-search book for adults/teens | 100 festive puzzles; easy-to-hard and answers; October/November promotion is a seasonal planning judgement, not measured demand |

### The First-Time U7 & U8 Football Coach

Before title (166): The First-Time U7 & U8 Football Coach: A Practical Grassroots Guide to Fun Training Sessions, 3v3 & 5v5, Match Days and Keeping Young Players Engaged | K.D.Publishing

After title (50): First-Time U7 & U8 Football Coach | K.D.Publishing

Before meta (143): A practical guide for parents and volunteers coaching U7 and U8 grassroots football in England. See actual interior pages and book information.

After meta (161): New to U7 or U8 football coaching? Explore a practical guide for parents and volunteers, with 12 ready-to-run sessions, a first-season toolkit and real previews.

Before product description: A practical guide for parents and volunteers coaching U7 and U8 grassroots football in England.

After product description: For parents and volunteers taking on U7 or U8 grassroots football in England. This practical guide covers preparing your first session, keeping young players involved, match days and communicating with parents, alongside 12 ready-to-run sessions and a 20-tool First Season Toolkit.

Contents bullets:

- Practical chapters on preparation, coaching young children, safety, match days and parent communication.
- 12 ready-to-run sessions covering ball confidence, dribbling, passing, shooting and small-sided games.
- A 20-tool First Season Toolkit, plus separate guidance for U7 3v3 and U8 5v5. Current official and local requirements take priority.

Contextual link: For 24 additional guided weeks and working pages to organise your season, explore the companion: U7 & U8 Season Planner.

### U7 & U8 Season Planner

Before title (216): The First-Time U7 & U8 Football Coach: Season Planner & Session Companion: 24 Guided Weeks of Fresh Training Sessions, Match-Day Plans, Player Notes and Simple Organisation for New Grassroots Coaches | K.D.Publishing

After title (56): U7 & U8 Season Planner: 24 Guided Weeks | K.D.Publishing

Before meta (150): A guided season companion with weekly training sessions, match-day plans and space for coaching notes. See actual interior pages and book information.

After meta (159): Plan U7 and U8 coaching with 24 guided weeks, complete training sessions, pitch-side cards and match-day reflections. See real pages from the season companion.

Before product description: A guided season companion with weekly training sessions, match-day plans and space for coaching notes.

After product description: A separate season companion for parents and volunteers coaching U7 or U8 football in England. Follow 24 guided weeks across six development blocks, with complete training sessions, pitch-side cards and space to record match-day observations. Use the weekly route or choose a session to suit your group.

Contents bullets:

- 24 fresh 60-minute sessions arranged in six four-week development blocks.
- Each week includes a brief, a complete session, a pitch-side card and diagram, and a match link with reflection.
- Quick-use support includes arrival activities, number fixes, rescue options and separate U7 carousel and U8 rotation examples.

Contextual link: This companion adds a weekly planning route. For the foundations of preparing, coaching and managing match day, explore: The First-Time U7 & U8 Football Coach.

### British Nostalgia Word Search

Before title (170): British Nostalgia Word Search: For Adults & Seniors: 100 Large-Print Puzzles Celebrating Childhood, School Days, Seaside Holidays & Everyday British Life | K.D.Publishing

After title (58): British Nostalgia Large-Print Word Search | K.D.Publishing

Before meta (190): 100 large-print British nostalgia word searches for adults and seniors, with familiar memories of childhood, school days and seaside holidays. See actual interior pages and book information.

After meta (159): Explore 100 large-print British nostalgia word searches for adults and seniors, with memory prompts and solutions. See genuine pages before visiting Amazon UK.

Before product description: 100 large-print British nostalgia word searches for adults and seniors, with familiar memories of childhood, school days and seaside holidays.

After product description: Revisit childhood games, school dinners, high-street shops and seaside holidays through 100 large-print word searches for adults and seniors. Each puzzle includes a short “Remember when...” prompt to enjoy on your own or share in conversation. Browse the genuine samples to check the layout, word lists and solutions before choosing a copy.

Contents bullets:

- One puzzle per page, with 15 × 15 grids and 16 hidden words or phrases.
- “Remember when...” prompts inspired by home, family, food, shopping and everyday British life.
- Large-print puzzles and solutions, with word lists and prompts in 16-point type or larger.
- Solutions included.

### I Deleted the Honest Version

Before title (111): I Deleted the Honest Version: Workplace Humour for Colleagues Who Choose Their Words Carefully | K.D.Publishing

After title (60): I Deleted the Honest Version: Office Humour | K.D.Publishing

Before meta (209): Dry workplace humour about the things you would like to say and the professional replies you actually send. A compact gift for a colleague who knows the feeling. See actual interior pages and book information.

After meta (155): Dry workplace humour about meetings, emails and the replies you rewrite. Explore real excerpts from I Deleted the Honest Version, a compact colleague gift.

Before product description: Dry workplace humour about the things you would like to say and the professional replies you actually send. A compact gift for a colleague who knows the feeling.

After product description: For anyone who has rewritten an email before pressing send. I Deleted the Honest Version finds dry humour in meetings, messages, quick questions and the gap between your first reaction and your professional reply. Short pieces let you dip in anywhere; read the genuine excerpts to see whether the humour suits your colleague.

Contents bullets:

- Short pieces about meetings, emails, quick questions, coworkers and managers.
- Dip in anywhere, pass it around or read a piece aloud to someone who recognises the situation.

### Cozy Christmas Word Search

Before title (116): Cozy Christmas Word Search Puzzle Book: 100 Festive Puzzles with Full Answer Key for Adults & Teens | K.D.Publishing

After title (56): Cozy Christmas Word Search: 100 Puzzles | K.D.Publishing

Before meta (121): Festive word searches for cosy Christmas puzzle time, with an answer key. See actual interior pages and book information.

After meta (153): Enjoy 100 festive word searches for adults and teens, arranged from easy to hard with a full answer key. See real Christmas puzzle pages before you shop.

Before product description: Festive word searches for cosy Christmas puzzle time, with an answer key.

After product description: Settle into a screen-free Christmas activity with 100 festive word searches for adults and teens. The puzzles progress from easy to hard, with 15 words in each 15 × 15 grid and complete solutions at the back. Browse actual puzzle and answer pages to see the style before choosing it for yourself or as a seasonal gift.

Contents bullets:

- 100 Christmas-themed puzzles arranged in easy, medium and hard sections.
- 15 festive words in each 15 × 15 grid; later sections add more word directions.
- A full answer key at the back, with genuine puzzle and solution previews on this page.

## All product SEO title lengths

| Page | Before | After | Proposed SEO title, including brand |
| --- | ---: | ---: | --- |
| i-deleted-the-honest-version | 111 | 60 | I Deleted the Honest Version: Office Humour \| K.D.Publishing |
| high-fantasy-realms | 101 | 58 | High Fantasy Realms: Adult Colouring Book \| K.D.Publishing |
| british-nostalgia | 170 | 58 | British Nostalgia Large-Print Word Search \| K.D.Publishing |
| space-and-stars | 138 | 42 | Space & Stars Word Search \| K.D.Publishing |
| nature-and-wildlife | 154 | 46 | Nature & Wildlife Word Search \| K.D.Publishing |
| season-planner | 216 | 56 | U7 & U8 Season Planner: 24 Guided Weeks \| K.D.Publishing |
| first-time-football-coach | 166 | 50 | First-Time U7 & U8 Football Coach \| K.D.Publishing |
| 80-day-sleep | 56 | 54 | The 80-Day Sleep: Daily Sleep Journal \| K.D.Publishing |
| ocean-and-beach | 132 | 42 | Ocean & Beach Word Search \| K.D.Publishing |
| classic-movies-and-music | 155 | 51 | Classic Movies & Music Word Search \| K.D.Publishing |
| world-war-2 | 103 | 52 | World War 2 Large-Print Word Search \| K.D.Publishing |
| calm-and-mindfulness-word-search | 158 | 59 | Calm & Mindfulness Large-Print Word Search \| K.D.Publishing |
| halloween-word-search | 122 | 50 | Halloween Large-Print Word Search \| K.D.Publishing |
| cozy-christmas-word-search | 116 | 56 | Cozy Christmas Word Search: 100 Puzzles \| K.D.Publishing |
| classic-motorcycles | 81 | 48 | Classic Motorcycles Word Search \| K.D.Publishing |
| 80-day-calm | 63 | 54 | The 80-Day Calm: Guided Daily Journal \| K.D.Publishing |
| 80-day-self-care | 64 | 52 | The 80-Day Self-Care: Daily Journal \| K.D.Publishing |
| 80-day-gratitude | 37 | 53 | The 80-Day Gratitude: Guided Journal \| K.D.Publishing |
| 80-day-confidence | 99 | 54 | The 80-Day Confidence: Guided Journal \| K.D.Publishing |
| 80-day-mindfulness | 135 | 55 | The 80-Day Mindfulness: Guided Journal \| K.D.Publishing |
| comfort-food-and-baking | 154 | 50 | Comfort Food & Baking Word Search \| K.D.Publishing |
| garden-and-flowers | 148 | 45 | Garden & Flowers Word Search \| K.D.Publishing |
| travel-and-world-cities | 150 | 50 | Travel & World Cities Word Search \| K.D.Publishing |
| gratitude-and-positivity-word-search | 126 | 51 | Gratitude & Positivity Word Search \| K.D.Publishing |

## Quality and remaining checks

Build, full catalogue/link/asset checks, tracking/consent simulation, semantic/design checks, independent structured-data/canonical/reachability/preservation checks and unpublished-template checks pass locally. The preservation comparison uses the actual approved base commit, not a regenerated approximation. Tracking tests cover all 24 books, exact outbound URLs, accepted/rejected/reset consent, one manual page view, campaign/referrer data, preview interactions and analytics failure without interrupting the destination.

The PR workflow has read-only repository permissions, no deployment step and a standard public-repository runner. Its Lighthouse measurements use one default mobile simulated-throttling run per page on local static files for the homepage and five priority books, before/after. Analytics consent is not accepted. This is a lab comparison without production network latency, real visitor devices or field INP/CWV. Inspect the actual logs and report results, not the mere existence of a workflow. Full rendered responsive review remains an additional check; source CSS/DOM preservation does not by itself prove complete WCAG conformance.

Book/BreadcrumbList JSON syntax, expected schema properties and agreement with visible content/canonicals are validated locally. A Google Rich Results Test and live Search Console inspection remain post-approved-deployment checks. Ordinary Book markup does not enrol this small publisher in Google's book-action provider programme or guarantee a book-specific rich result. Breadcrumbs can improve machine understanding; Google decides whether/how to display them.

Sources: [Google titles](https://developers.google.com/search/docs/appearance/title-link), [snippets](https://developers.google.com/search/docs/appearance/snippet), [breadcrumb guidance](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb), [Schema.org Book](https://schema.org/Book), [Google Book actions](https://developers.google.com/search/docs/appearance/structured-data/book), [Lighthouse scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring).

Next stage: owner reviews the implementation PR and exact Search Console/GA4 account actions. After approved deployment and a real search baseline, Phase 2B produces a small number of approved original resources. Passing technical tests is not evidence of traffic or sales growth.
