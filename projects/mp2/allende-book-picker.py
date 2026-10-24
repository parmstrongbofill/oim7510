import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    My co-host and I run a literary podcast, and every week we have to choose the book we will discuss. We want a book that is well written, popular right now, and likely to spark conversation, by a well-known author, and short enough to read in a week (300 pages or fewer). Given a literary genre, this tool finds the best-known authors in it, looks at all their books, and picks the one with the best rating that is 300 pages or fewer, so we can choose the book for the next episode.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. I type a literary genre I’m interested in (for example, magical realism).
    2. I ask Open Library for the most-edited books in that genre.
    3. From the top 10 most-edited books, I keep their authors, without repeating anyone.
    4. For each author, I ask for all their books using the author’s key, with their rating, number of ratings and page count.
    5. If the API reports more books (numFound) than it sent, I ask for the next page until I have them all.
    6. I ignore books that are missing a rating or a page count.
    7. I keep only books with 300 pages or fewer.
    8. I keep only books with an average rating of 4 or more, from at least 10 ratings.
    9. I sort the remaining books by rating, best first.
    10. I show the best book in a table and one sentence for the week’s episode.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Functions**
    - get_genre_authors(genre, top_n): takes a genre and how many books to look at; returns a list of authors (name and key).
    - get_author_books(author_key): takes an author's key; returns a list of that author's books (title, rating, number of ratings, pages), going through every page.

    **Addresses**
    - https://openlibrary.org/subjects/{genre}.json
    - https://openlibrary.org/search.json?author_key={key}&fields=...

    **How I'll know I have every record:** for each author, the number of books I collected must equal numFound.

    **Check for section 6:** for one author, the number of books my function returns should equal the numFound I see when I open the address in my browser.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent
    """)
    return


if __name__ == "__main__":
    app.run()
