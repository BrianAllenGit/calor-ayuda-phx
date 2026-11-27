# Website definition of done: evidence

Mirrors Brian's website definition of done (vault: `me/working-together/web-definition-of-done.md`). Run 2026-11-27 inside Docker only (Playwright 1.49.1 image, axe-core 4.10.2, Lighthouse 12.2.1). Re-run with `./tools/audit.sh` and `./tools/dod.sh`. Planned address (not live): https://brianallengit.github.io/calor-ayuda-phx/

## 1. Accessibility
- [x] axe-core 0 violations, ES and EN at 375 and 1280 in Chromium, and in WebKit at iPhone 15 (393), iPhone SE (320) and an iPhone 16 Pro Max size (440), both languages (`docs/screenshots/audit-report.txt`).
- [x] Keyboard: 36 tab stops per language, 0 without a visible focus indicator, no trap, skip link first (`docs/lighthouse/extra.txt`).
- [x] One H1 per language, headings in order, landmarks (header, nav, main, labeled sections, footer). No text field on the page, so no on-screen keyboard case.
- [x] 0 tap targets under 44px at 320, 375, 768 and in WebKit. Contrast checked by axe.
- [x] reduced-motion and forced-colors screenshots in `docs/lighthouse/`; text spacing overrides at 320 and 375; 200% zoom equivalent. JavaScript off: both languages in the static HTML.
- [ ] Not machine-verifiable: real screen reader pass, native Spanish read, real-device phone test.

## 2. Phone first
- [x] No horizontal scroll or overflow at 320, 375, 768, 1280 and in WebKit iPhone sizes, both languages. Screenshots in `docs/screenshots/`.
- [ ] The page is long on a phone (many quoted blocks and source lists); a human should judge whether to shorten.

## 3. Languages
- [x] ES default, visible ES/EN switch, `lang` on `<html>` updates, hreflang es/en/x-default.

## 4 to 7. Search, previews, GEO, polish
- [x] Unique title (56) and description (155), canonical, robots, sitemap, JSON-LD (Organization, WebSite, WebPage, ItemList that matches visible links; no FAQPage), og and twitter tags, og-image 1200x630, llms.txt, favicons, manifest, print styles (`docs/lighthouse/validate.txt`).
- [x] Lighthouse mobile, both languages: performance 100, accessibility 100, best practices 100, SEO 100 (`docs/lighthouse/lighthouse.txt`).
- [ ] Not done by machine: Facebook and X link debuggers, Google Rich Results Test (by hand before ship).

## 8. Trust and safety
- [x] Zero tracking, storage, ads. Strict CSP, no third-party requests (the audit fails on any external request).
- [x] Every fact is from an official page with a "checked on" date. Quotes are proven word for word (`python3 tools/verify_quotes.py`).
- [ ] A human should open the county map (hrn.azmag.gov) and the MAG page on a phone when the map returns: our browser was blocked, so they were never read.
- [ ] Re-read every source on the day of shipping, and on 2027-05-01 (see README).
