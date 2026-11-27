#!/usr/bin/env python3
"""Builds index.html, llms.txt, sitemap.xml, docs/SOURCES.md and docs/NEEDS-NATIVE-READ.md from one place.

Run:  python3 tools/build.py     (after tools/extract_quotes.py when the captures change)
No dependencies. The output files are committed, so the site itself has no build step.

Rule (Brian, 2026-11-27: "We are boosting signal not making"): this page writes no medical or program text of its own.
Every action is a link to an existing official page, a phone number copied from an official page, or a passage of US
federal text (CDC, NIOSH, NWS: public domain) quoted word for word from tools/quotes.json. County, city and 211 text is
"all rights reserved" or has no stated terms, so it is linked and described in one short factual line, never copied.
Every Spanish string we wrote is listed in docs/NEEDS-NATIVE-READ.md.

SEASON: "off" until the county map returns on 2027-05-01. On that day: re-read the county page, set SEASON = "on",
rebuild, rerun the checks (see README).
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKED = "2026-11-27"
CHECKED_TXT = {"es": "27 de noviembre de 2026", "en": "November 27, 2026"}
SITE_URL = "https://brianallengit.github.io/calor-ayuda-phx/"
NAME = "Calor · Ayuda en Phoenix"
E = html.escape
SEASON = "off"

SPANISH_UI = []


def S(es):
    SPANISH_UI.append(es)
    return es


MARICOPA_ES = "https://www.maricopa.gov/3947/Protejase-Del-Calor-Extremo-En-Arizona"
MARICOPA_EN = "https://www.maricopa.gov/1871/Extreme-Heat"
HRN_MAP = "https://hrn.azmag.gov/"
HRN_NET = "https://azmag.gov/Programs/Heat-Relief-Network"
COUNTY_ILL_ES = "https://www.maricopa.gov/3949/Enfermedades-Relacionadas-al-Calor"
COUNTY_ILL_EN = "https://www.maricopa.gov/2457/Signs-of-Heat-Illness"
COUNTY_HELP_ES = "https://www.maricopa.gov/3958/Recursos-a-Su-Alcance"
COUNTY_HELP_EN = "https://www.maricopa.gov/2462/Energy-Assistance-Help-for-Seniors"
PHX_HEAT = "https://www.phoenix.gov/administration/departments/heat.html"
PHX_NEWS = "https://www.phoenix.gov/newsroom/heat-news.html"
PHX_LIB = "https://www.phoenixpubliclibrary.org/"
A211_ES = "https://es.211arizona.org/crisis/heat-relief/"
A211_EN = "https://211arizona.org/crisis/heat-relief/"
A211_HOME = "https://211arizona.org/"
NWS_PHX = "https://www.weather.gov/psr/heat"
NWS_HAZ = "https://www.weather.gov/wrh/hazards?wfo=psr"
HEATRISK_EN = "https://www.wpc.ncep.noaa.gov/heatrisk/"
HEATRISK_ES = "https://www.wpc.ncep.noaa.gov/heatrisk/esp"
CDC_ES = "https://www.cdc.gov/heat-health/es/about/acerca-del-calor-y-su-salud.html"
CDC_EN = "https://www.cdc.gov/heat-health/about/index.html"
NWS_ILL = "https://www.weather.gov/safety/heat-illness"
NIOSH_ES = "https://www.cdc.gov/niosh/heat-stress/es/about/enfermedades-relacionadas-con-el-calor.html"
AZDHS = "https://www.azdhs.gov/preparedness/epidemiology-disease-control/extreme-weather/heat-safety/index.php"

# id -> (url, Spanish label, English label, what we took from it, terms note)
SOURCES = {
    "county_es": (MARICOPA_ES, "Condado de Maricopa: Protéjase del calor extremo en Arizona (español)", "Maricopa County: Protect yourself from extreme heat in Arizona (Spanish page)",
                  "LINK ONLY plus facts in our words: sites run May 1 to September 30; the Heat Relief map returns May 1, 2027 (the page says so in both languages, saved in tools/captures/county_heat_es.txt and county_heat_en.txt); early signs link. The county footer says: \"All content (c) 2006-2026 Maricopa County, AZ and its representatives. All rights reserved.\" (tools/captures/county_copyright.txt), so no text is copied.",
                  "Link only. All rights reserved."),
    "county_en": (MARICOPA_EN, "Condado de Maricopa: Staying Safe in the Extreme Heat (inglés)", "Maricopa County: Staying Safe in the Extreme Heat (English page)",
                  "Same page in English. Read in full.", "Link only. All rights reserved."),
    "hrn_map": (HRN_MAP, "Mapa oficial de la Red de Alivio del Calor (hrn.azmag.gov)", "Official Heat Relief Network map (hrn.azmag.gov)",
                "LINK ONLY. The address is the one the county page gives for its map. The site answers a bot check (Cloudflare) to our automated browser, so the map itself was NOT opened and its language support is unverified. The county says it returns May 1, 2027.",
                "Link only. A human should open it on a phone once the map is back."),
    "hrn_net": (HRN_NET, "Maricopa Association of Governments: Red Regional de Alivio del Calor", "Maricopa Association of Governments: Heat Relief Regional Network",
                "LINK ONLY. Address from the county page. Blocked to our browser by the same bot check; not read.", "Link only. Not read."),
    "county_ill_es": (COUNTY_ILL_ES, "Condado de Maricopa: Enfermedades relacionadas al calor (español)", "Maricopa County: heat-related illness page (Spanish)",
                      "LINK ONLY. Address from the county page. Not opened separately.", "Link only. All rights reserved."),
    "county_help": (COUNTY_HELP_ES, "Condado de Maricopa: Recursos a su alcance, ayuda con la luz y para adultos mayores (español)", "Maricopa County: help with energy bills and seniors (Spanish page)",
                    "LINK ONLY. Address from the county page (\"Vea medios de ayuda\"). Not opened separately.", "Link only. All rights reserved."),
    "phx_heat": (PHX_HEAT, "Ciudad de Phoenix: Oficina de Respuesta y Mitigación del Calor (inglés)", "City of Phoenix: Office of Heat Response and Mitigation",
                 "LINK ONLY. Read: the office coordinates heat response year round; phone 602-262-1800 (TTY 7-1-1) is on the page but not repeated here. The page offers machine translation into 100+ languages.",
                 "Link only. The city terms page returned 404 to our browser, so no reuse terms were found."),
    "phx_news": (PHX_NEWS, "Ciudad de Phoenix: noticias de calor (inglés)", "City of Phoenix: heat news (English)",
                 "Fact in our words: headline \"Dedicated Heat Relief Sites Close For Fall, Winter\", dated October 1, 2026, with the line \"Heat relief will still be available at public libraries.\" (tools/captures/phx_news_list.txt). The article itself was not opened (its address returned 404).",
                 "Link only. No terms found."),
    "phx_lib": (PHX_LIB, "Biblioteca Pública de Phoenix", "Phoenix Public Library",
                "LINK ONLY. Address from the City of Phoenix heat page. Hours and which branches act as heat relief were NOT read.", "Link only."),
    "a211_es": (A211_ES, "211 Arizona: información y recursos para aliviar el calor (español)", "211 Arizona: heat relief information and resources",
                "Facts in our words: dial 2-1-1 or 877-211-8661; live operators in English and Spanish, daily 9 a.m. to 7 p.m.; other languages by interpreter (from the 211 home page); Arizona Relay callers dial 711 or 800-367-8939 and ask for 877-211-8661; \"If you are experiencing a medical emergency or any symptoms of heat-related illness, call 911 immediately\". The page has a cooling-center finder link. Saved: az211.txt, az211_hub_es.txt. The home page and the heat page disagree on whether heat information is 24/7 or 9 to 7; we show 9 to 7.",
                "Link only. \"(c) 2026 Community Information and Referral Services. All Rights Reserved.\""),
    "a211_home": (A211_HOME, "211 Arizona", "211 Arizona", "Phone numbers and hours, read on the home page.", "Link only. All rights reserved."),
    "cdc_es": (CDC_ES, "CDC: Acerca del calor y su salud (español)", "CDC: About Heat and Your Health (Spanish page)",
               "QUOTED word for word: the \"Conozca los síntomas\" section (tools/quotes.json, key cdc_symptoms_es).",
               "US government work. cdc.gov Linking and Reuse page (tools/captures/cdc_linking.txt): public domain content may be reused if you credit CDC, show a no-endorsement disclaimer, do not change the substance, and say the material is available free on CDC's site. The quote notice does all four."),
    "cdc_en": (CDC_EN, "CDC: About Heat and Your Health (inglés)", "CDC: About Heat and Your Health",
               "QUOTED word for word: the \"Know the Symptoms\" section (key cdc_symptoms_en). Page dated July 20, 2026.", "Same CDC terms as above."),
    "niosh_es": (NIOSH_ES, "NIOSH (parte de los CDC): Enfermedades relacionadas con el calor (español)", "NIOSH (part of CDC): Heat-related illnesses (Spanish page)",
                 "QUOTED word for word: the \"Golpe de calor\" section, including \"Llame al 911 para obtener atención médica de emergencia.\" (key niosh_stroke_es). It is written for workers (\"trabajador\"). It is the only official Spanish general text on heat stroke we could read: the CDC Spanish poster returned HTTP 403 and the CDC Spanish signs page returned 404.",
                 "Same CDC terms as above."),
    "nws_ill": (NWS_ILL, "Servicio Meteorológico Nacional: Calambres, agotamiento y golpe de calor (inglés)", "National Weather Service: Heat Cramps, Exhaustion, Stroke",
                "QUOTED word for word (English view only): the \"Heat Exhaustion\" and \"Heat Stroke\" sections, minus the closing \"see the CDC site\" sentence (key nws_illness_en). A Spanish NWS version exists only as an image (Heat_Illness_Spanish.jpg), which is not used.",
                "US government work. weather.gov Disclaimer (tools/captures/nws_copyright.txt): public domain; use is fine if you do not claim it as your own, do not imply endorsement, and do not modify it and present it as official. The NWS name is only used to identify unaltered content."),
    "nws_phx": (NWS_PHX, "Servicio Meteorológico Nacional, Phoenix: página de calor (inglés)", "National Weather Service Phoenix: heat page",
                "LINK ONLY. Read: forecast, HeatRisk 7-day strip, and links to heat safety.", "Link only. Public domain."),
    "nws_haz": (NWS_HAZ, "Servicio Meteorológico Nacional: avisos activos en el área de Phoenix (inglés)", "National Weather Service: active alerts for the Phoenix area",
                "LINK ONLY. Address from the NWS Phoenix heat page.", "Link only."),
    "heatrisk_es": (HEATRISK_ES, "NWS HeatRisk: riesgo de calor para 7 días (español)", "NWS HeatRisk (Spanish page)",
                    "LINK ONLY. The English page has an \"En español\" link to this address. Read the English page: categories 0 to 4 from \"little to no risk\" to \"extreme\". The Spanish page itself was not opened.", "Link only. Public domain."),
    "heatrisk_en": (HEATRISK_EN, "NWS HeatRisk (inglés)", "NWS HeatRisk (English page)", "LINK ONLY.", "Link only. Public domain."),
    "azdhs": (AZDHS, "Departamento de Servicios de Salud de Arizona: seguridad ante el calor (inglés)", "Arizona Department of Health Services: heat safety",
              "LINK ONLY. Read: it points to cooling centers (heat.azdhs.gov), heat illness data and extreme heat warnings.", "Link only. No terms read."),
}

SOURCE_ORDER = ["county_es", "county_en", "hrn_map", "phx_news", "phx_heat", "a211_es", "cdc_es", "cdc_en", "niosh_es", "nws_ill", "nws_phx", "heatrisk_es"]

with open(os.path.join(ROOT, "tools", "quotes.json"), encoding="utf-8") as _f:
    QUOTES = json.load(_f)

WHO = {
    "cdc": ("los Centros para el Control y la Prevención de Enfermedades de EE. UU. (CDC)", "the U.S. Centers for Disease Control and Prevention (CDC)"),
    "nws": ("el Servicio Meteorológico Nacional de EE. UU. (NWS)", "the U.S. National Weather Service (NWS)"),
}

TEXT = {
    "title": S("Hace mucho calor: dónde refrescarte y cuándo pedir ayuda"),
    "title_en": "It is very hot: where to cool off and when to get help",
    "desc": S("Dónde refrescarte en Phoenix, a quién llamar (211) y cuándo llamar al 911 por golpe de calor. Enlaces y textos oficiales, en español e inglés. Sin rastreo."),
    "desc_en": "Where to cool off in Phoenix, who to call (211) and when to call 911 for heat stroke. Official links and texts, in Spanish and English. No tracking.",
    "imgalt": S("Hace mucho calor: dónde refrescarte y cuándo pedir ayuda, Phoenix, Arizona. It is very hot: where to cool off and when to get help."),
}


def ext(url, label, extra=""):
    return '<a href="%s" rel="noopener noreferrer"%s>%s</a>' % (E(url, quote=True), extra, label)


def btn(url, label, cls="secondary", lang=None):
    la = ' lang="%s"' % lang if lang else ""
    return '<a class="btn %s" href="%s" rel="noopener noreferrer"%s>%s</a>' % (cls, E(url, quote=True), la, E(label))


def tel(num, label, cls="call"):
    return '<a class="btn %s" href="tel:%s">%s</a>' % (cls, num, E(label))


def quote(lang, key):
    q = QUOTES[key]
    es = lang == "es"
    link = '<a href="%s" rel="noopener noreferrer">%s</a>' % (E(q["url"], quote=True), E(q["url"]))
    who_es, who_en = WHO[q["kind"]]
    read = ("Leído el %s." if es else "Read on %s.") % CHECKED_TXT[lang]
    note_en = " (en inglés)" if es and q["lang"] == "en" else ""
    label = ("Cita de %s%s, palabra por palabra y sin cambios" % (who_es, note_en)) if es else ("Quoted from %s, word for word and unchanged" % who_en)
    if q["kind"] == "cdc":
        notice = ("Fuente: %s, %s. Material desarrollado por los CDC; información del gobierno de EE. UU., de dominio público. El material está disponible sin costo en el sitio de los CDC. "
                  "Citarlo o enlazarlo no significa que los CDC, el Departamento de Salud y Servicios Humanos (HHS) o el gobierno de EE. UU. nos respalden ni respalden a otros. %s") if es else (
                  "Source: %s, %s. Material developed by CDC; U.S. government information, in the public domain. The material is available for no charge on the CDC website. "
                  "Quoting or linking it does not imply endorsement by CDC, the Department of Health and Human Services (HHS) or the U.S. government of this page or anyone else. %s")
    else:
        notice = ("Fuente: %s, %s. Información del gobierno de EE. UU., de dominio público, sin modificar. No implica respaldo del NWS ni de NOAA. %s") if es else (
                  "Source: %s, %s. U.S. government information, in the public domain, unmodified. Not an endorsement by NWS or NOAA. %s")
    notice = notice % (E(who_es if es else who_en), link, read)
    if es:
        SPANISH_UI.append(label)
        SPANISH_UI.append(notice)
    return '<figure class="quote" lang="%s"><p class="qlabel" lang="%s">%s</p><div class="qbody">%s</div><figcaption>%s</figcaption></figure>' % (
        q["lang"], lang, E(label), q["html"], notice)


def sources(lang, ids):
    head = {"es": "De dónde viene esta información", "en": "Where this information comes from"}[lang]
    chk = {"es": "revisado el", "en": "checked on"}[lang]
    li = []
    for i in ids:
        url, es, en, _f, _t = SOURCES[i]
        li.append('<li>%s <span class="chk">(%s <time datetime="%s">%s</time>)</span></li>' % (ext(url, E(es if lang == "es" else en)), chk, CHECKED, CHECKED_TXT[lang]))
    return '<div class="src"><h3>%s</h3><ul>%s</ul></div>' % (head, "".join(li))


def lab(es, en, lang):
    if lang == "es":
        S(es)
    return es if lang == "es" else en


OFF = SEASON == "off"


def body(lang):
    es = lang == "es"
    L = lambda a, b: lab(a, b, lang)  # noqa: E731
    p = "es" if es else "en"
    county = MARICOPA_ES if es else MARICOPA_EN
    a211 = A211_ES if es else A211_EN
    map_label = L("Mapa oficial de sitios de alivio del calor (vuelve el 1 de mayo de 2027)", "Official heat relief site map (returns May 1, 2027)") if OFF else \
        L("Mapa oficial de sitios de alivio del calor", "Official heat relief site map")
    out = []
    out.append('<p class="lead">%s</p>' % E(L("Dónde refrescarte, a quién llamar y cuándo pedir ayuda de emergencia. Todo viene de fuentes oficiales.",
                                           "Where to cool off, who to call and when to get emergency help. Everything comes from official sources.")))
    out.append('<section class="notice" aria-labelledby="%s-imp-h"><h2 id="%s-imp-h">%s</h2><p>%s</p></section>' % (
        p, p, E(L("Importante", "Important")),
        E(L("Si alguien está muy mal por el calor, llama al 911 ya. Esta página no da consejos médicos: te lleva a fuentes oficiales. No recoge ningún dato tuyo. Los enlaces te llevan a otros sitios.",
             "If someone is very sick from the heat, call 911 now. This page gives no medical advice: it takes you to official sources. It collects no data about you. Links take you to other sites."))))
    if OFF:
        out.append('<section class="tip" aria-labelledby="%s-off-h"><h2 id="%s-off-h">%s</h2><p>%s</p><p>%s</p></section>' % (
            p, p, E(L("Fuera de temporada hasta el 1 de mayo de 2027", "Off season until May 1, 2027")),
            E(L("El Condado de Maricopa dice que su mapa de sitios de alivio del calor vuelve el 1 de mayo de 2027. Los sitios funcionan del 1 de mayo al 30 de septiembre.",
                "Maricopa County says its heat relief site map returns May 1, 2027. The sites run May 1 to September 30.")),
            E(L("La Ciudad de Phoenix publicó el 1 de octubre de 2026 que sus sitios de alivio del calor cerraron para otoño e invierno y que el alivio sigue en las bibliotecas públicas. Si necesitas ayuda hoy, llama al 211.",
                "The City of Phoenix posted on October 1, 2026 that its dedicated heat relief sites closed for fall and winter and that heat relief remains at public libraries. If you need help today, call 211."))))
    # jump menu
    out.append('<nav class="jump no-print" aria-label="%s"><h2>%s</h2><ul>%s</ul></nav>' % (
        E(L("Ir a una sección", "Jump to a section")), E(L("¿Qué necesitas?", "What do you need?")),
        "".join('<li><a class="btn secondary" href="#%s-%s">%s</a></li>' % (p, k, E(t)) for k, t in [
            ("fresco", L("Dónde refrescarme", "Where to cool off")), ("211", L("Llamar al 211", "Call 211")),
            ("senales", L("Señales de alerta", "Warning signs")), ("911", L("Golpe de calor: 911", "Heat stroke: 911"))])))
    # 1. cooling
    out.append('<section class="panel card" id="%s-fresco" tabindex="-1" aria-labelledby="%s-fresco-h"><h2 id="%s-fresco-h">%s</h2><p>%s</p><div class="calls">%s%s%s%s</div>%s</section>' % (
        p, p, p, E(L("1. Dónde refrescarte", "1. Where to cool off")),
        E(L("El Condado de Maricopa tiene el mapa oficial de sitios de alivio del calor: centros de enfriamiento, centros de respiro y estaciones de hidratación. Su página explica cómo usarlo.",
            "Maricopa County has the official map of heat relief sites: cooling centers, respite centers and hydration stations. Its page explains how to use it.")),
        btn(county, L("Abrir la página del condado (español)", "Open the county page (English)"), "primary"),
        btn(HRN_MAP, map_label, "secondary"),
        btn(PHX_LIB, L("Bibliotecas públicas de Phoenix (alivio del calor, según la ciudad)", "Phoenix public libraries (heat relief, per the city)"), "secondary"),
        btn(PHX_NEWS, L("Aviso de la Ciudad de Phoenix, 1 de octubre de 2026 (inglés)", "City of Phoenix notice, October 1, 2026"), "secondary", None if not es else "en"),
        sources(lang, ["county_es" if es else "county_en", "hrn_map", "phx_news", "phx_heat"])))
    # 2. 211
    out.append('<section class="panel card" id="%s-211" tabindex="-1" aria-labelledby="%s-211-h"><h2 id="%s-211-h">%s</h2><p>%s</p><div class="calls">%s%s%s</div><p class="hint">%s</p>%s</section>' % (
        p, p, p, E(L("2. Llama al 211", "2. Call 211")),
        E(L("211 Arizona te conecta con ayuda local, incluida información sobre el calor. Atiende todos los días de 9 a. m. a 7 p. m., con operadores en español e inglés y, según 211, ayuda en otros idiomas con intérpretes.",
            "211 Arizona connects you with local help, including heat information. It answers every day from 9 a.m. to 7 p.m., with live operators in English and Spanish and, per 211, help in other languages through interpreters.")),
        tel("211", L("Llamar al 2-1-1", "Call 2-1-1")),
        tel("+18772118661", L("Llamar al 877-211-8661 (desde cualquier lugar)", "Call 877-211-8661 (from anywhere)")),
        btn(a211, L("Página de 211 sobre el calor (español)", "211 page on heat relief (English)"), "secondary"),
        E(L("Si usas el servicio de relevo de Arizona: marca 711 u 800-367-8939 y pide el 877-211-8661.", "Arizona Relay callers: dial 711 or 800-367-8939 and ask for 877-211-8661.")),
        sources(lang, ["a211_es" if es else "a211_home"])))
    # 3. signs
    out.append('<section class="panel card" id="%s-senales" tabindex="-1" aria-labelledby="%s-senales-h"><h2 id="%s-senales-h">%s</h2><p>%s</p>%s<div class="calls">%s%s</div>%s</section>' % (
        p, p, p, E(L("3. Señales de alerta", "3. Warning signs")),
        E(L("El calor puede enfermar a cualquiera. Esto lo dicen los CDC, copiado sin cambios.", "Heat can make anyone sick. This is what the CDC says, copied unchanged.")),
        quote(lang, "cdc_symptoms_es" if es else "cdc_symptoms_en"),
        btn(COUNTY_ILL_ES if es else COUNTY_ILL_EN, L("Señales de enfermedad por calor, Condado de Maricopa (español)", "Signs of heat illness, Maricopa County (English)"), "secondary"),
        btn(CDC_ES if es else CDC_EN, L("Página completa de los CDC (español)", "Full CDC page (English)"), "secondary"),
        sources(lang, ["cdc_es" if es else "cdc_en", "county_ill_es" if es else "county_es"])))
    # 4. 911
    if es:
        intro911 = "El golpe de calor es una emergencia. Este texto oficial de NIOSH (parte de los CDC) está escrito para trabajadores y dice «trabajador». Es el único texto oficial en español sobre golpe de calor que pudimos leer."
        S(intro911)
        qs = quote(lang, "niosh_stroke_es")
        srcs = ["niosh_es", "a211_es"]
    else:
        intro911 = "Heat stroke is an emergency. This official text is from the National Weather Service, for everyone."
        qs = quote(lang, "nws_illness_en")
        srcs = ["nws_ill", "a211_home"]
    out.append('<section class="panel card" id="%s-911" tabindex="-1" aria-labelledby="%s-911-h"><h2 id="%s-911-h">%s</h2><p>%s</p><div class="calls">%s</div>%s%s</section>' % (
        p, p, p, E(L("4. Golpe de calor: llama al 911", "4. Heat stroke: call 911")), E(intro911),
        tel("911", L("Llamar al 911", "Call 911"), "call emergency big"),
        qs, sources(lang, srcs)))
    # 5. more
    out.append('<section class="panel" id="%s-mas" tabindex="-1" aria-labelledby="%s-mas-h"><h2 id="%s-mas-h">%s</h2><p>%s</p><div class="calls">%s%s%s%s</div>%s</section>' % (
        p, p, p, E(L("5. Más: avisos de calor y ayuda con la luz", "5. More: heat alerts and help with energy bills")),
        E(L("El Servicio Meteorológico Nacional publica el riesgo de calor de los próximos 7 días (HeatRisk). El condado enlaza ayuda con facturas de luz y servicios y ayuda para adultos mayores.",
            "The National Weather Service publishes the heat risk for the next 7 days (HeatRisk). The county links help with energy and utility bills and help for seniors.")),
        btn(HEATRISK_ES if es else HEATRISK_EN, L("HeatRisk: riesgo de calor, 7 días (español)", "HeatRisk: heat risk, 7 days"), "primary"),
        btn(NWS_PHX, L("Servicio Meteorológico Nacional, Phoenix: calor (inglés)", "National Weather Service Phoenix: heat"), "secondary", "en" if es else None),
        btn(NWS_HAZ, L("Avisos activos en el área de Phoenix (inglés)", "Active alerts for the Phoenix area"), "secondary", "en" if es else None),
        btn(COUNTY_HELP_ES if es else COUNTY_HELP_EN, L("Ayuda con la luz y para adultos mayores, Condado (español)", "Help with energy bills and seniors, County"), "secondary"),
        sources(lang, ["nws_phx", "heatrisk_es" if es else "heatrisk_en", "county_help"])))
    out.append('<section class="panel no-print" aria-labelledby="%s-print-h"><h2 id="%s-print-h">%s</h2><p>%s</p><button type="button" class="btn secondary js-print">%s</button></section>' % (
        p, p, E(L("Imprimir", "Print")),
        E(L("Imprime esta página para ponerla en el refrigerador o dársela a un vecino. Los enlaces se imprimen completos.", "Print this page for the fridge or to give to a neighbor. Links print in full.")),
        E(L("Imprimir esta página", "Print this page"))))
    return "\n".join(out)


def ld_items():
    return [("Maricopa County: Staying Safe in the Extreme Heat", MARICOPA_EN), ("211 Arizona: Heat Relief Information and Resources", A211_EN),
            ("CDC: About Heat and Your Health", CDC_EN), ("National Weather Service: Heat Cramps, Exhaustion, Stroke", NWS_ILL),
            ("National Weather Service: HeatRisk", HEATRISK_EN)]


def page():
    es_html, en_html = body("es"), body("en")
    items = ld_items()
    graph = [
        {"@type": "Organization", "@id": SITE_URL + "#org", "name": NAME, "url": SITE_URL, "logo": SITE_URL + "apple-touch-icon.png",
         "description": "Free, ad-free, zero-tracking page in Spanish and English that links official heat relief, 211 and heat illness resources for Phoenix, Arizona."},
        {"@type": "WebSite", "@id": SITE_URL + "#website", "url": SITE_URL, "name": NAME, "description": TEXT["desc"], "inLanguage": ["es", "en"], "publisher": {"@id": SITE_URL + "#org"}},
        {"@type": "WebPage", "@id": SITE_URL + "#webpage", "url": SITE_URL, "name": TEXT["title"], "description": TEXT["desc"], "inLanguage": ["es", "en"],
         "isPartOf": {"@id": SITE_URL + "#website"}, "publisher": {"@id": SITE_URL + "#org"}, "dateModified": CHECKED,
         "primaryImageOfPage": {"@type": "ImageObject", "url": SITE_URL + "og-image.png", "width": 1200, "height": 630},
         "about": {"@type": "Thing", "name": "Extreme heat safety and heat relief in Phoenix, Arizona"}},
        {"@type": "ItemList", "@id": SITE_URL + "#sources", "name": "Official heat resources for Phoenix, Arizona", "inLanguage": ["es", "en"], "numberOfItems": len(items),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": u} for i, (n, u) in enumerate(items)]},
    ]
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=1, ensure_ascii=False)
    foot_es = ("Este sitio no tiene analíticas, cookies ni anuncios y no guarda nada. Está alojado en GitHub Pages, que puede guardar registros estándar de visitas que nosotros no podemos ver. "
               "No somos parte del Condado de Maricopa, la Ciudad de Phoenix, 211 Arizona, los CDC ni el Servicio Meteorológico Nacional. No es consejo médico. Emergencia: 911.")
    foot_en = ("This site has no analytics, cookies or ads and saves nothing. It is hosted on GitHub Pages, which may keep standard visit logs that we cannot see. "
               "We are not part of Maricopa County, the City of Phoenix, 211 Arizona, the CDC or the National Weather Service. This is not medical advice. Emergency: 911.")
    S(foot_es)
    for t in ["Ir al contenido", "Hace mucho calor", "Dónde refrescarte · Phoenix"]:
        S(t)
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{site}">
<link rel="alternate" hreflang="es" href="{site}">
<link rel="alternate" hreflang="en" href="{site}">
<link rel="alternate" hreflang="x-default" href="{site}">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{imgalt}">
<meta property="og:url" content="{site}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_US">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}og-image.png">
<meta name="twitter:image:alt" content="{imgalt}">
<meta name="theme-color" content="#9a3412">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<script type="application/ld+json">{jsonld}</script>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; manifest-src 'self'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<link rel="stylesheet" href="style.css">
<noscript><link rel="stylesheet" href="noscript.css"></noscript>
</head>
<body>
<a class="skip es" href="#main">Ir al contenido</a>
<a class="skip en" href="#main" lang="en">Skip to content</a>
<header class="top">
  <div class="brand">
    <h1 class="es">Hace mucho calor <span class="where">Dónde refrescarte · Phoenix</span></h1>
    <h1 class="en" lang="en">It is very hot <span class="where">Where to cool off · Phoenix</span></h1>
  </div>
  <div class="langs no-print" role="group" aria-label="Idioma / Language">
    <button type="button" id="lang-es" data-lang="es" lang="es" aria-label="ES, Español" aria-pressed="true">ES</button>
    <button type="button" id="lang-en" data-lang="en" lang="en" aria-label="EN, English" aria-pressed="false">EN</button>
  </div>
</header>

<main id="main" tabindex="-1">
<div class="es wrap">
{es}
</div>
<div class="en wrap" lang="en">
{en}
</div>
</main>

<footer>
  <p class="es">{foot_es}</p>
  <p class="en" lang="en">{foot_en}</p>
  <p>{name} · MIT</p>
</footer>
<script src="app.js"></script>
</body>
</html>
""".format(desc=E(TEXT["desc"]), title=E(TEXT["title"]), imgalt=E(TEXT["imgalt"]), jsonld=jsonld, site=SITE_URL, name=NAME,
           es=es_html, en=en_html, foot_es=E(foot_es), foot_en=E(foot_en))


def llms():
    return """# %s

> A free, ad-free, zero-tracking one-page tool in Spanish and English for people in the Phoenix, Arizona area who are hot or worried about heat. It boosts existing official pages (linked, not copied): the Maricopa County heat relief page and map, 211 Arizona, the CDC and NWS heat illness texts (quoted word for word, public domain), and the National Weather Service heat forecast. It gives general information, not medical advice. In an emergency, call 911. Read on %s.

## What it is
- Where to cool off: Maricopa County's official Heat Relief Network map (sites run May 1 to September 30; the county says the map returns May 1, 2027).
- 211 Arizona: dial 2-1-1 or 877-211-8661, daily 9 a.m. to 7 p.m., English and Spanish.
- Warning signs of heat illness (CDC text, Spanish and English, unchanged) and the heat stroke text with the 911 instruction (NIOSH Spanish, NWS English, unchanged).
- Heat forecast: NWS Phoenix heat page and HeatRisk.

## Who it is for
- People in the Phoenix area who need a place to cool off, or who are not sure when heat is an emergency.

## Key links
- Page: %s
- English view: %s?lang=en

## Sources
%s
""" % (NAME, CHECKED, SITE_URL, SITE_URL, "\n".join("- %s: %s" % (SOURCES[i][2], SOURCES[i][0]) for i in SOURCE_ORDER))


def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>%s</loc>
    <lastmod>%s</lastmod>
    <xhtml:link rel="alternate" hreflang="es" href="%s"/>
    <xhtml:link rel="alternate" hreflang="en" href="%s"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>
  </url>
</urlset>
""" % (SITE_URL, CHECKED, SITE_URL, SITE_URL, SITE_URL)


def sources_md():
    out = ["# Sources", "",
           "Every external fact and quote on the page, with the page it was read on and the terms that allow (or do not allow) using it.",
           "All pages were read on %s. Generated by `tools/build.py`; edit the lists there." % CHECKED, "",
           "Rule: boost existing official pages, write nothing of our own. Only US federal text (CDC, NIOSH, NWS) is quoted. County, city and 211 pages are linked, with one short factual line in our words.", "",
           "## Source pages", "", "| # | Source | URL | What the page uses | Terms |", "|---|---|---|---|---|"]
    for n, (k, (url, _es, en, facts, terms)) in enumerate(SOURCES.items(), 1):
        out.append("| %d | %s | %s | %s | %s |" % (n, en, url, facts.replace("|", "/"), terms.replace("|", "/")))
    out += ["", "## Quotes (%d)" % len(QUOTES), "", "| Key | Language | Source | Document date |", "|---|---|---|---|"]
    for k, q in QUOTES.items():
        out.append("| %s | %s | %s | %s |" % (k, q["lang"], q["title"].replace("|", "/"), q["doc_date"]))
    out += ["", "## Looked for and not used", "",
            "- The county's own words for \"the map returns May 1, 2027\": the county site says \"All rights reserved\", so the date is given in our words with a link. If the county allows quoting that one sentence, a human can ask (not done: nobody was contacted).",
            "- The Heat Relief Network map (hrn.azmag.gov) and the MAG page: blocked by a bot check; not opened. Whether the map has a Spanish toggle is unverified.",
            "- City of Phoenix cooling or respite center pages: the address we guessed returned 404; the heat office page and news list were read. Which libraries act as heat relief is not stated on what we read.",
            "- Official Spanish CDC heat-stroke text for the general public: the CDC Spanish poster returned 403 and the Spanish signs page 404. NIOSH's Spanish page (workers) is used instead and labeled.",
            "- NWS Spanish heat-illness text: exists only as an image; not used.",
            "- ADHS heat page (cooling center finder at heat.azdhs.gov): read, not on the page (the county and 211 pages cover the same). Linked in README only.",
            "", "## Notes for the reviewer", "",
            "- Spanish labels written for this page were produced by an AI and need a native-speaker read: see NEEDS-NATIVE-READ.md. Quoted Spanish is the CDC's own.",
            "- Nothing on the page was tried against a live heat relief site: it is November and the sites are closed. Hours, addresses and the map are not on this page by design.", ""]
    return "\n".join(out)


def native_md():
    seen, rows = set(), []
    for s in SPANISH_UI:
        s = html.unescape(re.sub(r"\s+", " ", s)).strip()
        s = re.sub(r"<[^>]+>", "", s)
        if s and s not in seen:
            seen.add(s)
            rows.append(s)
    out = ["# Spanish text written for this page (needs a native-speaker read)", "",
           "Generated by `tools/build.py`. Every Spanish string below was written by an AI, not copied from a source (quoted CDC text is not listed).",
           "Questions for the reader: natural for Mexican and Central American Spanish readers in Phoenix? \"Sitios de alivio del calor\", \"centros de enfriamiento\" and \"golpe de calor\" are the county's and CDC's own terms: keep. \"Fuera de temporada\", \"relevo de Arizona\", \"HeatRisk\" ok?", ""]
    out += ["%d. %s" % (i, r) for i, r in enumerate(rows, 1)]
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    allq = " ".join(q["html"] for q in QUOTES.values())
    assert "911" in allq
    with open(os.path.join(ROOT, "tools", "captures", "az211.txt"), encoding="utf-8") as f:
        t211 = f.read()
    for n in ["877-211-8661", "800-367-8939", "9:00am"]:
        assert n in t211, n
    out = page()
    for name, content in [("index.html", out), ("llms.txt", llms()), ("sitemap.xml", sitemap()), ("docs/SOURCES.md", sources_md()), ("docs/NEEDS-NATIVE-READ.md", native_md())]:
        assert chr(0x2014) not in content, name
        os.makedirs(os.path.dirname(os.path.join(ROOT, name)) or ROOT, exist_ok=True)
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(content)
    print("built index.html (%d bytes); title %d chars, desc %d chars; en title %d, en desc %d" % (len(out), len(TEXT["title"]), len(TEXT["desc"]), len(TEXT["title_en"]), len(TEXT["desc_en"])))
