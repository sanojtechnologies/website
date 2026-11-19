#!/usr/bin/env python3
"""Generate the press kit pages (<slug>/press/index.html) and the press hub (press/index.html).

The facts, screenshots and wording for each app live in tools/press-apps.json.
Edit that file, then run from the repo root:

    python3 tools/build-press.py

The output is plain HTML that is committed to the repo; nothing runs at deploy time.
Screenshot thumbnails (*-thumb.jpg) and icon-128/192 PNGs are made with sips, not by this script.
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tools", "press-apps.json")
SITE = "https://sanojtechnologies.com"
CF_TOKEN = "54eec4ca55f14407903cc0e5da73ca10"
apps = json.load(open(DATA))

e = html.escape


def play_url(a, campaign_src="presskit"):
    return a.get("play_link") or (
        f"https://play.google.com/store/apps/details?id={a['package']}"
        f"&referrer=utm_source%3D{campaign_src}%26utm_medium%3Ddirect%26utm_campaign%3Dlaunch"
    )


def clean_play(a):
    return f"https://play.google.com/store/apps/details?id={a['package']}"


STYLE = """:root{--bg:#0e1218;--panel:#171d27;--text:#e9eef6;--muted:#a3aebf;--accent:%s;--accent-ink:%s;--line:#2a3342}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:880px;margin:0 auto;padding:24px 16px 64px}
nav.crumbs{font-size:14px;color:var(--muted);margin-bottom:24px} nav.crumbs a{color:var(--muted)}
header{display:flex;gap:20px;align-items:center;margin-bottom:24px}
header img{width:96px;height:96px;border-radius:22px;flex:none}
h1{font-size:34px;line-height:1.15;margin:0 0 4px}
h2{font-size:21px;margin:40px 0 10px;padding-top:20px;border-top:1px solid var(--line)}
.lead{color:var(--muted);margin:0}
a{color:var(--accent)}
ul{padding-left:20px;margin:0} li{margin:6px 0}
table{width:100%%;border-collapse:collapse} th,td{text-align:left;vertical-align:top;padding:8px 12px 8px 0;border-bottom:1px solid var(--line)} th{color:var(--muted);font-weight:600;width:34%%}
.btn{display:inline-block;background:var(--accent);color:var(--accent-ink);font-weight:700;text-decoration:none;padding:12px 22px;border-radius:999px;margin:6px 8px 0 0}
.btn.ghost{background:transparent;color:var(--text);border:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px} .grid img{width:100%%;height:auto;display:block;border-radius:10px}
.grid.land{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.wide{width:100%%;height:auto;border-radius:12px;display:block}
.video{position:relative;aspect-ratio:16/9;background:var(--panel);border-radius:12px;overflow:hidden} .video iframe{position:absolute;inset:0;width:100%%;height:100%%;border:0}
.more{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;list-style:none;padding:0}
.more li{margin:0} .more a{display:flex;gap:12px;align-items:center;padding:10px;border:1px solid var(--line);border-radius:12px;text-decoration:none;color:var(--text)}
.more img{width:44px;height:44px;border-radius:10px;flex:none} .more span{font-weight:600;line-height:1.3}
.cta{margin-top:40px;padding:24px;border:1px solid var(--line);border-radius:16px;background:var(--panel);text-align:center}
.cta p{margin:0 0 8px}
footer{color:var(--muted);font-size:15px;margin-top:40px}
"""

BEACON = f"""<script>
(function(){{var s=document.createElement('script');s.type='module';s.defer=true;s.src='https://static.cloudflareinsights.com/beacon.min.js';s.setAttribute('data-cf-beacon',JSON.stringify({{token:'{CF_TOKEN}'}}));document.body.appendChild(s);}})();
window.trackEvent=function(l){{try{{if(window.zaraz&&zaraz.track)zaraz.track('cta_click',{{label:l}});if(window.goatcounter&&goatcounter.count)goatcounter.count({{path:'cta/'+l,title:l,event:true}});}}catch(e){{}}}};
document.addEventListener('click',function(ev){{var t=ev.target.closest('[data-cta]');if(t)window.trackEvent(t.getAttribute('data-cta'));}},{{passive:true}});
</script>"""


def page(a):
    slug = a["slug"]
    url = f"{SITE}/{slug}/press/"
    title = f"{a['name']} for Android: press kit | Sanoj Technologies"
    if len(title) > 60:
        title = f"{a['name']} for Android: press kit"
    fg = a["feature_graphic"]
    fg_abs = f"{url}{fg['display']}"
    icon_abs = f"{url}icon-512.png"
    shots = a["screenshots"]

    ld_app = {
        "@context": "https://schema.org",
        "@type": ["VideoGame", "MobileApplication"] if a["is_game"] else "MobileApplication",
        "@id": f"{url}#app",
        "name": a["name"],
        "description": a["meta_description"],
        "operatingSystem": a["os"],
        "applicationCategory": a["category_schema"],
        "url": url,
        "installUrl": clean_play(a),
        "sameAs": [clean_play(a)],
        "image": icon_abs,
        "screenshot": [f"{url}{s['file']}" for s in shots],
        "publisher": {"@id": f"{SITE}/#organization"},
        "author": {"@id": f"{SITE}/#organization"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
    }
    if a["is_game"]:
        ld_app["gamePlatform"] = "Android"
        ld_app["genre"] = a["genre"]
    if a.get("date_published"):
        ld_app["datePublished"] = a["date_published"]
    if a.get("file_size"):
        ld_app["fileSize"] = a["file_size"]
    if a.get("content_rating"):
        ld_app["contentRating"] = a["content_rating"]
    ld_crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Press kits", "item": f"{SITE}/press/"},
            {"@type": "ListItem", "position": 3, "name": a["name"], "item": url},
        ],
    }

    out = []
    w = out.append
    w('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">')
    w(f"<title>{e(title)}</title>")
    w(f'<meta name="description" content="{e(a["meta_description"])}">')
    w(f'<link rel="canonical" href="{url}">')
    w('<meta name="theme-color" content="#0e1218">')
    w('<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
    w('<meta property="og:type" content="website">\n<meta property="og:site_name" content="Sanoj Technologies">')
    w(f'<meta property="og:url" content="{url}">')
    w(f'<meta property="og:title" content="{e(a["name"])}: press kit">')
    w(f'<meta property="og:description" content="{e(a["meta_description"])}">')
    w(f'<meta property="og:image" content="{fg_abs}">')
    w(f'<meta property="og:image:width" content="{fg["w"]}">\n<meta property="og:image:height" content="{fg["h"]}">')
    w(f'<meta property="og:image:alt" content="{e(a["name"])} feature graphic">')
    w('<meta name="twitter:card" content="summary_large_image">')
    w(f'<meta name="twitter:title" content="{e(a["name"])}: press kit">')
    w(f'<meta name="twitter:description" content="{e(a["meta_description"])}">')
    w(f'<meta name="twitter:image" content="{fg_abs}">')
    w('<script type="application/ld+json">\n' + json.dumps(ld_app, indent=2, ensure_ascii=False) + "\n</script>")
    w('<script type="application/ld+json">\n' + json.dumps(ld_crumbs, indent=2, ensure_ascii=False) + "\n</script>")
    w(f"<style>\n{STYLE % (a['accent'], a['accent_ink'])}</style>\n</head>\n<body>\n<main>")
    w(f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Sanoj Technologies</a> &rsaquo; <a href="/press/">Press kits</a> &rsaquo; {e(a["name"])}</nav>')
    w(f'<header>\n<img src="icon-192.png" alt="{e(a["name"])} icon" width="96" height="96" fetchpriority="high">')
    w(f'<div><h1>{e(a["h1"])}</h1><p class="lead">{e(a["lead"])}</p></div>\n</header>')
    w(f'<a class="btn" href="{e(play_url(a))}" data-cta="press-{slug}-play">Get it on Google Play</a>')
    if a.get("youtube_id"):
        w(f'<a class="btn ghost" href="https://www.youtube.com/watch?v={a["youtube_id"]}" data-cta="press-{slug}-trailer">Trailer</a>')

    w("\n<h2>What it is</h2>")
    for para in a["what_it_is"]:
        w(f"<p>{e(para)}</p>")
    w("\n<h2>What's different</h2>\n<ul>")
    for b in a["bullets"]:
        w(f"<li>{e(b)}</li>")
    w("</ul>\n\n<h2>Facts</h2>\n<table>")
    for k, v in a["facts"]:
        w(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>")
    w("</table>")
    if a.get("notes"):
        for n in a["notes"]:
            w(f"<p>{e(n)}</p>")

    if a.get("youtube_id"):
        w(f'\n<h2>Trailer</h2>\n<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{a["youtube_id"]}" title="{e(a["name"])} trailer" allowfullscreen loading="lazy"></iframe></div>')

    w('\n<h2>Screenshots</h2>\n<p class="lead">Select a screenshot for the full-size PNG.</p>\n<div class="grid' + (' land' if a.get("landscape") else '') + '">')
    for s in shots:
        w(f'<a href="{s["file"]}"><img src="{s["thumb"]}" alt="{e(s["alt"])}" width="{s["tw"]}" height="{s["th"]}" loading="lazy"></a>')
    w("</div>")

    w("\n<h2>Logo and art</h2>")
    w(f'<p><a href="icon-512.png">Icon, 512x512 PNG</a> &middot; <a href="{fg["file"]}">Feature graphic, {fg["w"]}x{fg["h"]} {fg["file"].rsplit(".",1)[1].upper()}</a></p>')
    w(f'<img class="wide" src="{fg["display"]}" alt="{e(a["name"])} feature graphic" width="{fg["w"]}" height="{fg["h"]}" loading="lazy">')

    w(f'\n<div class="cta"><p><strong>{e(a["name"])}</strong> is available on Google Play for Android.</p><a class="btn" href="{e(play_url(a))}" data-cta="press-{slug}-play-bottom">Get it on Google Play</a></div>')

    others = [o for o in apps if o["slug"] != slug]
    w("\n<h2>More apps by Sanoj Technologies</h2>\n<ul class=\"more\">")
    for o in others:
        w(f'<li><a href="/{o["slug"]}/press/"><img src="/{o["slug"]}/press/icon-128.png" alt="" width="44" height="44" loading="lazy"><span>{e(o["name"])}</span></a></li>')
    w("</ul>")

    w("\n<h2>Contact</h2>")
    w('<p>Manoj, Sanoj Technologies: <a href="mailto:contact@sanojtechnologies.com">contact@sanojtechnologies.com</a></p>')
    w(f'<footer>{e(a["footer_note"])} <a href="/">Sanoj Technologies</a> &middot; <a href="/press/">All press kits</a> &middot; <a href="/privacy.html">Privacy</a></footer>')
    w("</main>")
    w(BEACON)
    w("</body>\n</html>\n")
    return "\n".join(out)


def hub():
    url = f"{SITE}/press/"
    desc = "Press kits for the Android apps and games by Sanoj Technologies: facts, screenshots, icons, feature graphics and trailers."
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Press kits | Sanoj Technologies",
        "url": url,
        "description": desc,
        "publisher": {"@id": f"{SITE}/#organization"},
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{a['slug']}/press/", "name": a["name"]}
                for i, a in enumerate(apps)
            ],
        },
    }
    out = []
    w = out.append
    w('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">')
    w("<title>Press kits: Android apps and games | Sanoj Technologies</title>")
    w(f'<meta name="description" content="{e(desc)}">')
    w(f'<link rel="canonical" href="{url}">\n<meta name="theme-color" content="#0e1218">')
    w('<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
    w('<meta property="og:type" content="website">\n<meta property="og:site_name" content="Sanoj Technologies">')
    w(f'<meta property="og:url" content="{url}">\n<meta property="og:title" content="Sanoj Technologies press kits">')
    w(f'<meta property="og:description" content="{e(desc)}">\n<meta property="og:image" content="{SITE}/og-image.png">')
    w('<meta name="twitter:card" content="summary_large_image">')
    w('<script type="application/ld+json">\n' + json.dumps(ld, indent=2) + "\n</script>")
    w(f"<style>\n{STYLE % ('#7eb892', '#0e1218')}"
      ".apps{list-style:none;padding:0;margin:28px 0 0;display:grid;gap:14px}.apps li{margin:0;display:flex;gap:16px;align-items:center;padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--panel)}"
      ".apps img{width:64px;height:64px;border-radius:14px;flex:none}.apps h2{margin:0;padding:0;border:0;font-size:19px}.apps p{margin:2px 0 6px;color:var(--muted)}.apps .links a{margin-right:16px;font-weight:600}"
      "\n</style>\n</head>\n<body>\n<main>")
    w('<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Sanoj Technologies</a> &rsaquo; Press kits</nav>')
    w('<h1>Press kits</h1>\n<p class="lead">Android apps and games by Sanoj Technologies, a solo developer in India. Each kit has facts, screenshots, the icon and feature graphic, and the trailer where there is one.</p>')
    w('<ul class="apps">')
    for a in apps:
        w(f'<li><img src="/{a["slug"]}/press/icon-128.png" alt="{e(a["name"])} icon" width="64" height="64" loading="lazy">'
          f'<div><h2>{e(a["name"])}</h2><p>{e(a["hub_line"])}</p><span class="links">'
          f'<a href="/{a["slug"]}/press/">Press kit</a>'
          f'<a href="{e(play_url(a))}" data-cta="presshub-{a["slug"]}-play">Google Play</a></span></div></li>')
    w("</ul>")
    w('\n<h2>Contact</h2>\n<p>Manoj, Sanoj Technologies: <a href="mailto:contact@sanojtechnologies.com">contact@sanojtechnologies.com</a></p>')
    w('<footer><a href="/">Sanoj Technologies</a> &middot; <a href="/privacy.html">Privacy</a></footer>\n</main>')
    w(BEACON)
    w("</body>\n</html>\n")
    return "\n".join(out)


for a in apps:
    d = os.path.join(ROOT, a["slug"], "press")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page(a))
os.makedirs(os.path.join(ROOT, "press"), exist_ok=True)
open(os.path.join(ROOT, "press", "index.html"), "w").write(hub())
print("wrote", len(apps), "kits + hub")
