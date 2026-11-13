import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, database, duckdb, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Tables

    This notebook deletes `database.duckdb`, builds six tables and a view from the CSV files in `data/`, and loads them. Run it from the top and you get the same database every time.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    database.unlink(missing_ok=True)

    with duckdb.connect(database) as _con:
        _con.execute("""
            CREATE TABLE books (
                book_id    INTEGER PRIMARY KEY,
                title      VARCHAR NOT NULL,
                author     VARCHAR,
                price_clp  INTEGER CHECK (price_clp >= 0)
            )
        """)
        _con.execute("""
            CREATE TABLE guests (
                guest_id  INTEGER PRIMARY KEY,
                name      VARCHAR NOT NULL
            )
        """)
        _con.execute("""
            CREATE TABLE platforms (
                platform_id  INTEGER PRIMARY KEY,
                name         VARCHAR NOT NULL UNIQUE
            )
        """)
        _con.execute("""
            CREATE TABLE episodes (
                episode_id        INTEGER PRIMARY KEY,
                title             VARCHAR NOT NULL,
                publish_date      DATE NOT NULL,
                duration_seconds  INTEGER NOT NULL CHECK (duration_seconds > 0),
                plays_total       INTEGER NOT NULL CHECK (plays_total >= 0),
                audience_total    INTEGER NOT NULL CHECK (audience_total >= 0),
                book_id           INTEGER REFERENCES books(book_id)
            )
        """)
        _con.execute("""
            CREATE TABLE episode_guests (
                episode_id  INTEGER NOT NULL REFERENCES episodes(episode_id),
                guest_id    INTEGER NOT NULL REFERENCES guests(guest_id),
                PRIMARY KEY (episode_id, guest_id)
            )
        """)
        _con.execute("""
            CREATE TABLE platform_daily_stats (
                stat_date    DATE NOT NULL,
                platform_id  INTEGER NOT NULL REFERENCES platforms(platform_id),
                plays        INTEGER NOT NULL CHECK (plays >= 0),
                audience     INTEGER NOT NULL CHECK (audience >= 0),
                PRIMARY KEY (stat_date, platform_id)
            )
        """)
        _data = mo.notebook_dir() / "data"
        for _table in ["books", "guests", "platforms", "episodes", "episode_guests", "platform_daily_stats"]:
            _con.execute(f"INSERT INTO {_table} SELECT * FROM read_csv('{_data}/{_table}.csv', header=true, nullstr='')")
        _con.execute("""
            CREATE VIEW episode_summary AS
            SELECT e.episode_id, e.title, e.publish_date, dayname(e.publish_date) AS weekday,
                   round(e.duration_seconds / 60.0, 1) AS minutes,
                   e.plays_total, e.audience_total,
                   b.title AS book, b.author, b.price_clp,
                   count(eg.guest_id) AS guests
            FROM episodes e
            LEFT JOIN books b ON b.book_id = e.book_id
            LEFT JOIN episode_guests eg ON eg.episode_id = e.episode_id
            GROUP BY ALL
        """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'main' AND table_name NOT IN ('episode_summary')
    ORDER BY table_name, ordinal_position
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Data

    The data is real. It is the podcast *Nota al Margen*, as of 13 November 2026.

    - **Real:** the 63 episodes (title, publish date, length, plays and audience, copied from Spotify for Creators), and the 1,044 daily rows of plays and audience (522 days, 10 June 2025 to 13 November 2026, two platforms each).
    - **Added by me:** the book each episode discusses and its author (from my own episode plan), the price of each book in Chilean pesos from Buscalibre Chile (empty when I could not find a price), the guests (read from episode titles and my calendar), and the `episode_id` numbers. Spotify only numbered episodes up to 26, so I numbered all of them in publish order.
    - **Cleaned:** the trailer is left out because it is not an episode, and Spotify listed episode 13 twice, so I added the two rows into one.

    Two rows break the rule on purpose: episode 35 (*Mujeres asesinas con Andrea Hartung*, 27 April 2026, a Monday) and episode 51 (*Relaciones abiertas*, 19 August 2026, a Wednesday). The rule is "an episode comes out on Tuesday". It is real: these are the only two episodes that did not, and `CHECK` cannot hold it without refusing my own history.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Look at the Data
    """)
    return


@app.cell
def _(mo, pl):
    import altair as alt

    _raw = pl.read_csv(mo.notebook_dir() / "data" / "platform_daily_stats.csv", try_parse_dates=True)
    _spotify = _raw.filter(pl.col("platform_id") == 1)
    _chart = mo.ui.altair_chart(
        _spotify.plot.line(
            x=alt.X("stat_date", title="Day"),
            y=alt.Y("plays", title="Plays on Spotify that day"),
        ).properties(title="Daily plays on Spotify, 10 June 2025 to 13 November 2026")
    )
    mo.vstack([
        _chart,
        mo.md(
            "This looks like a real small podcast: plays climb from about 2,000 a month in August 2025 to over 5,000 a month "
            "by mid-2026, spike on the days after a Tuesday release, and dip in February 2026, when no episode came out between 27 January and 3 March."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Row Counts
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT 'books' AS table_name, count(*) AS n FROM books
    UNION ALL SELECT 'guests', count(*) FROM guests
    UNION ALL SELECT 'platforms', count(*) FROM platforms
    UNION ALL SELECT 'episodes', count(*) FROM episodes
    UNION ALL SELECT 'episode_guests', count(*) FROM episode_guests
    UNION ALL SELECT 'platform_daily_stats', count(*) FROM platform_daily_stats
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Row It Refuses

    A book with a negative price breaks the rule that a price is never below zero. The database should say no.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    with duckdb.connect(database) as _con:
        try:
            _con.execute("INSERT INTO books VALUES (9999, 'Libro de prueba', 'Autor de prueba', -5000)")
            _result = "The row was accepted (this should not happen)"
        except duckdb.Error as _e:
            _result = f"The database refused the row: {_e}"
    mo.md(_result)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Answers You Already Knew

    I know my own show, so I know three answers before asking. If the database agrees, the data loaded the way I meant it to.
    """)
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**How many episodes are there?** Expected: 63. Spotify lists 65 items, minus the trailer and minus the duplicated episode 13."),
        ask("SELECT count(*) AS episodes FROM episodes"),
    ])
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**Which book did I talk about in two episodes?** Expected: *El adversario*, by Emmanuel Carrère, in episodes 44 and 50."),
        ask("""
        SELECT b.title, b.author, list(e.episode_id ORDER BY e.episode_id) AS episodes
        FROM books b JOIN episodes e ON e.book_id = b.book_id
        GROUP BY b.book_id, b.title, b.author
        HAVING count(*) > 1
        """),
    ])
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**Which episodes did not come out on a Tuesday?** Expected: episodes 35 and 51, the two rows that break the rule on purpose."),
        ask("""
        SELECT episode_id, title, publish_date, dayname(publish_date) AS weekday
        FROM episodes
        WHERE dayname(publish_date) <> 'Tuesday'
        ORDER BY episode_id
        """),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A View

    `episode_summary` keeps one row per episode with its book, author, price, weekday and number of guests, so a question about episodes does not need to join three tables every time.
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT episode_id, title, weekday, minutes, plays_total, book, author, guests
    FROM episode_summary
    ORDER BY plays_total DESC
    LIMIT 5
    """)
    return


if __name__ == "__main__":
    app.run()
