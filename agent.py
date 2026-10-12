"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


def _parse_query(query: str) -> dict:
    """Extract a description, size, and price limit from a natural-language query."""
    text = (query or "").strip()
    if not text:
        return {"description": "", "size": None, "max_price": None}

    raw = text
    max_price = None
    price_match = re.search(r"under\s+\$?\s*(\d+(?:\.\d+)?)", text, flags=re.I)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[: price_match.start()] + " " + text[price_match.end():]

    size = None
    size_match = re.search(
        r"\b(?:size|in size|sz)\s*([a-z0-9]+)", text, flags=re.I)
    if size_match:
        size = size_match.group(1).upper()
        text = text[: size_match.start()] + " " + text[size_match.end():]

    description = re.sub(r"\s+", " ", text).strip(" ,.-")
    description = re.sub(r"\bunder\b", " ", description, flags=re.I)
    description = re.sub(r"\b(?:in|on|with)\b", " ", description, flags=re.I)
    description = re.sub(r"\s+", " ", description).strip(" ,.-")
    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)
    count = 0

    while True:
        count += 1
        trace.check_iterations(count)

        trace.step("new_session", inputs={"query": query}, returned={
                   "parsed": session["parsed"]})
        session["parsed"] = _parse_query(query)
        trace.step("parse_query", inputs={
                   "query": query}, returned=session["parsed"])

        session["search_results"] = search_listings(
            session["parsed"]["description"],
            session["parsed"]["size"],
            session["parsed"]["max_price"],
        )
        trace.step(
            "search_listings",
            inputs={
                "description": session["parsed"]["description"],
                "size": session["parsed"]["size"],
                "max_price": session["parsed"]["max_price"],
            },
            returned=session["search_results"],
        )

        if not session["search_results"]:
            session["error"] = (
                "No listings match your description, size, and budget. Try a different item, "
                "a size that exists in the data, or a higher price ceiling."
            )
            trace.step(
                "branch: empty-search",
                inputs={"parsed": session["parsed"]},
                returned=session["error"],
                note="stop: empty results",
            )
            return session

        session["selected_item"] = session["search_results"][0]
        trace.step(
            "selected_item",
            inputs={"first_result": session["selected_item"]},
            returned=session["selected_item"],
        )

        try:
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"], wardrobe)
            trace.step(
                "suggest_outfit",
                inputs={
                    "title": session["selected_item"].get("title"),
                    "wardrobe_items": len(wardrobe.get("items", [])),
                },
                returned=session["outfit_suggestion"],
            )

            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"], session["selected_item"])
            trace.step(
                "create_fit_card",
                inputs={
                    "item": session["selected_item"].get("title"),
                    "outfit": session["outfit_suggestion"],
                },
                returned=session["fit_card"],
            )
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            trace.step(
                "ModelUnavailable",
                inputs={
                    "selected_item": session["selected_item"].get("title")},
                returned=session["error"],
                note="stop: model unavailable",
            )
            return session

        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(
            f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(
        f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
