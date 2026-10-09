# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    The team behind Nota al Margen, a Spanish-language book podcast, would use this tool. It helps them decide whether investing in Spotify advertising is worth it, by comparing how many months it takes to reach a download goal with organic growth versus with paid promotion, and how much that promotion would cost in total.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more.
    1. I start with the current monthly downloads (the real number from September).
    2. For the organic scenario, each month I multiply the previous month's downloads by (1 + the organic growth rate), until it reaches the goal.
    3. For the paid scenario, I do the same but with the paid growth rate, and I also add up the monthly promotion cost.
    4. I repeat month by month until each scenario reaches the goal, counting how many months each one took.
    5. At the end, I compare how many months the paid promotion saves, and how much it cost in total.
    6. (Note) This assumes a constant growth rate, which is a simplification — in reality, many variables could affect real growth, and a true A/B test would be more accurate.

    *What does your loop carry from one step to the next, the way a running total carries its sum?*
    -  The number of downloads accumulated so far each month (and, in the paid scenario, also the accumulated cost).
    -
     *Which check will you use in section 6, and which two numbers should agree?*
    - If I set the growth rate to 0%, each month's downloads should stay exactly equal to the previous month's, never growing.

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inpu# 3. Inputs — every number the project starts from goes here, nowhere else

    current_monthly_downloads = 4812   
    organic_growth_rate = 0.047        
    paid_growth_rate = 0.12           
    monthly_ad_cost = 250             
    download_goal = 10000             
    return (
        current_monthly_downloads,
        download_goal,
        monthly_ad_cost,
        organic_growth_rate,
        paid_growth_rate,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(current_monthly_downloads, download_goal, organic_growth_rate):
    downloads = current_monthly_downloads  
    months = 0
    while downloads < download_goal:
        downloads = downloads * (1 + organic_growth_rate)
        months = months + 1
    return downloads, months


@app.cell
def _(download_goal, downloads, months):
    print(f"Organic growth reaches {download_goal} downloads in {months} months.")
    print(f"Final downloads: {downloads:.0f}")
    return


@app.cell
def _(
    current_monthly_downloads,
    download_goal,
    monthly_ad_cost,
    paid_growth_rate,
):
    paid_downloads = current_monthly_downloads
    paid_months = 0
    total_cost = 0
    while paid_downloads < download_goal:
        paid_downloads = paid_downloads * (1 + paid_growth_rate)
        paid_months = paid_months + 1
        total_cost = total_cost + monthly_ad_cost

    print(f"Paid growth reaches {download_goal} downloads in {paid_months} months.")
    print(f"Final downloads: {paid_downloads:.0f}")
    print(f"Total promotion cost: ${total_cost:.2f}")
    return paid_downloads, paid_months, total_cost


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(
    download_goal,
    downloads,
    months,
    paid_downloads,
    paid_months,
    total_cost,
):
    months_saved = months - paid_months

    print("Scenario      Months to goal   Final downloads   Total cost")
    print(f"Organic       {months:>14}   {downloads:>16.0f}   $0.00")
    print(f"Paid          {paid_months:>14}   {paid_downloads:>16.0f}   ${total_cost:.2f}")

    print(f"\nPaying for Spotify ads gets Nota al Margen to {download_goal} downloads {months_saved} months sooner than organic growth alone, at a total cost of ${total_cost:.2f}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _(current_monthly_downloads):
    _check_downloads = current_monthly_downloads
    _check_rate = 0
    _check_months = 0
    while _check_months < 6:
        _check_downloads = _check_downloads * (1 + _check_rate)
        _check_months = _check_months + 1

    print(f"With a 0% growth rate, downloads after 6 months: {_check_downloads:.0f}")
    print(f"Starting downloads: {current_monthly_downloads}")
    print(f"Match: {_check_downloads == current_monthly_downloads}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    While writing the paid-growth scenario cell, I made two mistakes: I referenced the wrong counter variable (paid_months = months + 1 instead of months = months + 1, so the counter never advanced), and the function ended in a bare return with no print, so the results were never displayed. I asked my agent to finish the code, and it corrected both issues
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I verified it was correct in two ways: by running the Section 6 check (setting the growth rate to 0%, which confirmed downloads stayed flat — Match: True), and by confirming the organic scenario’s result (16 months, 10,034 downloads) matched a manual calculation of 4,812 × (1.047)^16.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sensitivity check: how does the paid scenario change if the ad-driven growth rate isn't exactly 12%?
    """)
    return


@app.cell
def _(current_monthly_downloads, download_goal, monthly_ad_cost):
    rates_to_test = [0.06, 0.24]

    for rate in rates_to_test:
        _downloads = current_monthly_downloads
        _months = 0
        _cost = 0
        while _downloads < download_goal:
            _downloads = _downloads * (1 + rate)
            _months = _months + 1
            _cost = _cost + monthly_ad_cost
        print(f"At a {rate*100:.0f}% growth rate: {_months} months, final downloads {_downloads:.0f}, total cost ${_cost:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Testing growth rates below and above the 12% assumption shows the result is sensitive to that number. At 6%, it takes 13 months and costs $3,250 to reach the goal; at 24%, it takes only 4 months and costs $1,000. The base case (12%) falls in between, at 7 months and $1,750. This means the 12% estimate matters a lot — if the real paid growth rate turns out closer to 6%, the promotion would cost nearly double and take almost twice as long to pay off.
    """)
    return


if __name__ == "__main__":
    app.run()
