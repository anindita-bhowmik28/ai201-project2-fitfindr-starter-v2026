"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def _normalize_size_tokens(value: str) -> set[str]:
    """Make sizes compare by token, not by loose substring."""
    cleaned = re.sub(r"[^a-z0-9]+", " ", (value or "").lower())
    return {token for token in cleaned.split() if token}


def _size_matches(listing_size: str | None, requested_size: str | None) -> bool:
    if not requested_size or not listing_size:
        return True
    requested_tokens = _normalize_size_tokens(requested_size)
    listing_tokens = _normalize_size_tokens(listing_size)
    if not requested_tokens:
        return True
    if requested_tokens & listing_tokens:
        return True

    # Handle strings like "US 8" or "UK 6" and compare the number only.
    requested_num = re.search(r"(\d+(?:\.\d+)?)", requested_size)
    listing_num = re.search(r"(\d+(?:\.\d+)?)", listing_size)
    if requested_num and listing_num:
        return float(requested_num.group(1)) == float(listing_num.group(1))
    return False


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """Search listings by description, size, and price ceiling."""
    listings = load_listings()
    description_words = {
        word.strip(".,!?;:'\"")
        for word in (description or "").lower().split()
        if word.strip(".,!?;:'\"")
    }

    scored_matches = []
    for listing in listings:
        if max_price is not None and float(listing["price"]) > float(max_price):
            continue
        if not _size_matches(listing.get("size"), size):
            continue

        searchable_text = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
            listing.get("brand") or "",
        ]).lower()

        score = sum(1 for word in description_words if word in searchable_text)
        if score > 0:
            scored_matches.append((score, listing))

    scored_matches.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored_matches[:config.SEARCH_RESULT_LIMIT]]

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """Suggest one or two outfits using the user's wardrobe and the new item."""
    if not new_item:
        return "Please pick an item first so I can suggest an outfit."

    item_title = new_item.get("title", "the item")
    item_price = new_item.get("price")
    item_platform = new_item.get("platform", "the shop")
    item_color = ", ".join(new_item.get("colors", [])) or "neutral"

    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    if not wardrobe_items:
        prompt = (
            f"A shopper found this item: {item_title} ({item_price} on {item_platform}, colors: {item_color}). "
            "Give 2 outfit ideas for styling it in a modern thrifted way. Mention a vibe, shoes, and one layering option. "
            "Keep it concise and practical."
        )
        return generate(prompt, system="You are a fashion stylist who gives practical thrift outfit suggestions.", cache=True)

    wardrobe_text = "; ".join(
        f"{item.get('name', 'wardrobe item')} ({item.get('category', 'clothes')}, {item.get('color', 'neutral')})"
        for item in wardrobe_items[:8]
    )

    prompt = (
        f"New item: {item_title}. Price: ${item_price}. Platform: {item_platform}. Colors: {item_color}.\n"
        f"Wardrobe: {wardrobe_text}.\n"
        "Suggest 2 outfits that pair the new item with pieces the shopper already owns. "
        "Name specific wardrobe pieces, describe the vibe, and keep each outfit to 1-2 sentences."
    )
    return generate(prompt, system="You are a helpful fashion stylist creating outfit pairings from a wardrobe.", cache=True)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """Write a short, post-ready caption for the find and the outfit."""
    if not outfit or not outfit.strip():
        return (
            f"Found {new_item.get('title', 'this thrifted piece')} for ${new_item.get('price', 'N/A')} "
            f"on {new_item.get('platform', 'the shop')} — exactly the kind of low-key win I was looking for."
        )

    item_title = new_item.get("title", "this thrifted piece")
    item_price = new_item.get("price", "N/A")
    item_platform = new_item.get("platform", "the shop")
    item_colors = ", ".join(new_item.get("colors", [])) or "neutral tones"

    prompt = (
        f"Write a 2-sentence caption for a thrifted outfit post. "
        f"Item: {item_title}. Price: ${item_price}. Platform: {item_platform}. Colors: {item_colors}. "
        f"Outfit: {outfit}. "
        "The caption must explicitly name the item or a clear description of it, mention its price and platform, and keep the tone casual and real. "
        "Do not sound like a catalog product description."
    )
    return generate(prompt, system="You are a fashion caption writer creating authentic social post captions.", cache=True)
