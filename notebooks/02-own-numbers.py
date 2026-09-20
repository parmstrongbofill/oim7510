import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How many downloads did each episode of Nota al Margen get, and what was the average per episode?
    """)
    return


@app.cell
def _():
    downloads = [1589, 1431, 1015, 2412, 1326, 915]
    episodes = [
        "1. MOMFLUENCERS: Los Reyes de la Casa",
        "2. Todo sobre el caso Giséle Pelicot",
        "3. Memorias de una Millennial",
        "4. Romina Pistolas: escritora, stripper y sensación en TikTok",
        "5. Tu thriller favorito: La paciente silenciosa",
        "6. Madres, hijas y otras rivalidades: Golpéate el corazón",
    ] 
    total_downloads = sum(downloads)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The first value in `downloads` (1589) is the download count for episode 1, MOMFLUENCERS.
    """)
    return


@app.cell
def _():
    downloads_raw = [1589, 1431, "n/a", 2419, 1326, 915]
    return (downloads_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This error means Python tried to add a number and a piece of text together, and it doesn't know how to combine those two types — that's why it stopped at 'n/a' instead of finishing the sum
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If an episode is missing its download count, I exclude it from the total and the average instead of making up a number.
    """)
    return


@app.cell
def _(downloads_raw):
    downloads_clean = []
    for dl_value in downloads_raw:
        if isinstance(dl_value, (int, float)):
            downloads_clean.append(dl_value)
    return (downloads_clean,)


@app.cell
def _(downloads_clean):
    total = sum(downloads_clean)
    average = total / len(downloads_clean)
    print(f"Nota al Margen had {total} downloads across {len(downloads_clean)} episodes with valid data, averaging {average:.2f} downloads per episode.")
    return (total,)


@app.cell
def _(downloads_clean, total):
    check_total = 0
    for check_value in downloads_clean:
        check_total += check_value
    check_total == total
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
