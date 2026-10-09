# Measurement and commercial growth plan

Prepared 9 October 2026. Account actions below are **proposals requiring owner approval**, not changes already made. Keep private traffic reports and KDP sales exports outside this public repository.

## Verified production measurement

The deployed HTML and builder use `G-64LMW6KFB7`. Authorised read-only GA4 reports map that Measurement ID to stream `15838666263`, named **K.D.Publishing production**, in property **555796140**. Production-host report rows were returned for 9 September–8 October 2026. Property **555781181** returned no rows for the same production-host query. That establishes the observed production mapping; it does not justify deleting the other property or assume its intended purpose.

Use hostname exactly `kyle-zerobaseduk.github.io` AND page path matching `^/kd-publishing(/|$)` in GA4 reporting, with stream 15838666263 where available. This avoids mixing another GitHub Pages project on the shared host. GA4 may report paths without a trailing slash; include both forms. The current connector's report filter supports `contains`, not this regex, so inspect the returned paths and report scope before comparing totals. Preview-host rows are known to exist; separate them in reporting. Use local test builds with `KD_GA4_ID=''`, then restore/rebuild production output before committing. Do not activate an irreversible account exclusion filter on unverified IPs or erase historical data.

Source-level checks show one manual `page_view` per accepted page load, `send_page_view:false`, book events and consent gating. GA4 is never loaded before consent, and rejection preserves book navigation/previews/purchasing. Consent withdrawal clears the choice, campaign storage and this site's analytics cookies, then reloads. The tracking script remains unchanged in Phase 2A. Visitors declining analytics are absent from these reports; these data are not a census. Search Console and GA4 are different measurements and should not be expected to match.

## Account checks and exact proposed changes

| Item | Current status | Smallest next action; approval required for a change |
| --- | --- | --- |
| Production stream | ID/property mapping verified in report rows | Owner opens this stream's Admin details and confirms its configured website URL is the production URL, not a preview |
| Enhanced measurement / extra tags | Admin settings unavailable; no second site tag found in source | Read current Page views/history/outbound settings; test one consented visit. Correct an actual duplicate source only if observed and approved. Do not add another tag or switch off all enhanced features blindly |
| Book custom dimensions | Parameters verified in source/tests; registration status unavailable | Read Custom definitions. If missing, propose event-scoped `book_id`, `category`, `asin`; `book_title` optional. Retain stable ID as the join key. Do not register page URL/referrer again or create unique user/session dimensions |
| Amazon interest key event | Audit reports returned zero key-event counts; designation unavailable | After owner approval, mark existing `amazon_click` as a key event. Label reports “Amazon outbound interest”. Keep event name, destination and consent unchanged; never send `purchase` or invented revenue |
| Internal/test traffic | Preview hostname observed; owner visits not positively identified | Use report comparisons first. If a persistent internal-traffic rule is desired, document exactly which verified traffic it excludes and approve before enabling; do not guess an IP |
| Recurring dashboard | Specification prepared; no scheduled export or account report created | Review the table below, then approve a weekly read-only report/export destination separately. No new automation or external sharing is activated here |

Google custom parameters need registered definitions for normal custom-dimension reporting, and new definitions can take 24–48 hours to become reportable. Do not promise historical backfill. The authorised connector exposes page/event reports but did not expose the book-specific custom parameters in its discovered field list; this does not prove definitions are absent. Until checked, join the event's product `page_path` to `catalogue/books.json` to identify the relevant book/ASIN. Paths identify where the event occurred, not a separately verified custom-parameter value.

## Proposed weekly dashboard

Owner reviews every Monday: last completed seven days, previous seven days, plus a rolling 28-day view. Use complete dates in the property timezone after checking what that timezone is. Allow for reporting delay and record missing data as **unavailable**, not zero. At this scale counts matter more than percent changes. Keep test visits in an annotation log. Source/landing rows in the small audit sample did not add cleanly to aggregate sessions: use separately queried totals, investigate scope/attribution in the GA4 UI, and do not silently sum them.

| Block | Source and reporting scope | What to show |
| --- | --- | --- |
| Search visibility | Search Console exact URL-prefix; Web search; consistent date/country filters | Sitemap last-read/result, relevant indexed URLs and exclusions, impressions, clicks, CTR, average position; branded/non-branded query and page tables |
| Organic Google visitors | GA4 production report scope; session source `google`, medium `organic` | Users, sessions, engaged sessions; counts alongside total production traffic. Keep Pinterest organic/social separate from Google search |
| Landing pages | GA4 Landing page, same production/session scope | Top entry pages by sessions and engaged sessions; compare resource versus product entries. Separate blank/not-set rows and investigate |
| Book engagement | `book_page_view` and `preview_open`; ID if available, otherwise product path | Event counts and users, ranked by book; source/medium breakdown where compatible. Repeated events are not unique people |
| Amazon interest | Existing `amazon_click`; exact source purchase destination | Event count, event users, interested books and source contribution; eventual key-event count after approved designation |
| Resource usefulness | Phase 2B consented page engagement plus proposed `resource_download` event | Relevant engaged visits, approved PDF downloads and onward book-page visits. A download alone is not proof of reading or satisfaction |
| Actual sales | Independently provided KDP report for the same dates, book and marketplace | Units and royalties, marked provisional/final as the report indicates; no causal join to GA4 visitors without genuine independent attribution |

The future `resource_download` event is a proposal, not implemented here. Send only resource ID and derivative filename after consent; do not collect children's names or coach-entered squad data. Whether automatic file-download measurement is already available must be checked first to prevent duplicate counts. For the resource → book journey, use a sequential GA4 funnel or a separately reviewed referral parameter/event; do not use internal UTMs that overwrite acquisition.

Book outbound-interest ratio = `amazon_click` event count / `book_page_view` event count, for the same book, period and scope. It is a descriptive event ratio, not a sales conversion rate, and can exceed 100% if users click repeatedly. A sequential user/session funnel is better once volume allows. Do not interpret three clicks as statistically useful conversion evidence. No sale, royalty or AdSense income can be inferred from GA4.

## Search Console owner runbook

No authorised Search Console account/property data were available. Verification/ownership, sitemap submission, discovered/indexed counts, exclusions, Google-selected canonicals, crawl/mobile issues, impressions/clicks/queries/CTR/position all remain **unverified**. This is not evidence that the site is unindexed.

1. In the owner's normal Google account, open Search Console and look for the exact existing URL-prefix property `https://kyle-zerobaseduk.github.io/kd-publishing/`. If it exists, inspect Settings → Ownership verification; export the reports below or grant an explicitly approved read-only access path. Do not create a duplicate property unnecessarily.
2. If absent, the proposed change is to add that exact URL-prefix property in the owner's account. Do not verify the shared `github.io` domain or change `https://kyle-zerobaseduk.github.io/` root files. The trailing slash scopes measurement to this project.
3. Choose HTML tag verification. Supply **only** Google's exact `content` value, not credentials or an invented placeholder. `catalogue/search-console.json` now accepts that value as `verificationToken`; it is empty by default and produces no tag. The builder emits a static tag in the homepage head. Adding a real token needs a reviewed repository change and approved deployment. It does not load Google code, bypass consent or change GA4. Google-side Verify/add-property actions require owner approval and ownership.
4. After the approved tag is deployed and visible in the live homepage head, the owner clicks Verify. Keep the token permanently unless deliberately changing ownership. No verification claim is valid before Google confirms it. A Google-supplied verification HTML file at the project URL could also work if Google explicitly specifies that location, but a static tag is the smaller scope-safe change. Do not move files to the shared host root.
5. After approval, submit `https://kyle-zerobaseduk.github.io/kd-publishing/sitemap.xml` in this property's Sitemaps report. Read its status, last-read date and discovered URLs; the current sitemap contains 35 canonical URLs. Submission is a discovery hint, not a guarantee of indexing.
6. Inspect the homepage, the five priority books, one category and later each new resource. Record indexed status, last crawl, fetch/robots result, user canonical, Google-selected canonical and mobile crawling result. Use Live Test to diagnose access, not as proof that a page is indexed. Request indexing of priority updated pages only when appropriate; avoid bulk repeated requests.
7. Export Page indexing and Search performance (Web, last completed 28 days, pages and queries). Add mobile device and UK comparisons without treating non-UK traffic as worthless. Save a dated baseline and refresh weekly. Use URL Inspection for page-level selected canonicals; GA4 cannot supply this.

Sources: [Google URL-prefix properties](https://support.google.com/webmasters/answer/34592?hl=en), [ownership verification](https://support.google.com/webmasters/answer/9008080?hl=en-GB), [Sitemaps report](https://support.google.com/webmasters/answer/7451001?hl=en-GB), [Page indexing report](https://support.google.com/webmasters/answer/7440203?hl=en-GB), [manual GA4 pageviews](https://developers.google.com/analytics/devguides/collection/ga4/views), [custom parameters](https://developers.google.com/analytics/devguides/collection/ga4/event-parameters), [custom dimensions](https://support.google.com/analytics/answer/14240153?hl=en), [key events](https://support.google.com/analytics/answer/9267568?hl=en).

## 30-, 60- and 90-day milestones

These are controllable delivery/review goals subject to owner approval and availability. The baseline is too small, and indexing is unknown, to support numerical traffic, click, sales or revenue forecasts. Record the first independently verified organic enquiry, Amazon interest and KDP sale if they occur; do not promise dates or counts. Proposed labour commitment: approximately 4–6 hours a week of useful resource work and 30 minutes of measurement/review. Adjust publication volume to real capacity.

| Horizon | Work and leading indicators | Commercial review |
| --- | --- | --- |
| Days 1–30 | Review/approve the Phase 2A PR; deploy only after approval. Complete the exact Search Console property/verification/sitemap runbook. Confirm production GA4 collection/settings; approve only necessary changes. Establish dated indexing/search/traffic baselines. Draft, practically check and seek approval for small-squad football, British nostalgia and Christmas samples | Separate tests from audience where identifiable. Verify purchase destinations in a normal supported Amazon session. Request a KDP units/royalties export for comparison; unavailable data stay unavailable |
| Days 31–60 | Subject to separate content approval, publish 2–3 substantive resources and corresponding hubs; all new pages linked, canonical, in sitemap and useful without downloads/consent. Inspect indexing and measure actual non-branded queries. Begin resource-led £0 distribution with campaign tags. Prepare rotation sheet and first-session resource | Review each resource's onward book interest and actual Amazon clicks. Use small-count notes, not sweeping percentage claims. Compare verified KDP data separately, allowing seasonality and other marketing |
| Days 61–90 | Aim for 4–6 total excellent resources if review capacity permits; update weak pages from observed queries/coach feedback before adding more. Recheck source dates, links, print quality, mobile measurement and selected canonicals. Retain useful Christmas URL through the season. Review next backlog items | Identify which cluster produces relevant visits and interested books; concentrate effort there. Scale only from consistent observations across several weeks. Assess incremental original-content readiness for future AdSense without applying or installing ads |

Desired search outcome is relevant indexed pages generating non-branded impressions and clicks. Desired engagement is useful resource consumption followed by a relevant book view/preview. Desired intent is attributable Amazon outbound interest. Actual business success is independently verified KDP units/royalties. Technical checks are prerequisites, not fulfilment of the traffic-growth objective.

## Respond to weak results

| Observed condition | First investigation | Next authorised proposal |
| --- | --- | --- |
| Page not indexed | URL Inspection fetch/robots/canonical, index exclusion reason, links and actual usefulness | Correct the evidenced issue; consolidate duplication or improve the content. Do not invent redirects or repeatedly request indexing |
| Indexed, few/no impressions after several weeks | Query fit, actual topic specificity, competitive result format, internal context and distinctive value | Narrow/refine the answer, add tested details or improve a resource; avoid flooding the site with variants. No fixed waiting period guarantees discovery |
| Impressions, few clicks | Query intent, page position, displayed Google title/snippet, country/device and adequate sample size | Improve truthful titles/snippets or targeting. Low CTR at low positions does not establish bad copy |
| Visits, little useful engagement | Whether the resource answers the task promptly, mobile/print usability, source relevance and consent gaps | Fix usefulness and friction; show actual sample/answer or simpler instructions, not aggressive popups |
| Resource engagement, few book views | Relevance of recommendation, visible contextual link, free-only search intent | Explain the additional value of the relevant book; accept that some free-resource visitors will not buy |
| Book views/previews, few Amazon clicks | Reader fit, description, sample legibility, mobile CTA and exact destination | Refine accurate copy/recommendations. Do not change price/ASIN/destination, fabricate trust or install tracking before consent |
| Amazon clicks, no verified sales | Repeated/test clicks, independently available KDP units, marketplace/date lag and listing/customer fit | Ask the owner to review the actual listing and demand. Website analytics cannot see Amazon checkout, so attribution remains limited |

## Future AdSense

Defer an application. Existing navigation, contact and privacy pages are useful foundations, but the catalogue is still predominantly product content and does not yet establish a substantial original resource audience. The planned original resources should stand on their own and earn repeat usefulness before any ad decision. There is no asserted Google minimum article count or traffic threshold here and no guaranteed approval.

Before a future application, recheck Google's current site/URL submission requirements and whether the GitHub Pages project path can be submitted under the current rules; ownership/control of the shared host root has not been confirmed. Do not assume Search Console verification alone proves AdSense site eligibility. Confirm owner age/account eligibility, content rights, publisher privacy disclosures and any required certified consent-management platform for UK/EEA/Swiss ad traffic. The existing analytics-only opt-in is not an advertising CMP. That future work is separately scoped and approved.

If eligible and commercially worthwhile later, prioritise book sales: assess ads on informational resources with sufficient reading value, away from purchase buttons, previews and print controls. Model actual ad benefit versus distraction once traffic exists. Do not place ads merely to make the site look established. No adverts, ad account submission or advertising configuration is part of Phase 2A.

Sources: [AdSense eligibility](https://support.google.com/adsense/answer/9724?hl=en), [adding sites](https://support.google.com/adsense/answer/12169212?hl=en), [Google publisher ad-consent requirements](https://support.google.com/adsense/answer/13554116?hl=en).
