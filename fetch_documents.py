"""
fetch_documents.py
------------------
Fetches raw text from each source URL and saves it as a .txt file in documents/.
Run once before building the pipeline. URLs that block scraping are flagged so
you can copy-paste the text manually.

Usage:
    python fetch_documents.py
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup

DOCUMENTS_DIR = "documents"

SOURCES = [
    ("01_uf_offcampus_housing.txt",       "https://offcampus.ufl.edu/resources/off-campus-housing/"),
    ("02_offcampus_universe_guide.txt",   "https://www.offcampus-universe.com/post/student-apartments-gainesville-fl-where-to-live-off-campus-at-uf"),
    ("03_sweetwater_best_apartments.txt", "https://sweetwatergainesville.com/resources/best-student-apartments-uf-gainesville/"),
    ("04_sweetwater_freshman_guide.txt",  "https://sweetwatergainesville.com/resources/freshman-uf-housing/"),
    ("05_prked_ultimate_guide.txt",       "https://prked.com/post/the-ultimate-university-of-florida-off-campus-housing-guide"),
    ("06_offcampus_universe_guide2.txt",  "https://www.offcampus-universe.com/post/uf-off-campus-housing-guide-for-students-in-gainesville"),
    ("07_swamprentals_bus_routes.txt",    "https://www.swamprentals.com/uf-parent-guide/apartments-in-gainesville-on-bus-route"),
    ("08_uf_taps_transportation.txt",     "https://offcampus.ufl.edu/resources/transportation/"),
    ("09_apartmentratings_gainesville_place.txt", "https://www.apartmentratings.com/fl/gainesville/gainesville-place-apartments_352271313132608/"),
    ("10_yelp_student_apartments.txt",    "https://www.yelp.com/search?find_desc=Student+Apartments&find_loc=Gainesville,+FL"),
    ("11_yelp_uf_apartments.txt",         "https://www.yelp.com/search?find_desc=Uf+Apartments&find_loc=Gainesville%2C+FL"),
    ("12_forrentuniversity_uf.txt",       "https://www.forrentuniversity.com/University-of-Florida"),
    ("13_quora_gainesville_areas.txt",    "https://www.quora.com/What-areas-of-Gainsville-are-the-most-pleasant-to-live-for-a-UF-student"),
    ("14_uf_phhp_living.txt",             "https://phhp.ufl.edu/admissions/living-in-gainesville/"),
    ("15_stoneridge_apartments.txt",      "https://www.stoneridgegainesville.com/"),
    ("16_centric_on_34th.txt",            "https://centricaptsgainesville.com/"),
    ("17_the_quarters.txt",               "https://thequartersgainesville.com/"),
    ("18_greenwich_green.txt",            "https://www.greenwichgreen.net/"),
]

# Tags whose entire subtree we discard before extracting text
JUNK_TAGS = [
    "script", "style", "noscript", "header", "footer", "nav",
    "aside", "form", "iframe", "svg", "button", "figure",
    "[document]", "meta", "link",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Sites known to block automated requests — will be skipped and flagged
MANUAL_SITES = {"yelp.com", "quora.com"}


def needs_manual(url: str) -> bool:
    return any(domain in url for domain in MANUAL_SITES)


def fetch_and_clean(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(JUNK_TAGS):
        tag.decompose()

    # Prefer main content containers if present
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"(content|main|body)", re.I))
        or soup.find(class_=re.compile(r"(content|main|body|post|entry)", re.I))
        or soup.body
    )
    raw = (main or soup).get_text(separator="\n")

    # Collapse whitespace: remove lines that are pure whitespace, compress blanks
    lines = [ln.strip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln]
    # Drop very short lines that are nav/button remnants (< 4 chars)
    lines = [ln for ln in lines if len(ln) >= 4]
    # Collapse 3+ consecutive blank lines to one blank line
    cleaned_lines = []
    blank_run = 0
    for ln in lines:
        if ln == "":
            blank_run += 1
            if blank_run <= 1:
                cleaned_lines.append(ln)
        else:
            blank_run = 0
            cleaned_lines.append(ln)

    return "\n".join(cleaned_lines)


def main():
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    manual_needed = []
    succeeded = []
    failed = []

    for filename, url in SOURCES:
        out_path = os.path.join(DOCUMENTS_DIR, filename)

        # Skip if already fetched
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            print(f"  [skip]  {filename}  (already exists)")
            succeeded.append(filename)
            continue

        if needs_manual(url):
            print(f"  [manual] {filename}  — {url}")
            manual_needed.append((filename, url))
            continue

        try:
            print(f"  [fetch]  {filename} ...", end=" ", flush=True)
            text = fetch_and_clean(url)
            if len(text) < 200:
                raise ValueError(f"Too little text extracted ({len(text)} chars) — likely blocked or JS-rendered")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"SOURCE: {url}\n\n")
                f.write(text)
            print(f"OK  ({len(text):,} chars)")
            succeeded.append(filename)
        except Exception as e:
            print(f"FAILED — {e}")
            failed.append((filename, url, str(e)))

        time.sleep(1)  # be polite

    print("\n" + "=" * 60)
    print(f"Done. {len(succeeded)} succeeded, {len(failed)} failed, {len(manual_needed)} need manual copy.")

    if manual_needed:
        print("\n--- MANUAL COPY NEEDED ---")
        print("These sites block automated scraping (Yelp, Quora).")
        print("Open each URL in a browser, select all the review/answer text,")
        print("and paste it into the corresponding file in documents/.\n")
        for fname, url in manual_needed:
            print(f"  documents/{fname}")
            print(f"    {url}\n")

    if failed:
        print("\n--- FAILED FETCHES ---")
        print("These may be JS-rendered or rate-limited. Try opening in a")
        print("browser and copying the text manually.\n")
        for fname, url, err in failed:
            print(f"  documents/{fname}")
            print(f"    {url}")
            print(f"    Error: {err}\n")


if __name__ == "__main__":
    main()
