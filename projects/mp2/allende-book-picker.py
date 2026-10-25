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


@app.cell
def _():
    genre = "science fiction"
    top_n_books = 10
    max_pages = 300
    min_rating = 4.0
    min_ratings_count = 10
    return genre, max_pages, min_rating, min_ratings_count, top_n_books


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell
def _():
    import requests

    return (requests,)


@app.cell
def _(requests):
    def get_genre_authors(genre, top_n):
        subject = genre.lower().replace(" ", "_")
        url = f"https://openlibrary.org/subjects/{subject}.json"
        response = requests.get(url, params={"limit": top_n}, timeout=30)
        response.raise_for_status()
        data = response.json()

        authors = []
        seen_keys = []
        for work in data["works"]:
            for author in work["authors"]:
                key = author["key"].replace("/authors/", "")
                if key not in seen_keys:
                    seen_keys.append(key)
                    authors.append({"name": author["name"], "key": key})
        return authors

    return (get_genre_authors,)


@app.cell
def _(requests):
    def get_author_books(author_key):
        books = []
        page = 1
        while True:
            url = "https://openlibrary.org/search.json"
            response = requests.get(
                url,
                params={
                    "author_key": author_key,
                    "fields": "title,ratings_average,ratings_count,number_of_pages_median",
                    "page": page,
                    "limit": 100,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            for doc in data["docs"]:
                books.append({
                    "title": doc.get("title"),
                    "rating": doc.get("ratings_average"),
                    "ratings_count": doc.get("ratings_count"),
                    "pages": doc.get("number_of_pages_median"),
                })

            if len(books) >= data["numFound"]:
                break
            page = page + 1

        return books

    return (get_author_books,)


@app.cell
def _(genre, get_genre_authors, top_n_books):
    authors = get_genre_authors(genre, top_n_books)
    for _a in authors:
        print(_a["name"], _a["key"])
    return (authors,)


@app.cell
def _(authors, get_author_books):
    all_books = []
    for _author in authors:
        _author_books = get_author_books(_author["key"])
        for _book in _author_books:
            _book["author"] = _author["name"]
            all_books.append(_book)

    len(all_books)
    return (all_books,)


@app.cell
def _(all_books, max_pages, min_rating, min_ratings_count):
    eligible_books = []
    for _book in all_books:
        if _book["rating"] is None or _book["pages"] is None:
            continue
        if _book["pages"] > max_pages:
            continue
        if _book["rating"] < min_rating or _book["ratings_count"] < min_ratings_count:
            continue
        eligible_books.append(_book)

    len(eligible_books)
    return (eligible_books,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell
def _(eligible_books):
    sorted_books = sorted(eligible_books, key=lambda b: b["rating"], reverse=True)

    print(f"{'Title':<40}{'Author':<25}{'Rating':>8}{'Pages':>8}")
    for _book in sorted_books:
        print(f"{_book['title']:<40}{_book['author']:<25}{_book['rating']:>8.2f}{_book['pages']:>8}")
    return (sorted_books,)


@app.cell
def _(genre, sorted_books):
    best_book = sorted_books[0]

    print(f"This week's pick for {genre} is '{best_book['title']}' by {best_book['author']}, rated {best_book['rating']:.2f} from {best_book['ratings_count']} ratings, at {best_book['pages']} pages.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell
def _(authors, get_author_books, requests):
    _check_author = authors[0]
    _check_response = requests.get(
        "https://openlibrary.org/search.json",
        params={"author_key": _check_author["key"], "limit": 1},
        timeout=30,
    )
    _check_num_found = _check_response.json()["numFound"]

    _check_books = get_author_books(_check_author["key"])

    print(f"Author: {_check_author['name']}")
    print(f"numFound from the API: {_check_num_found}")
    print(f"Books collected by get_author_books: {len(_check_books)}")
    print(f"Match: {_check_num_found == len(_check_books)}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    I checked `get_author_books` against the API directly, for one author (Isabel Allende). I asked the API for her `numFound`, the total number of her books it reports, without going through my function. Then I ran `get_author_books` on her and counted what it returned. Both numbers were 104, so my function collected every page and neither lost nor duplicated any books.
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
    To find the best-known authors in a genre, the agent’s first idea was to use the authors list on Open Library’s genre page (/subjects/magical_realism.json?details=true).

    What I found: When I opened that reply in my browser, the top authors were Rohan Quine, Toshikazu Kawaguchi and Luis Ochoa Siguencia, and Gabriel García Márquez was not on the list at all. The number next to each author only counts how many of their books carry the “magical realism” tag, not how well known they are.

    What I changed: I didn’t use that list. Instead, my tool takes the 10 most-edited books in the genre (the works list, which is ordered by number of editions) and keeps their authors, without repeating anyone. That gives Isabel Allende, Salman Rushdie and Laura Esquivel, which matches what I wanted: well-known authors.

    How I knew: I compared the two lists in the raw reply in my browser. Where it is: my plan (commit mp2: plan before AI) and the function get_genre_authors in section 4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **`get_genre_authors(genre, top_n)`**

    What goes in: a genre, as plain text (such as `"magical realism"`), and how many of the genre's most-edited books to look at.

    What comes out: a list of authors, each one a dictionary with their name and their Open Library key, with no author repeated.

    One line I had to ask about: `key = author["key"].replace("/authors/", "\")`. The API returns an author's key wrapped in a path, like `"/authors/OL228079A"`, and every other request in this notebook needs just `"OL228079A"`, so this line strips the wrapping off.

    **`get_author_books(author_key)`**

    What goes in: one author's key.

    What comes out: a list of every book by that author the API knows about, each one a dictionary with its title, rating, number of ratings, and page count.

    One line I had to ask about: `if len(books) >= data["numFound"]:`. The API sends an author's books 100 at a time, so this line checks, after each page, whether I already have every book the API reports (`numFound`). If not, the loop asks for the next page.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Prediction.** I will change `genre` in section 3 from `"magical realism"` to `"science fiction"`. I expect the list of authors to change completely (different well-known names), and I expect the final pick in section 5 to be a different book, since it depends on which authors and books the new genre returns. I do not know in advance whether the new pick will have a higher or lower rating than `Haroun and the Sea of Stories` (4.30).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I changed `genre` to `"science fiction"` and ran the notebook again. As predicted, the list of authors changed completely — Arthur Conan Doyle, Aldous Huxley, Jack London, Lewis Carroll, H. G. Wells and L. Frank Baum replaced Isabel Allende, Salman Rushdie and the rest. The final pick changed too, from "Haroun and the Sea of Stories" (4.30) to "The Case-Book of Sherlock Holmes" by Arthur Conan Doyle (4.55) — a higher rating than before. One thing I did not predict: the notebook took much longer to run, about 7.5 minutes instead of a few seconds, because "science fiction" surfaced authors like Conan Doyle and Wells with hundreds of editions each, so `get_author_books` had to request many more pages from the API.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further
    """)
    return


@app.cell
def _(
    get_author_books,
    get_genre_authors,
    max_pages,
    min_rating,
    min_ratings_count,
):
    genres_to_compare = ["magical realism", "science fiction", "historical fiction"]
    _compare_top_n = 5

    genre_picks = []
    for _genre in genres_to_compare:
        _authors = get_genre_authors(_genre, _compare_top_n)
        _genre_books = []
        for _author in _authors:
            _author_books = get_author_books(_author["key"])
            for _book in _author_books:
                _book["author"] = _author["name"]
                _genre_books.append(_book)

        _eligible = []
        for _book in _genre_books:
            if _book["rating"] is None or _book["pages"] is None:
                continue
            if _book["pages"] > max_pages:
                continue
            if _book["rating"] < min_rating or _book["ratings_count"] < min_ratings_count:
                continue
            _eligible.append(_book)

        if len(_eligible) == 0:
            genre_picks.append({"genre": _genre, "title": "(no eligible book found)", "author": "", "rating": 0, "pages": 0})
            continue

        _sorted = sorted(_eligible, key=lambda b: b["rating"], reverse=True)
        _best = _sorted[0]
        genre_picks.append({"genre": _genre, "title": _best["title"], "author": _best["author"], "rating": _best["rating"], "pages": _best["pages"]})

    print(f"{'Genre':<22}{'Title':<35}{'Author':<22}{'Rating':>8}{'Pages':>8}")
    for _pick in genre_picks:
        print(f"{_pick['genre']:<22}{_pick['title']:<35}{_pick['author']:<22}{_pick['rating']:>8.2f}{_pick['pages']:>8}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    About 6 hours.
    """)
    return


if __name__ == "__main__":
    app.run()
