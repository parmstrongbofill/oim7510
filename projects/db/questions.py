import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    from datetime import date

    # The one date the whole notebook uses as "today": the day I exported the data.
    as_of = date(2026, 11, 13)

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return as_of, ask, mo


@app.cell(hide_code=True)
def _(as_of, mo):
    mo.md(f"""
    # Questions — Nota al Margen

    All answers use the data as of **{as_of:%d %B %Y}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading It Back

    **The question I picked:** business question 6, *for each guest, how many episodes they joined, the total plays of those episodes and the books discussed.* It uses four tables: `guests`, `episode_guests`, `episodes` and `books`.

    **My prediction, written before running anything:** the join will have **11 rows before grouping**.

    **Why:** `episode_guests` has 11 rows, and each row is one guest in one episode. Joining it to `guests` adds one guest to each row, joining it to `episodes` adds one episode to each row, and joining it to `books` with a `LEFT JOIN` adds at most one book to each row (an episode has one book or none). No join can add a second match to a row, so the number of rows stays at 11. After grouping by guest I expect one row per guest who appears in an episode.
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT g.name, e.episode_id, b.title AS book
    FROM guests g
    JOIN episode_guests eg ON eg.guest_id = g.guest_id
    JOIN episodes e ON e.episode_id = eg.episode_id
    LEFT JOIN books b ON b.book_id = e.book_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The join has 11 rows before grouping, as I predicted
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT g.name,
           count(DISTINCT e.episode_id) AS episodes,
           sum(e.audience_total) AS plays,
           string_agg(b.title, '; ') AS books
    FROM guests g
    JOIN episode_guests eg ON eg.guest_id = g.guest_id
    JOIN episodes e ON e.episode_id = eg.episode_id
    LEFT JOIN books b ON b.book_id = e.book_id
    GROUP BY g.guest_id, g.name
    ORDER BY plays DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Romina Pistolas brings the most plays with 2 episodes
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. In which month did total plays grow the most compared with the month before?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT date_trunc('month', stat_date)::DATE AS month,
           sum(plays) AS plays
    FROM platform_daily_stats
    GROUP BY month
    ORDER BY month
    """)
    return


@app.cell
def _(ask):
    ask("""
    WITH m AS (
        SELECT date_trunc('month', stat_date)::DATE AS month,
               sum(plays) AS plays
        FROM platform_daily_stats
        GROUP BY 1
    )
    SELECT month,
           plays,
           plays - lag(plays) OVER (ORDER BY month) AS growth
    FROM m
    ORDER BY month
    """)
    return


@app.cell
def _(ask):
    ask("""
    WITH m AS (
        SELECT date_trunc('month', stat_date)::DATE AS month,
               sum(plays) AS plays
        FROM platform_daily_stats
        WHERE stat_date < DATE '2026-11-01'
        GROUP BY 1
    )
    SELECT month,
           plays,
           plays - lag(plays) OVER (ORDER BY month) AS growth
    FROM m
    ORDER BY growth DESC NULLS LAST
    LIMIT 5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    March 2026 grew the most: 4,392 plays, which is 2,505 more than February. November is left out because it is not finished.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Do episodes with a guest average more plays than episodes without one?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT guests > 0 AS has_guest,
           count(*) AS episodes,
           round(avg(plays_total)) AS avg_plays
    FROM episode_summary
    GROUP BY has_guest
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Do episodes about a book average more plays than episodes that are not about a book?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT book_id IS NOT NULL AS about_a_book,
           count(*) AS episodes,
           round(avg(plays_total)) AS avg_plays
    FROM episodes
    GROUP BY book_id IS NOT NULL
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There is no real difference: the 49 episodes about a book average 964 plays and the 14 that are not average 972
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #What is the average number of plays by episode length?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT CASE WHEN duration_seconds < 2700 THEN '1. under 45 min'
                WHEN duration_seconds <= 3300 THEN '2. 45 to 55 min'
                ELSE '3. over 55 min' END AS length,
           count(*) AS episodes,
           round(avg(plays_total)) AS avg_plays
    FROM episodes
    GROUP BY 1
    ORDER BY 1
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Longer episodes get more plays: the 15 episodes over 55 minutes average 1,240, while the 13 under 45 minutes average 716. Many long episodes have a guest, but they still do better without one
    """)
    return


if __name__ == "__main__":
    app.run()
