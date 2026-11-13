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

    return ask, database, duckdb, mo


@app.cell
def _(database, duckdb, mo):
    database.unlink(missing_ok=True)

    with duckdb.connect(database) as _con:
        _con.execute("""
            CREATE TABLE books (
                isbn      VARCHAR PRIMARY KEY,
                title     VARCHAR NOT NULL,
                author    VARCHAR NOT NULL,
                pages     INTEGER NOT NULL CHECK (pages > 0 AND pages <= 300),
                pub_year  INTEGER
            )
        """)
        _con.execute("""
            CREATE TABLE guests (
                guest_id       INTEGER PRIMARY KEY,
                first_name     VARCHAR NOT NULL,
                last_name      VARCHAR NOT NULL,
                bio            VARCHAR,
                contact_email  VARCHAR
            )
        """)
        _con.execute("""
            CREATE TABLE platforms (
                name VARCHAR PRIMARY KEY
            )
        """)
        _con.execute("""
            CREATE TABLE episodes (
                episode_number    INTEGER PRIMARY KEY,
                title             VARCHAR NOT NULL,
                isbn              VARCHAR NOT NULL REFERENCES books(isbn),
                release_date      DATE NOT NULL,
                duration_minutes  INTEGER NOT NULL CHECK (duration_minutes > 0),
                status            VARCHAR NOT NULL CHECK (status IN ('draft', 'scheduled', 'published'))
            )
        """)
        _con.execute("""
            CREATE TABLE episode_guests (
                episode_number  INTEGER NOT NULL REFERENCES episodes(episode_number),
                guest_id        INTEGER NOT NULL REFERENCES guests(guest_id),
                role            VARCHAR,
                PRIMARY KEY (episode_number, guest_id)
            )
        """)
        _con.execute("""
            CREATE TABLE episode_platform_stats (
                episode_number      INTEGER NOT NULL REFERENCES episodes(episode_number),
                platform            VARCHAR NOT NULL REFERENCES platforms(name),
                stat_date           DATE NOT NULL,
                listens_cumulative  INTEGER NOT NULL CHECK (listens_cumulative >= 0),
                ad_revenue_dollars  DECIMAL(10, 2) NOT NULL CHECK (ad_revenue_dollars >= 0),
                PRIMARY KEY (episode_number, platform, stat_date)
            )
        """)
        _data = mo.notebook_dir() / "data"
        for _table in ["books", "guests", "platforms", "episodes", "episode_guests", "episode_platform_stats"]:
            _con.execute(f"INSERT INTO {_table} SELECT * FROM read_csv('{_data}/{_table}.csv', header=true, nullstr='')")
        _con.execute("""
            CREATE VIEW episode_latest AS
            SELECT e.episode_number, e.title, e.release_date, e.status, e.duration_minutes,
                   b.author,
                   count(s.platform) AS platforms_live,
                   coalesce(sum(s.listens_cumulative), 0) AS listens,
                   coalesce(sum(s.ad_revenue_dollars), 0) AS ad_revenue
            FROM episodes e
            JOIN books b ON b.isbn = e.isbn
            LEFT JOIN (
                SELECT * FROM episode_platform_stats
                QUALIFY row_number() OVER (PARTITION BY episode_number, platform ORDER BY stat_date DESC) = 1
            ) s ON s.episode_number = e.episode_number
            GROUP BY ALL
        """)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Look at the Data
    """)
    return


@app.cell
def _(ask, mo):
    import altair as alt

    _data = ask("""
    SELECT episode_number, title, listens
    FROM episode_latest
    WHERE status = 'published' AND platforms_live > 0
    ORDER BY episode_number
    """)
    _chart = mo.ui.altair_chart(
        _data.plot.line(
            x=alt.X("episode_number", title="Episode number"),
            y=alt.Y("listens", title="Listens so far, all platforms"),
        ).properties(title="Listens so far for each published episode")
    )
    _top = _data.sort("listens", descending=True).row(0, named=True)
    mo.vstack([
        _chart,
        mo.md(
            f"Episode {_top['episode_number']}, *{_top['title']}*, has the most listens so far "
            f"({_top['listens']:,}); the newest episodes sit lower only because they have had less time to collect listens."
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
    UNION ALL SELECT 'episode_platform_stats', count(*) FROM episode_platform_stats
    """)
    return



@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Row It Refuses

    A book of 450 pages breaks the rule that a book is never more than 300 pages. The database should say no.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    with duckdb.connect(database) as _con:
        try:
            _con.execute("INSERT INTO books VALUES ('9780000000000', 'Libro muy largo', 'Autor de prueba', 450, 2020)")
            _result = "The row was accepted (this should not happen)"
        except duckdb.Error as _e:
            _result = f"The database refused the row: {_e}"
    mo.md(_result)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Answers You Already Knew

    I wrote `make_data.py`, so I know three answers before asking. If the database agrees, the data loaded the way I meant it to.
    """)
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**How many episodes are published?** Expected: 52, because `make_data.py` writes 52 published episodes."),
        ask("SELECT count(*) AS published_episodes FROM episodes WHERE status = 'published'"),
    ])
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**Which guests never appeared in an episode?** Expected: Ignacio Salas, the one guest I invited but have not yet recorded."),
        ask("""
        SELECT first_name, last_name
        FROM guests
        WHERE guest_id NOT IN (SELECT guest_id FROM episode_guests)
        """),
    ])
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("**Which published episodes have no stats at all?** Expected: episodes 19 and 41, the two rows that break the rule on purpose."),
        ask("""
        SELECT episode_number, title
        FROM episodes
        WHERE status = 'published'
          AND episode_number NOT IN (SELECT episode_number FROM episode_platform_stats)
        ORDER BY episode_number
        """),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A View

    `episode_latest` keeps one row per episode with its latest listens and ad revenue added up across platforms, so a question about episodes does not need to join and filter three tables every time.
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT episode_number, title, author, platforms_live, listens, ad_revenue
    FROM episode_latest
    ORDER BY listens DESC
    LIMIT 5
    """)
    return



if __name__ == "__main__":
    app.run()
