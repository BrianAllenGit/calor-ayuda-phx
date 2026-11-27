# Calor · Ayuda en Phoenix

A free, ad-free, zero-tracking, Spanish-first page (Spanish and English) for one reason to arrive: "Hace mucho calor: dónde refrescarte y cuándo pedir ayuda." It writes no heat advice of its own. It boosts existing official pages: the Maricopa County heat relief page and map, 211 Arizona, the CDC and National Weather Service heat illness texts (quoted word for word, public domain) and the NWS HeatRisk forecast. Actions: find a cooling place, call 211, know the warning signs, call 911 for heat stroke.

Status: private draft. Not published. Planned address once shipped: https://brianallengit.github.io/calor-ayuda-phx/

## Off season until May 1, 2027

The county says its Heat Relief map returns on May 1, 2027 (sites run May 1 to September 30). The page says so in a banner (`SEASON = "off"` in `tools/build.py`). The City of Phoenix said on 2026-10-01 that its dedicated sites closed for fall and winter and that heat relief remains at public libraries.

**On 2027-05-01 (or when the county map is back):** re-read the county page, 211 hours and the map (a human should open the map on a phone: our browser was blocked), re-capture with `tools/fetch/fetchall.sh`, set `SEASON = "on"`, rebuild, rerun the checks, then ask the owner to publish. The in-season wording in `build.py` was not verified against a live season.

## What is quoted and what is only linked

Quoted word for word (US federal, public domain, with the credit, no-endorsement notice and "free on the agency site" line CDC asks for): CDC "Know the Symptoms" (English and Spanish), NIOSH (CDC) Spanish "Golpe de calor" section with "Llame al 911", NWS heat exhaustion and heat stroke (English). `python3 tools/verify_quotes.py` proves each block matches its saved source (4 quotes).

Only linked, never copied: Maricopa County (all rights reserved), City of Phoenix (no terms found), 211 Arizona (all rights reserved), MAG and the map. Phone numbers (211, 877-211-8661, 911) are facts read from 211 and the quotes. Details: [docs/SOURCES.md](docs/SOURCES.md). Spanish labels we wrote: [docs/NEEDS-NATIVE-READ.md](docs/NEEDS-NATIVE-READ.md).

## Privacy promise

No cookies, no localStorage, no accounts, no forms, no analytics, no ads, no third-party fonts or scripts. A strict Content Security Policy blocks every outside request. The language choice lives only in the page address (`?lang=en`). GitHub Pages, the planned host, may keep standard visit logs.

## Checks (all in Docker)

```
python3 tools/extract_quotes.py && python3 tools/build.py && python3 tools/verify_quotes.py
./tools/audit.sh    # axe (Chromium 375/1280, WebKit iPhone 15, SE, 16 Pro Max size), overflow 320/375/768, screenshots
./tools/dod.sh      # icons, head and JSON-LD validation, keyboard, text spacing, Lighthouse mobile (run twice the first time: icons are created on the first run)
```

The page has no text input, so there is no on-screen keyboard case to check.

## Deploy to GitHub Pages (only when the owner says so)

1. Make the repository public. 2. Settings, Pages, branch `main`, folder `/ (root)`. 3. If the address changes, update `SITE_URL` in `tools/build.py` and rebuild.

## License

MIT for the code and the page's own wording, see `LICENSE`. Quoted CDC, NIOSH and NWS text is a US government work. Linked pages belong to their publishers. This page is not affiliated with any of them.
