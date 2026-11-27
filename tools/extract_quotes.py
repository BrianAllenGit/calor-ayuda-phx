#!/usr/bin/env python3
"""Builds tools/quotes.json from the pages saved in tools/captures/ (see tools/fetch/).

Only US federal text (CDC, NIOSH, NWS: public domain) is quoted. Nothing is reworded: this script cuts passages out of the
saved page text by their first and last line, and only adds markup (p, ul, li, h3). tools/verify_quotes.py then proves every
block is a word for word match of its capture, and that the page contains exactly the quote.
County and city text is never copied: their sites say "All rights reserved" or state no terms, so the page links to them.
"""
import html as H
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(HERE, "captures")
RETRIEVED = "2026-11-27"
E = H.escape


def lines(name):
    with open(os.path.join(CAP, name), encoding="utf-8", errors="replace") as f:
        return [l.strip() for l in f.read().replace("​", "").split("\n")]


def cut(ls, start, end, start_nth=0):
    """Lines from the first line equal to `start` through the line `end`, blank lines dropped."""
    idx = [i for i, l in enumerate(ls) if l == start]
    a = idx[start_nth]
    b = next(i for i in range(a, len(ls)) if ls[i] == end)
    return [l for l in ls[a:b + 1] if l]


def build(ls, h3, bullets_after=None, bullets_until=None):
    """h3 title line first; the lines between the two markers become a list; the other lines become paragraphs."""
    out, in_ul = [], False
    for i, l in enumerate(ls):
        if i == 0 and h3:
            out.append("<h3>%s</h3>" % E(l))
            continue
        if bullets_after and l == bullets_after:
            out.append("<p>%s</p>" % E(l))
            in_ul = True
            out.append("<ul>")
            continue
        if in_ul and l == bullets_until:
            out.append("</ul>")
            in_ul = False
        out.append("<li>%s</li>" % E(l) if in_ul else "<p>%s</p>" % E(l))
    if in_ul:
        out.append("</ul>")
    return "".join(out)


quotes = {}


def add(key, lang, kind, url, title, body, doc_date):
    assert "—" not in body, key
    quotes[key] = {"lang": lang, "kind": kind, "url": url, "title": title, "html": body, "doc_date": doc_date, "retrieved": RETRIEVED}


# 1. CDC "About Heat and Your Health", the Know the Symptoms part (English and Spanish)
ls = cut(lines("cdc_heat_illness.txt"), "Know the Symptoms", "Watch for symptoms of overheating when you’re outside on hot days.", 0)
add("cdc_symptoms_en", "en", "cdc", "https://www.cdc.gov/heat-health/about/index.html", "CDC: About Heat and Your Health, Know the Symptoms",
    build(ls, True, "Symptoms can include:", "Watch for symptoms of overheating when you’re outside on hot days."), "Page date shown: July 20, 2026")
ls = cut(lines("cdc_about_es.txt"), "Conozca los síntomas", "Esté atento a los síntomas de sobrecalentamiento cuando esté afuera en los días de calor.", 0)
# the Spanish page repeats one sentence twice; keep it once, as the page shows it twice only for screen layout
dedup = [l for i, l in enumerate(ls) if i == 0 or l != ls[i - 1] and l not in ls[:i]]
add("cdc_symptoms_es", "es", "cdc", "https://www.cdc.gov/heat-health/es/about/acerca-del-calor-y-su-salud.html", "CDC: Acerca del calor y su salud, Conozca los síntomas",
    build(dedup, True, "Los síntomas pueden incluir:", "Esté atento a los síntomas de sobrecalentamiento cuando esté afuera en los días de calor."), "Page date shown: not read")

# 2. NIOSH (CDC), heat stroke section, Spanish. Written for the workplace ("trabajador"), the only official Spanish text found.
ls = lines("niosh_es.txt")
a = ls.index("Golpe de calor", ls.index("Golpe de calor") + 1) if ls.count("Golpe de calor") > 1 and ls.index("Golpe de calor") < 15 else ls.index("Golpe de calor")
sec = cut(ls[a:], "Golpe de calor", "Coloque paños húmedos fríos o hielo sobre la cabeza y en el cuello, las axilas y las ingles; o empape la ropa con agua fría.")
body = ["<h3>%s</h3>" % E(sec[0])]
i = 1
while i < len(sec):
    l = sec[i]
    if l in ("Síntomas del golpe de calor", "Primeros auxilios para el golpe de calor"):
        body.append("<h4>%s</h4>" % E(l))
        j = i + 1
        items = []
        while j < len(sec) and sec[j] not in ("Síntomas del golpe de calor", "Primeros auxilios para el golpe de calor"):
            items.append(sec[j]); j += 1
        body.append("<ul>%s</ul>" % "".join("<li>%s</li>" % E(x) for x in items))
        i = j
    else:
        body.append("<p>%s</p>" % E(l)); i += 1
add("niosh_stroke_es", "es", "cdc", "https://www.cdc.gov/niosh/heat-stress/es/about/enfermedades-relacionadas-con-el-calor.html",
    "NIOSH (CDC): Enfermedades relacionadas con el calor, Golpe de calor", "".join(body), "Page date shown: not read")

# 3. NWS (National Weather Service), heat exhaustion and heat stroke, English, for everyone
ls = lines("nws_illness_en.txt")
ex = cut(ls, "Heat Exhaustion", "Seek immediate medical attention if the person vomits, symptoms worsen or last longer than 1 hour")
st = cut(ls, "Heat Stroke", "Using a fan to blow air in someone’s direction may actually make them hotter if heat index temperatures are above the 90s. For more information on all of these heat related illnesses, see the Centers for Disease Control and Prevention (CDC) site.")
st = st[:-1]  # drop the closing "see the CDC site" paragraph; the page links the CDC itself
add("nws_illness_en", "en", "nws", "https://www.weather.gov/safety/heat-illness", "NWS: Heat Cramps, Exhaustion, Stroke",
    "<h3>%s</h3>" % E(ex[0]) + "".join("<p>%s</p>" % E(l) for l in ex[1:]) + "<h3>%s</h3>" % E(st[0]) + "".join("<p>%s</p>" % E(l) for l in st[1:]),
    "Page date shown: none")

with open(os.path.join(HERE, "quotes.json"), "w", encoding="utf-8") as f:
    json.dump(quotes, f, ensure_ascii=False, indent=1)
print("wrote %d quotes" % len(quotes))
for k, q in quotes.items():
    print(k, len(q["html"]))
