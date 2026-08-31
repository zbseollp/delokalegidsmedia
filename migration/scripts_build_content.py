"""
delokalegidsmedia.nl is een eenpagina-site. De REST API, de sitemap, de feed
en zelfs robots.txt geven allemaal een 500; alleen de voorpagina doet het. Het
Internet Archive kent ook geen andere pagina's van dit domein.

De inhoud komt dus uit de gespiegelde HTML. In plaats van de Elementor-markup
plat te slaan (dat levert losse zinnen zonder verband op) wordt hier de tekst
gestructureerd uitgelezen: de SEO-meta, de kop en intro, de vier korte
beloftes, de sectieteksten en de lijst met regionale gidsen.
"""
import html as H
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC, MIRROR = HERE / "source", HERE / "mirror"
SRC.mkdir(parents=True, exist_ok=True)
OUT = HERE.parent / "src" / "data"
OUT.mkdir(parents=True, exist_ok=True)
DOMAIN = "https://delokalegidsmedia.nl"

raw = (MIRROR / "index.html").read_text(encoding="utf-8", errors="replace")
head = raw.split("</head>")[0]
body = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", raw.split("<body", 1)[1], flags=re.S)


def pick(text, pattern):
    m = re.search(pattern, text, re.I | re.S)
    return H.unescape(m.group(1)).strip() if m else ""


def clean(text):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


# --- teksten in documentvolgorde ---------------------------------------
blocks = []
for m in re.finditer(r"<(h[1-4]|p)[^>]*>(.*?)</\1>", body, re.S):
    t = clean(m.group(2))
    if t:
        blocks.append((m.group(1), t))

heads = [t for tag, t in blocks if tag.startswith("h")]
paras = [t for tag, t in blocks if tag == "p"]

# De vier korte beloftes staan tussen de intro en de eerste H2.
intro = next((t for t in paras if t.startswith("DeLokaleGidsMedia.nl is een uitgever")), "")
promises = [t for t in paras if 40 < len(t) < 110 and t != intro][:4]


def para_after(heading, skip=0):
    """De eerste alinea die na een bepaalde kop staat."""
    seen = False
    hits = 0
    for tag, t in blocks:
        if tag.startswith("h") and t == heading:
            seen = True
            continue
        if seen and tag == "p":
            if hits >= skip:
                return t
            hits += 1
    return ""


# --- regionale gidsen --------------------------------------------------
guides = []
for url in sorted({u for u in re.findall(r'href="(https?://[a-z0-9.-]*gids[a-z0-9.-]*\.nl/?)"', body)}):
    host = re.sub(r"^https?://", "", url).strip("/")
    naam = host.replace(".nl", "")
    # "deaaltengids" -> "Aalten", "dehofvantwentegids" -> "Hof van Twente"
    kern = re.sub(r"^de", "", naam)
    kern = re.sub(r"gids$", "", kern)
    guides.append({"url": url, "host": host, "slug": kern, "name": kern.capitalize()})

# --- afbeeldingen ------------------------------------------------------
images = sorted({
    i for i in re.findall(
        r"(/wp-content/uploads/[^\"'?\s)]+?\.(?:jpe?g|png|webp|gif|svg))", body, re.I)
})

# De vier iconen staan in dezelfde volgorde als de vier beloftes; het origineel
# zette ze er telkens boven.
icons = []
for m in re.finditer(r"/wp-content/uploads/2023/02/(icon-park-solid_[a-z-]+\.png)", body):
    if m.group(1) not in icons:
        icons.append("/wp-content/uploads/2023/02/" + m.group(1))

hero_image = next(
    (i for i in images if "phone_14_pro_mockup" in i and "-262x300" not in i), "")

data = {
    "icons": icons,
    "heroImage": hero_image,
    "seoTitle": pick(head, r"<title>(.*?)</title>"),
    "seoDescription": pick(head, r'<meta name="description" content="(.*?)"'),
    "canonical": pick(head, r'<link rel="canonical" href="(.*?)"') or DOMAIN + "/",
    "ogImage": pick(head, r'<meta property="og:image" content="(.*?)"').replace(DOMAIN, ""),
    "h1": heads[0] if heads else "",
    "intro": intro,
    "promises": promises,
    "sections": [
        {"title": "Onze regionale uitgaves", "body": para_after("Onze regionale uitgaves")},
        {"title": "Complete portals voor elke plaats", "body": para_after("Complete portals voor elke plaats")},
        {"title": "Contact met DeLokaleGidsMedia", "body": para_after("Contact met DeLokaleGidsMedia")},
    ],
    "footerText": next((t for t in paras if t.startswith("DeLokaleGidsMedia.nl is uitgever")), ""),
    "guides": guides,
    "images": images,
}
(OUT / "content.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
(SRC / "images.txt").write_text("\n".join(DOMAIN + i for i in images), encoding="utf-8")

print(f"seoTitle: {data['seoTitle'][:70]}")
print(f"h1:       {data['h1']}")
print(f"intro:    {data['intro'][:90]}")
print(f"beloftes: {len(data['promises'])}")
for p in data["promises"]:
    print(f"   - {p[:80]}")
print(f"secties:  {[s['title'] for s in data['sections']]}")
for s in data["sections"]:
    print(f"   {s['title'][:34]:<34} {'tekst gevonden' if s['body'] else 'GEEN TEKST'}")
print(f"gidsen:   {len(guides)}")
print(f"afbeeldingen: {len(images)}")
print(f"iconen:       {len(icons)}")
print(f"hero:         {hero_image or '(geen)'}")
