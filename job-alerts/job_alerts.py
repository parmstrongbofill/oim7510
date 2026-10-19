"""
Job alerts bot for Paula's job search.

Checks several companies' public job boards for postings matching her target
roles, and sends any new match to her Telegram:
  - Greenhouse: Hasbro, SharkNinja, Toast, DoorDash
  - Workable: Quantis
  - SmartRecruiters: Mattel
  - Workday: Lego

State (which job IDs have already been checked/alerted) is kept in
seen_jobs.json, next to this script, so the same posting is never sent twice.
This file is committed back to the repo by the GitHub Actions workflow after
every run.

To add another company later, write a fetch_<company>() function that
returns a list of dicts with keys: id, title, location, url, company —
then add it to the SOURCES list near the bottom of this file.
"""

import json
import os

import requests

# --- Keywords: role titles Paula is targeting -------------------------------
# Matching is case-insensitive substring matching against the job title.
KEYWORDS = [
    "mba internship",
    "mba intern",
    "sustainability analyst",
    "sustainability manager",
    "sustainability coordinator",
    "corporate sustainability strategy",
    "corporate responsibility",
    "csr manager",
    "csr analyst",
    "esg analyst",
    "esg manager",
    "social impact",
    "impact analyst",
    "corporate communications",
    "strategy and planning",
    "strategic planning",
    "corporate strategy",
    "business development",
    "global growth",
]

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_jobs.json")

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def matches_keywords(title):
    title_lower = title.lower()
    return any(kw in title_lower for kw in KEYWORDS)


def make_greenhouse_fetcher(board_token, company_name):
    """Factory for Greenhouse-hosted job boards. No auth needed.

    board_token is the path segment after /boards/ on the company's
    boards.greenhouse.io career page.
    """

    def fetch():
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("jobs", []):
            jobs.append(
                {
                    "id": str(job["id"]),
                    "title": job["title"],
                    "location": job.get("location", {}).get("name", ""),
                    "url": job["absolute_url"],
                    "company": company_name,
                }
            )
        return jobs

    return fetch


def make_workday_fetcher(tenant, shard, site, company_name):
    """Factory for Workday-hosted career sites. No auth needed — this calls
    the same JSON endpoint the career site's own search box uses.

    tenant/shard/site come from the company's myworkdayjobs.com URL:
    https://{tenant}.{shard}.myworkdayjobs.com/{site}
    """

    def fetch():
        base = f"https://{tenant}.{shard}.myworkdayjobs.com/{site}"
        api_url = f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"

        jobs = []
        offset = 0
        limit = 20  # Workday returns zero rows (no error) above 20
        while True:
            response = requests.post(
                api_url,
                json={"appliedFacets": {}, "limit": limit, "offset": offset, "searchText": ""},
                headers={"Accept-Language": "en-US"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            postings = data.get("jobPostings", [])
            for job in postings:
                external_path = job.get("externalPath", "")
                jobs.append(
                    {
                        "id": external_path or job["title"],
                        "title": job["title"],
                        "location": job.get("locationsText", ""),
                        "url": base + external_path,
                        "company": company_name,
                    }
                )

            offset += limit
            if offset >= data.get("total", 0) or not postings:
                break

        return jobs

    return fetch


def fetch_quantis_jobs():
    """Quantis's public Workable job board. No auth needed."""
    url = "https://apply.workable.com/api/v1/widget/accounts/quantis"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    jobs = []
    for job in data.get("jobs", []):
        job_id = str(job.get("id") or job.get("shortcode"))
        location = job.get("location", {}) or {}
        jobs.append(
            {
                "id": job_id,
                "title": job["title"],
                "location": location.get("location_str", ""),
                "url": job.get("url") or job.get("shortlink", ""),
                "company": "Quantis",
            }
        )
    return jobs


def fetch_mattel_jobs():
    """Mattel's public SmartRecruiters job board. No auth needed."""
    url = "https://api.smartrecruiters.com/v1/companies/mattelinc/postings"
    jobs = []
    offset = 0
    limit = 100
    while True:
        response = requests.get(url, params={"limit": limit, "offset": offset}, timeout=30)
        response.raise_for_status()
        data = response.json()

        for job in data.get("content", []):
            location = job.get("location", {}) or {}
            location_bits = [location.get("city"), location.get("region"), location.get("country")]
            location_str = ", ".join(b for b in location_bits if b)
            jobs.append(
                {
                    "id": str(job["id"]),
                    "title": job["name"],
                    "location": location_str,
                    "url": f"https://jobs.smartrecruiters.com/mattelinc/{job['id']}",
                    "company": "Mattel",
                }
            )

        offset += limit
        if offset >= data.get("totalFound", 0):
            break

    return jobs


# Add new companies here once connected: ("source_key", fetch_function)
SOURCES = [
    ("hasbro", make_greenhouse_fetcher("hasbro", "Hasbro")),
    ("sharkninja", make_greenhouse_fetcher("sharkninjaoperatingllc", "SharkNinja")),
    ("toast", make_greenhouse_fetcher("toast", "Toast")),
    ("doordash", make_greenhouse_fetcher("doordashusa", "DoorDash")),
    ("quantis", fetch_quantis_jobs),
    ("mattel", fetch_mattel_jobs),
    ("lego", make_workday_fetcher("lego", "wd103", "LEGO_External", "Lego")),
]


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    response.raise_for_status()


def main():
    state = load_state()
    new_matches = []

    for source_name, fetch_fn in SOURCES:
        try:
            jobs = fetch_fn()
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue

        seen_ids = set(state.get(source_name, []))
        for job in jobs:
            already_seen = job["id"] in seen_ids
            seen_ids.add(job["id"])
            if already_seen:
                continue
            if matches_keywords(job["title"]):
                new_matches.append(job)
        state[source_name] = sorted(seen_ids)

    if new_matches:
        for job in new_matches:
            text = (
                f"\U0001F514 New job match\n"
                f"{job['title']}\n"
                f"{job['company']} — {job['location']}\n"
                f"{job['url']}"
            )
            send_telegram_message(text)
        print(f"Sent {len(new_matches)} new job alert(s).")
    else:
        print("No new matching jobs this run.")

    save_state(state)


if __name__ == "__main__":
    main()
