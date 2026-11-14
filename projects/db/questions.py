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

    return as_of, ask, mo, pl


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
    ## 4. What is the average number of plays by episode length?
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Which day of the week has the most plays on average?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT dayname(stat_date) AS weekday,
           round(avg(day_plays), 1) AS avg_daily_plays
    FROM (
        SELECT stat_date, sum(plays) AS day_plays
        FROM platform_daily_stats
        WHERE stat_date >= (SELECT min(publish_date) FROM episodes)
          AND stat_date < DATE '2026-11-01'
        GROUP BY stat_date
    )
    GROUP BY weekday
    ORDER BY 2 DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Wednesday is the strongest day with 215 plays on average, the day after the Tuesday release.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. For each guest: how many episodes, the plays of those episodes, and the books discussed
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT g.name,
           count(DISTINCT e.episode_id) AS episodes,
           sum(e.plays_total) AS plays,
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
    Romina Pistolas brings the most plays: 3,286 in 2 episodes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Which episodes did not come out on a Tuesday? (checks a rule)
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT episode_id, title, publish_date, dayname(publish_date) AS weekday
    FROM episodes
    WHERE dayname(publish_date) <> 'Tuesday'
    ORDER BY episode_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exactly 2 of 63 episodes break the rule: episode 35, published on a Monday, and episode 51, published on a Wednesday
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Which episode has the best share of audience over plays?
    """)
    return


@app.cell
def _(ask):
    ask("""
    SELECT e.episode_id, e.title, e.plays_total, e.audience_total,
           round(e.audience_total * 1.0 / e.plays_total, 3) AS audience_share,
           b.title AS book, g.name AS guest
    FROM episodes e
    LEFT JOIN books b ON b.book_id = e.book_id
    LEFT JOIN episode_guests eg ON eg.episode_id = e.episode_id
    LEFT JOIN guests g ON g.guest_id = eg.guest_id
    ORDER BY audience_share DESC
    LIMIT 5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How I Know These Numbers Are Right
    """)
    return


@app.cell
def _(mo, pl):
    _episodes = pl.read_csv(mo.notebook_dir() / "data" / "episodes.csv")
    _with_book = _episodes.filter(pl.col("book_id").is_not_null())
    _without_book = _episodes.filter(pl.col("book_id").is_null())

    mo.md(
        f"With a book: {_with_book.height} episodes, average {_with_book['plays_total'].mean():,.0f} plays. "
        f"Without a book: {_without_book.height} episodes, average {_without_book['plays_total'].mean():,.0f} plays."
    )
    return


@app.cell
def _(mo, pl):
    _ep = pl.read_csv(mo.notebook_dir() / "data" / "episodes.csv", try_parse_dates=True)
    _not_tuesday = _ep.filter(pl.col("publish_date").dt.weekday() != 2)

    _not_tuesday.select("episode_id", "title", "publish_date")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I checked two answers a second way, with polars on the CSV files in `data/`. For question 3, the CSV gives 49 episodes about a book (average 964 plays) and 14 that are not (average 972), the same as SQL. For question 7, the CSV gives the same two episodes that did not come out on a Tuesday: 35 and 51.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I used the agent to help me build the tables and write the SQL. I told it my goal: to understand where the podcast can grow, and to analyze strategically the results for guests and for series, which are the episodes that are not about a book. The agent explained each query in small steps with blanks for me to fill in, and I typed the code myself in marimo. Along the way I also caught my own errors, such as using `audience_total` instead of `plays_total`, and I fixed them by running the cells in marimo and reading the results. What I learned is how to combine data from several tables with joins.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Going Further
    """)
    return


@app.cell
def _(ask):
    _year = ask("""
    SELECT date_trunc('month', stat_date)::DATE AS month,
           sum(plays)::BIGINT AS plays
    FROM platform_daily_stats
    WHERE stat_date >= DATE '2025-08-01'
      AND stat_date < DATE '2026-09-01'
    GROUP BY 1
    ORDER BY 1
    """)
    _year.plot.line(x="month", y="plays").properties(title="Monthly plays, August 2025 to August 2026")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In one year the show grew from 2,018 plays in August 2025 to 5,674 in August 2026, an increase of 181%. The growth was not steady: plays fell in February 2026, when no episode came out for five weeks, and then jumped in March, the month with the biggest growth. The lesson for strategy is that publishing every week matters, and that guests and longer episodes (see questions 2 and 4) are where I can grow next.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Time Spent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    About 6 hours in total, between Part A (the README, the data and `build.py`) and Part B (this notebook).
    """)
    return


if __name__ == "__main__":
    app.run()
