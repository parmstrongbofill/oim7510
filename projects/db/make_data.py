"""Cleans the real Nota al Margen files in data/raw/ into the CSV files in data/.

Run it with:  python projects/db/make_data.py
Inputs (data/raw/):
  spotify_episodes_raw.txt   episode list copied from Spotify for Creators (";" separated)
  books_draft.csv            book, author and Buchalibre Chile price for each episode that has a book
  daily_performance.csv      the daily export from Spotify for Creators
Nothing here is random: the same inputs always give the same files.
"""

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
OUT = HERE / "data"

# Spotify numbers its episodes only until 26, so we number them ourselves,
# 1, 2, 3 ... in publish order. Spotify's first item is the trailer ("n" = 1 in the
# raw file); it is not an episode, so the first real episode gets episode_id 1.
FIRST_REAL_N = 2

# Who appeared in which episode ("n" is the number used in the raw files).
GUESTS_BY_N = {
    5: ["Romina Pistolas"],
    8: ["Andrés Montero"],
    10: ["Josefa Cortés"],
    13: ["Francisca Feuerhake"],
    17: ["La Nota del Libro"],
    23: ["Milagros Mir"],
    36: ["Andrea Hartung"],
    41: ["Francisca Alegría"],
    49: ["Valeria Luna"],
    58: ["Romina Pistolas"],
    62: ["Mónica Rincón"],
}

# A book discussed twice: the second episode points to the same book as the first one.
SAME_BOOK_AS = {51: 45}


def parse_date(text):
    day, month, year = (int(x) for x in text.split("/"))
    return date(year + 2000 if year < 100 else year, month, day)


def parse_seconds(text):
    parts = [int(x) for x in text.split(":")]
    if len(parts) == 2:
        parts = [0] + parts
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def write_csv(name, header, rows):
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


# ---------------------------------------------------------------- episodes
with open(RAW / "spotify_episodes_raw.txt", encoding="utf-8") as f:
    raw_rows = list(csv.DictReader(f, delimiter=";"))

merged = {}  # n -> dict. Spotify lists episode 13 twice: we add the two rows together.
for row in raw_rows:
    n = int(row["n"])
    if n < FIRST_REAL_N:
        continue
    title = row["title"].replace(" (FILA DUPLICADA)", "")
    plays, audience = int(row["plays"]), int(row["audience"])
    if n in merged:
        merged[n]["plays"] += plays
        merged[n]["audience"] += audience
    else:
        merged[n] = {"title": title, "date": parse_date(row["date"]),
                     "seconds": parse_seconds(row["length"]),
                     "plays": plays, "audience": audience}

episode_id = {n: n - FIRST_REAL_N + 1 for n in merged}

# ---------------------------------------------------------------- books
with open(RAW / "books_draft.csv", encoding="utf-8") as f:
    book_rows = list(csv.DictReader(f))
book_id_for_n = {}
books_out = []
for i, row in enumerate(book_rows, start=1):
    book_id_for_n[int(row["episodio"])] = i
    books_out.append([i, row["titulo"], row["autor"], row["precio_clp"]])
for later, first in SAME_BOOK_AS.items():
    book_id_for_n[later] = book_id_for_n[first]
write_csv("books", ["book_id", "title", "author", "price_clp"], books_out)

episodes_out = []
for n in sorted(merged):
    e = merged[n]
    episodes_out.append([episode_id[n], e["title"], e["date"].isoformat(), e["seconds"],
                         e["plays"], e["audience"], book_id_for_n.get(n, "")])
write_csv("episodes",
          ["episode_id", "title", "publish_date", "duration_seconds",
           "plays_total", "audience_total", "book_id"],
          episodes_out)

# ---------------------------------------------------------------- guests
names = []
for guests in GUESTS_BY_N.values():
    for g in guests:
        if g not in names:
            names.append(g)
guest_id = {g: i for i, g in enumerate(sorted(names), start=1)}
write_csv("guests", ["guest_id", "name"], [[guest_id[g], g] for g in sorted(names)])
eg_rows = [[episode_id[n], guest_id[g]] for n, gs in sorted(GUESTS_BY_N.items()) for g in gs]
write_csv("episode_guests", ["episode_id", "guest_id"], eg_rows)

# ---------------------------------------------------------------- platforms and daily stats
write_csv("platforms", ["platform_id", "name"], [[1, "Spotify"], [2, "Otras plataformas"]])

def number(text):
    return int(text) if text.strip() else 0   # the export leaves a day empty when it is 0

daily_out = []
with open(RAW / "daily_performance.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        day = parse_date(row["Fecha"]).isoformat()
        daily_out.append([day, 1, number(row["Reproducciones (en Spotify)"]),
                          number(row["Audiencia (en Spotify)"])])
        daily_out.append([day, 2, number(row["Descargas (en cualquier otra plataforma)"]),
                          number(row["Audiencia (en cualquier otra plataforma)"])])
write_csv("platform_daily_stats", ["stat_date", "platform_id", "plays", "audience"], daily_out)

# ---------------------------------------------------------------- quick checks
not_tuesday = [(episode_id[n], merged[n]["title"], merged[n]["date"].isoformat(),
                merged[n]["date"].strftime("%A")) for n in sorted(merged)
               if merged[n]["date"].weekday() != 1]
print()
print("Rows that record what happens:", len(daily_out) + len(eg_rows))
print("Episodes not published on a Tuesday:", not_tuesday)
print("Sum of plays in the episode list:", sum(e["plays"] for e in merged.values()))
print("Sum of daily plays (all days):", sum(r[2] for r in daily_out))
print("Books with no price:", sum(1 for b in books_out if not b[3]),
      "| with no author:", sum(1 for b in books_out if not b[2]))
