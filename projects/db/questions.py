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


if __name__ == "__main__":
    app.run()
