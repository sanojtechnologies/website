#!/usr/bin/env python3
"""Fail the build if index.html references a local asset that does not exist.

Covers relative paths (favicon.svg), root-absolute paths (/og-image.png) and
absolute URLs on the production domain, all of which map to files in the repo.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
SITE_HOSTS = {"sanojtechnologies.com", "www.sanojtechnologies.com"}
SKIP_SCHEMES = ("#", "mailto:", "tel:", "data:", "javascript:")

attr_re = re.compile(r'(?:href|src)="([^"]+)"')
url_re = re.compile(r'https?://([^/"\s]+)(/[^"\s]*)?')

errors = []


def resolves(path):
    """Map a URL path to a repo file. Returns True if it should be checked."""
    path = path.split("?")[0].split("#")[0]
    if not path or path == "/":
        return True
    target = os.path.join(ROOT, path.lstrip("/"))
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    if not os.path.exists(target):
        errors.append(f"missing local asset: {path}")
    return True


with open(HTML, encoding="utf-8") as fh:
    html = fh.read()

for ref in attr_re.findall(html):
    if ref.startswith(SKIP_SCHEMES):
        continue
    if ref.startswith("http://") or ref.startswith("https://"):
        continue
    resolves(ref)

for host, path in url_re.findall(html):
    if host in SITE_HOSTS:
        resolves(path or "/")

# The Tailwind CDN compiler must not come back: the stylesheet is prebuilt.
if "cdn.tailwindcss.com" in html:
    errors.append("index.html references cdn.tailwindcss.com; use the prebuilt styles.css")

if not os.path.exists(os.path.join(ROOT, "styles.css")):
    errors.append("styles.css is missing")

if 'href="styles.css"' not in html:
    errors.append('index.html does not link href="styles.css"')

if errors:
    print("Asset check failed:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"Asset check passed ({len(attr_re.findall(html))} references scanned).")
