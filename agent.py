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


# ── planning loop ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """Extract the main description, requested size, and max price from a user query."""
    text = query.strip()
    if not text:
        return {"description": "", "size": None, "max_price": None}

    price_match = re.search(r"(?:under|below|up\s+to|budget|max(?:imum)?|\$)\s*\$?(\d+(?:\.\d+)?)", text, flags=re.I)
    max_price = float(price_match.group(1)) if price_match else None

    size_match = re.search(
        r"\bsize\s+([A-Za-z0-9/ ]+?)(?=(?:\s*(?:under|below|budget|up\s+to|\$)|$))",
        text,
        flags=re.I,
    )
    if size_match is None:
        size_match = re.search(
            r"\bin\s+size\s+([A-Za-z0-9/ ]+?)(?=(?:\s*(?:under|below|budget|up\s+to|\$)|$))",
            text,
            flags=re.I,
        )
    size = size_match.group(1).strip() if size_match else None
    if size is None:
        size_match = re.search(r"\b(?:us|uk)\s*(\d+(?:\.\d+)?)\b", text, flags=re.I)
        size = size_match.group(0).upper() if size_match else None

    description = text
    if price_match:
        description = description[:price_match.start()] + description[price_match.end():]
    if size_match:
        description = description[:size_match.start()] + description[size_match.end():]
    description = re.sub(r"\s+", " ", description).strip(" ,.-")
    return {"description": description, "size": size, "max_price": max_price}


def run_agent(query: str, wardrobe: dict) -> dict:
    """Run the loop once and return the finished session."""
    session = new_session(query, wardrobe)
    trace.start_trace()

    for count in range(1, config.MAX_ITERATIONS + 2):
        trace.check_iterations(count)

        parsed = _parse_query(query)
        session["parsed"] = parsed
        description = parsed.get("description") or query
        size = parsed.get("size")
        max_price = parsed.get("max_price")

        try:
            results = search_listings(description, size=size, max_price=max_price)
            session["search_results"] = results
            trace.step(
                "search_listings",
                inputs={"description": description, "size": size, "max_price": max_price},
                returned=results,
            )
        except Exception as exc:  # noqa: BLE001
            session["error"] = f"Search failed: {exc}"
            return session

        if not results:
            session["error"] = (
                "No matching listings found. Try a different item description, size, or max price."
            )
            trace.step("empty search branch", note="stopping because no matching listings were found")
            return session

        selected_item = results[0]
        session["selected_item"] = selected_item
        trace.step(
            "select first result",
            inputs={"result_count": len(results)},
            returned={"id": selected_item.get("id"), "title": selected_item.get("title")},
        )

        try:
            outfit = suggest_outfit(selected_item, wardrobe)
            session["outfit_suggestion"] = outfit
            trace.step("suggest_outfit", inputs={"item": selected_item.get("title")}, returned=outfit)
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            return session
        except Exception as exc:  # noqa: BLE001
            session["error"] = f"Outfit generation failed: {exc}"
            return session

        try:
            fit_card = create_fit_card(outfit, selected_item)
            session["fit_card"] = fit_card
            trace.step("create_fit_card", inputs={"item": selected_item.get("title")}, returned=fit_card)
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            return session
        except Exception as exc:  # noqa: BLE001
            session["error"] = f"Fit card generation failed: {exc}"
            return session

        return session

    session["error"] = "The loop exceeded the step budget. Check the branch logic."
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
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
