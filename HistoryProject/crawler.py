# -*- coding: utf-8 -*-
"""
Iranian-wars Wikipedia crawler — writes every unique link to a file immediately.

Usage:
    python crawler.py

Features:
- START_URLS: add your initial pages here
- MAX_DEPTH: how deep to follow links (0 = only the start pages)
- OUTPUT_FILE: each unique url is appended immediately as discovered
- Safe to stop/restart: existing links are loaded from OUTPUT_FILE on start
"""

import requests
from bs4 import BeautifulSoup
from collections import deque
import time
import os

# -------------------------
# CONFIG
# -------------------------

BASE_URL = "https://fa.wikipedia.org"
MAIN_URL = BASE_URL + "/wiki/فهرست_جنگ‌های_ایران"

START_URLS = [
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_ایران',
    f'https://fa.wikipedia.org/wiki/رده:ائتلاف%E2%80%8Cهای_نظامی_ایران',
    f'https://fa.wikipedia.org/wiki/رده:پیمان%E2%80%8Cنامه%E2%80%8Cهای_شاهنشاهی_ساسانی',
    f'https://fa.wikipedia.org/wiki/رده:پیمان%E2%80%8Cهای_شاهنشahi_اشکانیان',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_افشاریان',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_دودمان_پهلوی',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_سلسله_قاجاریان',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_صفویان',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_صلح_ایران',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_معاصر_ایران',
    f'https://fa.wikipedia.org/wiki/رده:معاهده%E2%80%8Cهای_هخامنشیان',
    "https://fa.wikipedia-on-ipfs.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%AC%D9%86%DA%AF%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86",
    "https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D8%AC%D9%86%DA%AF%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86",
    "https://fa.wikipedia.org/wiki/%D8%B1%D8%AF%D9%87:%D8%AC%D9%86%DA%AF%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86",
]

# =============================================
import json

with open("/content/Crawled_Texts3.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if "url" in item:  # make sure key exists
        START_URLS.append(item["url"])

print(len(START_URLS), "URLs collected")
print(START_URLS[:5])  # preview first 5

# =============================================

OUTPUT_FILE = "links_v2.txt"
MAX_DEPTH = 1
REQUEST_DELAY = 0.5  # seconds between requests
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IranWarsCrawler/1.0)"}

# -------------------------
# Helpers
# -------------------------
def load_existing_links(path):
    """Load already-saved links from OUTPUT_FILE into a set."""
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def append_link_to_file(path, url):
    """Append a single url to the output file and flush."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(url.rstrip() + "\n")
        f.flush()  # ensure it's written to disk right away

def normalize_and_filter_href(href):
    """
    Normalize hrefs encountered in pages to absolute URLs.
    Returns None if href should be skipped (files, categories, anchors, etc).
    """
    if not href:
        return None

    # handle protocol-relative URLs
    if href.startswith("//"):
        href = "https:" + href

    # keep only URLs that contain /wiki/
    if "/wiki/" not in href:
        return None

    # extract part after /wiki/
    try:
        title = href.split("/wiki/", 1)[1]
    except Exception:
        return None

    # skip anchors, categories, files, special pages (anything with ':') and empty titles
    if not title or ":" in title or "#" in title:
        return None

    # if href is already absolute, return it; else prefix with BASE_URL
    if href.startswith("http://") or href.startswith("https://"):
        # remove fragments
        return href.split("#", 1)[0]
    elif href.startswith("/wiki/"):
        return BASE_URL + href.split("#", 1)[0]
    else:
        return None

def get_links_from_url(url):
    """Fetch a page and return all normalized internal wiki links (set)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return set()

    soup = BeautifulSoup(r.text, "html.parser")
    found = set()
    for a in soup.find_all("a", href=True):
        normalized = normalize_and_filter_href(a["href"])
        if normalized:
            found.add(normalized)
    return found

# -------------------------
# Main crawling loop
# -------------------------
def main():
    visited = load_existing_links(OUTPUT_FILE)
    print(f"[INFO] Loaded {len(visited)} existing links from {OUTPUT_FILE!r}")

    q = deque()
    # seed queue with start urls (depth 0)
    for s in START_URLS:
        if s not in visited:
            visited.add(s)
            append_link_to_file(OUTPUT_FILE, s)
            print(f"[ADD start] {s}")
        q.append((s, 0))

    while q:
        url, depth = q.popleft()
        # if we've reached the max depth, don't expand this node
        if depth >= MAX_DEPTH:
            continue

        print(f"[CRAWL depth={depth}] {url}")
        links = get_links_from_url(url)
        time.sleep(REQUEST_DELAY)

        for link in links:
            if link not in visited:
                visited.add(link)
                append_link_to_file(OUTPUT_FILE, link)
                print(f"  [NEW depth={depth+1}] {link}")
                # enqueue for further crawling if we haven't reached next depth
                if depth + 1 < MAX_DEPTH:
                    q.append((link, depth + 1))

    print(f"\n[DONE] Crawling finished. Total unique links: {len(visited)}")
    print(f"All discovered urls are in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
