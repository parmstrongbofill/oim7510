"""Writes the CSV files for the Nota al Margen database into projects/db/data/.

Run it with:  uv run projects/db/make_data.py
It uses a fixed random seed, so it writes the same files every time.
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

AS_OF = date(2026, 11, 1)          # the as_of date used in Part B
FIRST_WEEK = date(2025, 11, 3)     # a Monday; the 12 months before AS_OF start here
N_PUBLISHED = 52                   # one episode a week
N_SCHEDULED = 2
N_DRAFT = 1

# On purpose: two published episodes with no row in episode_platform_stats.
# They break the rule "a published episode is live on at least one platform".
BROKEN_RULE_EPISODES = {19, 41}


def write_csv(name, header, rows):
    with open(DATA_DIR / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")


def isbn13(n):
    """A synthetic ISBN-13 (not a real book's ISBN) with a valid check digit."""
    digits = [9, 7, 8] + [int(c) for c in f"{n:09d}"]
    total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    return "".join(map(str, digits)) + str((10 - total % 10) % 10)


# ---------------------------------------------------------------- books
# title, author, pages (approximate, at most 300), year first published.
# Pages and years are approximate: check them if they matter.
BOOKS = [
    ("Pedro Páramo", "Juan Rulfo", 140, 1955),
    ("El llano en llamas", "Juan Rulfo", 150, 1953),
    ("Crónica de una muerte anunciada", "Gabriel García Márquez", 120, 1981),
    ("El coronel no tiene quien le escriba", "Gabriel García Márquez", 100, 1961),
    ("La metamorfosis", "Franz Kafka", 100, 1915),
    ("El extranjero", "Albert Camus", 130, 1942),
    ("La caída", "Albert Camus", 150, 1956),
    ("Ficciones", "Jorge Luis Borges", 200, 1944),
    ("El Aleph", "Jorge Luis Borges", 190, 1949),
    ("El libro de arena", "Jorge Luis Borges", 150, 1975),
    ("Bestiario", "Julio Cortázar", 150, 1951),
    ("La hora de la estrella", "Clarice Lispector", 90, 1977),
    ("Agua viva", "Clarice Lispector", 100, 1973),
    ("El túnel", "Ernesto Sabato", 160, 1948),
    ("La tregua", "Mario Benedetti", 190, 1960),
    ("Montevideanos", "Mario Benedetti", 150, 1959),
    ("Aura", "Carlos Fuentes", 80, 1962),
    ("Los de abajo", "Mariano Azuela", 150, 1915),
    ("Cartas a un joven poeta", "Rainer Maria Rilke", 100, 1929),
    ("La casa de Bernarda Alba", "Federico García Lorca", 100, 1936),
    ("Bodas de sangre", "Federico García Lorca", 90, 1933),
    ("La invención de Morel", "Adolfo Bioy Casares", 120, 1940),
    ("Platero y yo", "Juan Ramón Jiménez", 150, 1914),
    ("La amortajada", "María Luisa Bombal", 120, 1938),
    ("La última niebla", "María Luisa Bombal", 100, 1935),
    ("La plaza del Diamante", "Mercè Rodoreda", 240, 1962),
    ("Distancia de rescate", "Samanta Schweblin", 120, 2014),
    ("Los peligros de fumar en la cama", "Mariana Enriquez", 200, 2009),
    ("Temporada de huracanes", "Fernanda Melchor", 200, 2017),
    ("El cuerpo en que nací", "Guadalupe Nettel", 200, 2011),
    ("Formas de volver a casa", "Alejandro Zambra", 150, 2011),
    ("Bonsái", "Alejandro Zambra", 100, 2006),
    ("Estrella distante", "Roberto Bolaño", 150, 1996),
    ("Los adioses", "Juan Carlos Onetti", 100, 1954),
    ("Cuentos de amor de locura y de muerte", "Horacio Quiroga", 200, 1917),
    ("El principito", "Antoine de Saint-Exupéry", 100, 1943),
    ("Rebelión en la granja", "George Orwell", 120, 1945),
    ("Un cuarto propio", "Virginia Woolf", 120, 1929),
    ("Todos deberíamos ser feministas", "Chimamanda Ngozi Adichie", 60, 2014),
    ("La campana de cristal", "Sylvia Plath", 270, 1963),
    ("Las malas", "Camila Sosa Villada", 200, 2019),
    ("La virgen de los sicarios", "Fernando Vallejo", 130, 1994),
    ("La oveja negra y demás fábulas", "Augusto Monterroso", 90, 1969),
    ("El libro de los abrazos", "Eduardo Galeano", 280, 1989),
    ("La condesa sangrienta", "Alejandra Pizarnik", 60, 1971),
    ("Cometierra", "Dolores Reyes", 200, 2019),
    ("Nadie nada nunca", "Juan José Saer", 200, 1980),
    ("La señorita Elsa", "Stefan Zweig", 100, 1924),
    ("Carta a una desconocida", "Stefan Zweig", 80, 1922),
    ("Una habitación en Babel", "Natalia Ginzburg", 150, 1963),
    ("Léxico familiar", "Natalia Ginzburg", 220, 1963),
]
assert len({b[0] for b in BOOKS}) == len(BOOKS)

books_rows = []
for i, (title, author, pages, year) in enumerate(BOOKS):
    books_rows.append([isbn13(100000 + i * 7919), title, author, pages, year])
write_csv("books", ["isbn", "title", "author", "pages", "pub_year"], books_rows)

# ---------------------------------------------------------------- guests
GUESTS = [
    ("Camila", "Rojas", "Editora independiente y lectora voraz", "camila.rojas@example.com"),
    ("Tomás", "Herrera", "Profesor de literatura latinoamericana", "tomas.herrera@example.com"),
    ("Valentina", "Sosa", "Traductora literaria", "valentina.sosa@example.com"),
    ("Andrés", "Pizarro", "Crítico y columnista cultural", None),
    ("Lucía", "Fernández", "Escritora de cuentos", "lucia.fernandez@example.com"),
    ("Martín", "Echeverría", "Librero", None),
    ("Daniela", "Cortés", "Booktuber", "daniela.cortes@example.com"),
    ("Joaquín", "Bravo", "Bibliotecario", None),
    ("Renata", "Molina", "Periodista cultural", "renata.molina@example.com"),
    # Invited, but has not appeared in any episode yet:
    ("Ignacio", "Salas", "Poeta", "ignacio.salas@example.com"),
]
guests_rows = [[i + 1, g[0], g[1], g[2], g[3] or ""] for i, g in enumerate(GUESTS)]
write_csv("guests", ["guest_id", "first_name", "last_name", "bio", "contact_email"], guests_rows)
GUEST_IDS_THAT_APPEAR = [g[0] for g in guests_rows[:-1]]

# ---------------------------------------------------------------- platforms
PLATFORMS = ["Spotify", "Apple Podcasts", "YouTube"]
write_csv("platforms", ["name"], [[p] for p in PLATFORMS])

# ---------------------------------------------------------------- episodes
n_episodes = N_PUBLISHED + N_SCHEDULED + N_DRAFT
n_distinct = n_episodes - 10          # 10 books get a second part
book_order = list(range(len(BOOKS)))
random.shuffle(book_order)
used_books = book_order[:n_distinct]  # the rest are books never discussed
second_part = set(random.sample(range(n_distinct), 10))

episode_books = []  # (book index, part)
for k, b in enumerate(used_books):
    episode_books.append((b, 1))
    if k in second_part:
        episode_books.append((b, 2))
# a part 2 should come right after its part 1 and the list is already in that order
episode_books = episode_books[:n_episodes]

weekday_weights = [2, 1, 3, 4, 3, 1, 2]  # Mon..Sun: Thursday is most common
episodes_rows = []
episode_info = {}  # episode_number -> dict used to make listens
for n in range(1, n_episodes + 1):
    book_index, part = episode_books[n - 1]
    book = BOOKS[book_index]
    week_start = FIRST_WEEK + timedelta(weeks=n - 1)
    offset = random.choices(range(7), weights=weekday_weights)[0]
    release = week_start + timedelta(days=offset)
    if n <= N_PUBLISHED:
        status = "published"
        assert release <= AS_OF
    elif n <= N_PUBLISHED + N_SCHEDULED:
        status = "scheduled"
        assert release > AS_OF
    else:
        status = "draft"
        assert release > AS_OF
    duration = int(min(85, max(22, random.gauss(46, 12))))
    title = book[0] if part == 1 else f"{book[0]} (parte 2)"
    isbn = books_rows[book_index][0]
    episodes_rows.append([n, title, isbn, release.isoformat(), duration, status])
    episode_info[n] = {"release": release, "duration": duration, "status": status,
                       "author": book[1]}
write_csv("episodes",
          ["episode_number", "title", "isbn", "release_date", "duration_minutes", "status"],
          episodes_rows)

# ---------------------------------------------------------------- episode_guests
# About a third of the published episodes have one guest, a few have two.
ROLES = ["author", "translator", "critic", "reader"]
guest_rows = []
for n in range(1, N_PUBLISHED + 1):
    if random.random() < 0.35:
        n_guests = 2 if random.random() < 0.15 else 1
        for gid in random.sample(GUEST_IDS_THAT_APPEAR, n_guests):
            guest_rows.append([n, gid, random.choice(ROLES)])
            episode_info[n]["has_guest"] = True
write_csv("episode_guests", ["episode_number", "guest_id", "role"], guest_rows)

# ---------------------------------------------------------------- episode_platform_stats
# One snapshot per episode, per platform, every 7 days from the release date
# (day 0, 7, 14, ... up to 70 days), never after AS_OF.
# listens_cumulative and ad_revenue_dollars are running totals: they never go down.
SHARE = {"Spotify": 0.55, "Apple Podcasts": 0.28, "YouTube": 0.17}
REVENUE_PER_1000 = {"Spotify": 12.0, "Apple Podcasts": 18.0, "YouTube": 6.0}
YOUTUBE_STARTS_AT_EPISODE = 10
WEEKDAY_EFFECT = [0.95, 0.90, 1.00, 1.10, 1.05, 0.90, 1.00]  # Mon..Sun
stats_rows = []
for n in range(1, N_PUBLISHED + 1):
    if n in BROKEN_RULE_EPISODES:
        continue
    info = episode_info[n]
    base = 420 + 6 * n                                  # the show grows over the year
    base *= 1.18 if info.get("has_guest") else 1.0      # guests help a little
    base *= WEEKDAY_EFFECT[info["release"].weekday()]
    base *= math.exp(-((info["duration"] - 45) / 40) ** 2 * 0.4)  # a sweet spot near 45 min
    base *= random.lognormvariate(0, 0.15)
    for platform in PLATFORMS:
        if platform == "YouTube" and n < YOUTUBE_STARTS_AT_EPISODE:
            continue
        final = base * SHARE[platform] * random.uniform(0.9, 1.1)
        rate = REVENUE_PER_1000[platform] * random.uniform(0.85, 1.15)
        for k in range(0, 11):
            stat_date = info["release"] + timedelta(days=7 * k)
            if stat_date > AS_OF:
                break
            days = 7 * k
            listens = int(final * (1 - math.exp(-(days + 1) / 21)))
            revenue = round(listens / 1000 * rate, 2)
            stats_rows.append([n, platform, stat_date.isoformat(), listens, f"{revenue:.2f}"])
write_csv("episode_platform_stats",
          ["episode_number", "platform", "stat_date", "listens_cumulative", "ad_revenue_dollars"],
          stats_rows)

print()
print(f"Rows that record what happens: {len(stats_rows) + len(guest_rows)}")
print("Published episodes with no row in episode_platform_stats, on purpose:",
      sorted(BROKEN_RULE_EPISODES))
print("Books never discussed:",
      [BOOKS[i][0] for i in book_order[n_distinct:]])
