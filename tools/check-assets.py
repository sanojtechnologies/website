#!/usr/bin/env python3
"""Fail the build if an HTML page references a local asset that does not exist.

Covers relative paths (favicon.svg), root-absolute paths (/og-image.png) and
absolute URLs on the production domain, all of which map to files in the repo.
Scans every .html file in the repository root.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(glob.glob(os.path.join(ROOT, "*.html")))
SITE_HOSTS = {"sanojtechnologies.com", "www.sanojtechnologies.com"}
SKIP_SCHEMES = ("#", "mailto:", "tel:", "data:", "javascript:")

attr_re = re.compile(r'(?:href|src)="([^"]+)"')
url_re = re.compile(r'https?://([^/"\s]+)(/[^"\s]*)?')

errors = []


def resolves(path, page):
    """Map a URL path to a repo file and report it if missing."""
    path = path.split("?")[0].split("#")[0]
    if not path or path == "/":
        return
    target = os.path.join(ROOT, path.lstrip("/"))
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    if not os.path.exists(target):
        errors.append(f"{page}: missing local asset {path}")


scanned = 0
for page_path in PAGES:
    page = os.path.relpath(page_path, ROOT)
    with open(page_path, encoding="utf-8") as fh:
        html = fh.read()
    scanned += len(attr_re.findall(html))

    for ref in attr_re.findall(html):
        if ref.startswith(SKIP_SCHEMES) or ref.startswith("http://") or ref.startswith("https://"):
            continue
        resolves(ref, page)

    for host, path in url_re.findall(html):
        if host in SITE_HOSTS:
            resolves(path or "/", page)

    # The Tailwind CDN compiler must not come back: the stylesheet is prebuilt.
    if "cdn.tailwindcss.com" in html:
        errors.append(f"{page} references cdn.tailwindcss.com; use the prebuilt styles.css")

if not os.path.exists(os.path.join(ROOT, "styles.css")):
    errors.append("styles.css is missing")

with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as fh:
    if 'href="styles.css"' not in fh.read():
        errors.append('index.html does not link href="styles.css"')

if errors:
    print("Asset check failed:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"Asset check passed ({len(PAGES)} pages, {scanned} references scanned).")
