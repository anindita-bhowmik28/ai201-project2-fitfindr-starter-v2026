# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> The three tools and planning loop are implemented, so the last command runs
> the complete FitFindr workflow.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps a shopper find a secondhand clothing item without searching several
marketplaces manually. The user describes the item, size, and maximum price in a
plain-language query. FitFindr searches the local listings, selects a match, and
uses the shopper's saved wardrobe to suggest outfits. It then returns a short,
post-ready fit-card caption for the selected item and outfit.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the available clothing listings for items that match the user's description, requested size, and maximum price.
- **Inputs:** `description` (str) — describes the item the user wants; `size` (str or None) — the requested clothing size, if provided; `max_price` (float or None) — the highest price the user is willing to pay, if provided.
- **Returns:** A list of matching listing dictionaries. Each listing contains information such as the item's id, title, description, category, style tags, size, condition, price, colors, brand, and platform.
- **When it has nothing:** Returns an empty list `[]` when no listings match the user's search requirements.

### `suggest_outfit`

- **What it does:** Takes the selected listing and the user's wardrobe and suggests an outfit that combines the new item with clothing the user already owns.
- **Inputs:** `new_item` (dict) — the listing selected from the search results; `wardrobe` (dict) — a dictionary whose `items` list contains the clothing the user already owns.
- **Returns:** A string containing an outfit suggestion that explains how the selected item can be styled with items from the user's wardrobe.
- **When it has nothing:** If the wardrobe is empty, returns general styling advice for the selected item instead of failing.

### `create_fit_card`

- **What it does:** Creates a short, post-ready caption for the outfit and the selected new clothing item.
- **Inputs:** `outfit` (str) — the outfit suggestion produced by `suggest_outfit`; `new_item` (dict) — the selected clothing listing.
- **Returns:** A string containing a short fit-card caption describing the outfit and new item.
- **When it has nothing:** If `outfit` is an empty string, returns a deterministic caption naming the selected item, price, and platform instead of calling the model. The planning loop never calls this tool without a selected `new_item`.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, store a helpful message in the session telling the user what they can change in their search, and stop the agent without calling `suggest_outfit`. Otherwise, select the first matching listing, store it in the session, and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query is parsed using string matching and regular expressions to extract the item description, requested size, and maximum price.

**What moves through the session:** The original query is stored first, followed by the parsed description, size, and maximum price. The results from `search_listings` are stored in `search_results`, the first matching item is stored in `selected_item`, the result from `suggest_outfit` is stored in `outfit_suggestion`, and the final result from `create_fit_card` is stored in `fit_card`. If the search returns no matches, an explanation is stored in `error` and the agent stops.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```text
$ python app.py ask 'vintage graphic tee under $30, size M'

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit: **Outfit 1: Casual Y2K Streetwear**
Pair the butterfly baby tee with the baggy straight-leg dark wash jeans and
chunky white sneakers for an effortless, nostalgic off-duty look. Layer the
black cropped zip hoodie on top for extra texture and a cool contrast against
the pastel print.

**Outfit 2: Elevated Retro Prep**
Style the baby tee tucked into the wide-leg khaki trousers, finished off with
black combat boots to add an edgy contrast to the sweet butterfly graphic.
Throw the vintage black denim jacket over your shoulders to tie the whole
retro-grunge aesthetic together.

Fit card: Scored this cute little pink and purple butterfly baby tee for just
$18 on Depop and honestly haven't taken it off since. Paired it with baggy
denim and chunky sneakers for the ultimate low-effort Y2K street fit.

```

**The three tools, tested one at a time**

```text
$ python -c "from tools import search_listings; r=search_listings('vintage graphic tee', 'M', 30); print(len(r), r[0]['title'], r[0]['price'], r[0]['platform'])"
8 Y2K Baby Tee — Butterfly Print 18.0 depop

```

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import load_listings,get_example_wardrobe; item=next(x for x in load_listings() if x['id']=='lst_002'); print(suggest_outfit(item,get_example_wardrobe()))"
**Outfit 1: Casual Y2K Streetwear**
Pair the butterfly baby tee with the baggy straight-leg dark wash jeans and
chunky white sneakers for an effortless, nostalgic off-duty look. Layer the
black cropped zip hoodie on top for extra texture and a cool contrast against
the pastel print.

**Outfit 2: Elevated Retro Prep**
Style the baby tee tucked into the wide-leg khaki trousers, finished off with
black combat boots to add an edgy contrast to the sweet butterfly graphic.
Throw the vintage black denim jacket over your shoulders to tie the whole
retro-grunge aesthetic together.

```

```text
$ python -c "from tools import create_fit_card; print(create_fit_card('', {'title':'Y2K Baby Tee — Butterfly Print','price':18.0,'platform':'depop'}))"
Found Y2K Baby Tee — Butterfly Print for $18.0 on depop — exactly the kind of
low-key win I was looking for.

```

---

## How I Used AI

**Moment 1**

- _What I asked for:_ I asked a model to help me structure the `suggest_outfit` tool to handle both a full wardrobe and an empty wardrobe, and to make the prompt more specific about which wardrobe pieces it was combining.
- _What came back:_ It suggested a conditional branch for the empty-wardrobe case and a wardrobe-aware prompt that names actual pieces from the user’s closet.
- _What I changed:_ I implemented the empty-wardrobe fallback and the wardrobe-specific prompt so the tool could produce useful suggestions instead of an empty or broken response.

**Moment 2**

- _What I asked for:_ I asked a model to tighten the `create_fit_card` prompt so the caption would explicitly name the selected item, its price, and the platform while keeping the tone casual and real.
- _What came back:_ It returned a stricter prompt design that required those details and explicitly avoided catalog-like language.
- _What I changed:_ I updated the fit-card prompt to require the item identity, price, and platform in the caption so the content was explicitly anchored to the selected listing.

**Part 2 moment**

- _What I asked for:_ I asked an AI assistant to test whether criterion 3 could be scored using only the trace as written.
- _What came back:_ It identified that the trace showed input key names but not the selected and received item IDs, so the state criterion was not observable from the evidence.
- _What I changed:_ I kept the agent behavior unchanged and made the trace print concrete values. The before and after logs now show `lst_004` both when the item is selected and when it enters `suggest_outfit`.

---

## Run Log — Before

This log was produced by `run_eval.py::main` in
`results/run_2026-10-12_0145_part2-before.md` with caching off. It contains
five real tries for each of the five scenarios and records 40 model calls.

| Criterion                          | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| ---------------------------------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes        | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 2. impossible query stops early    | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 3. state item transfer             | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 4. fit card mentions selected item | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 5. price ceiling respected         | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |

**Real output from one try per criterion**

```text
1. matching query completes
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
fit_card: Pulled this pink and purple butterfly baby tee from the thrift and
honestly didn't want to list it. Grab this Y2K absolute steal on my Depop right
now for just $18 before I change my mind.

2. impossible query stops early
stopped early: yes — No listings match your description, size, and budget.
Try a different item, a size that exists in the data, or a higher price ceiling.
selected_item: (none)
search_results: 0

3. state item transfer
selected_item output: 90s Track Jacket — Navy/White Stripe [lst_004]
suggest_outfit input: new_item_id='lst_004',
new_item_title='90s Track Jacket — Navy/White Stripe'

4. fit card mentions selected item
selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
fit_card: Toughened up this floral 90s silk slip dress with chunky boots and a
denim jacket for that ultimate alt-rock vibe. Snagged it on Depop for just $30
and I am never taking it off.

5. price ceiling respected
query: platform sneakers size 8 under $60
selected_item: Platform Sneakers — White Chunky Sole ($48.0, poshmark)
search_results: 1; every result price was at or below $60
```

---

## Verdicts and Diagnoses

I applied the unchanged targets in `criteria.md` to the five tries in
`results/run_2026-10-12_0145_part2-before.md`.

| #   | Criterion                       | Target | Verdict | How I decided                                                                                                                          |
| --- | ------------------------------- | ------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | matching query completes        | 4 of 5 | MET (5/5) | All five runs passed through MCP search, outfit generation, and fit-card generation without stopping early. |
| 2   | impossible query stops early    | 5 of 5 | MET (5/5) | All five searches returned `[]`; each trace ended at `branch: empty-search`, before `suggest_outfit`. |
| 3   | state item transfer             | 5 of 5 | MET (5/5) | In all five traces, selected item ID `lst_004` was also the `new_item_id` entering `suggest_outfit`. |
| 4   | fit card mentions selected item | 4 of 5 | MET (5/5) | All five captions called the item a floral silk slip dress or an equivalent recognizable description. |
| 5   | price ceiling respected         | 5 of 5 | MET (5/5) | All five MCP searches returned one $48 listing under the requested $60 ceiling and no over-budget result. |

**Diagnosis:** No criterion missed, so there is no failed tool or loop step to
diagnose. The deterministic checks—empty-result branching, session ID transfer,
and price filtering—were appropriately strict at 5 of 5. Criterion 4 was the
most generous because “recognizable description” requires judgment; I would
tighten a future version to require the exact title or a deterministic title
check. I did not revise it after seeing the results because the original
criterion remains measurable and the instructions say not to move a valid
target after testing.

---

## Loop Trace

This trace was produced by `agent.py::run_agent` through
`python app.py ask 'vintage graphic tee under $30, size M' --trace`.

```text
[1] new_session
      in:  dict with keys: query
      out: dict with keys: parsed
[2] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[3] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 8 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, 90s Silk Slip Dress — Floral, Midi Length … +5 more
[4] selected_item
      in:  dict with keys: first_result
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[5] suggest_outfit
      in:  dict with keys: new_item_title, wardrobe_items
      out: **Outfit 1: Casual Y2K Streetwear** Pair the butterfly baby tee with the baggy straight-leg dark wash jeans an…
[6] create_fit_card
      in:  dict with keys: item, outfit
      out: Scored this cute little pink and purple butterfly baby tee for just $18 on Depop and honestly haven't taken it…
```

The MCP move changed the call in `agent.py::run_agent` from a local Python
function call to `mcp_client.call_tool("search_listings", ...)`. The return
shape stayed a native list of listing dictionaries, so the branch and the two
downstream tools behaved the same.

### Failure modes triggered on purpose

- **Empty search:** `designer ballgown size XXS under $5` stopped before
  `suggest_outfit` and returned: “No listings match your description, size,
  and budget. Try a different item, a size that exists in the data, or a
  higher price ceiling.”
- **Empty wardrobe:** `vintage graphic tee under $30, size M` with
  `--empty-wardrobe` returned two general styling ideas, including suggested
  bottoms, shoes, and a layering option. It completed rather than crashing or
  returning an empty string.
- **Model unavailable:** A new uncached query was run with a deliberately
  invalid API key. It stopped at `suggest_outfit` and returned: “Outfit
  generation could not reach the model. The model rejected your API key.
  Check GEMINI_API_KEY in your .env file, or create a fresh key at
  aistudio.google.com. Check your internet connection and GEMINI_API_KEY, then
  try again.” The real key was not modified.

The empty-search trace showed the branch and early stop:

```text
[1] new_session
      in:  dict with keys: query
      out: dict with keys: parsed
[2] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[3] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[4] branch: empty-search
      in:  dict with keys: parsed
      out: No listings match your description, size, and budget. Try a different item, a size that exists in the data, or…
      →    stop: empty results
```

---

## The Improvement

**What I changed:** I made one system improvement: the `create_fit_card`
prompt now requires the exact selected-item title verbatim. The price,
platform, tone, and two-sentence constraints stayed the same.

**Why I picked it:** No original criterion missed, but the diagnosis found that
criterion 4 allowed subjective “recognizable” descriptions. In the before run,
all five captions were recognizable, but zero of five contained the exact title
`90s Silk Slip Dress — Floral, Midi Length`.

### Run Log — After

This log was produced by `run_eval.py::main` in
`results/run_2026-10-12_0225_part2-after.md`, using the same scenarios, five
tries each, and caching off.

| Criterion                          | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| ---------------------------------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes        | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 2. impossible query stops early    | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 3. state item transfer             | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 4. fit card mentions selected item | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |
| 5. price ceiling respected         | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5) |

**Did it help?** Yes. The original criterion verdict stayed MET (5/5), but the
stricter exact-title measurement improved from 0 of 5 before to 5 of 5 after.
For example, after try 1 says: “this 90s Silk Slip Dress — Floral, Midi Length.”
One unrelated fit-card request in the state-transfer scenario timed out; the
new required timeout handler stopped cleanly, and criterion 3 still passed
because `lst_004` had already reached `suggest_outfit` correctly.

---

## What's Still Broken

No acceptance criterion is still missed. The remaining operational limitation is
model availability: one after-run request timed out while creating a fit card.
The agent now stops within 30 seconds and tells the user to check the connection
and key, but it does not automatically retry the failed tool call.

I would add one bounded retry for transient model timeouts, then measure it with
the same five-try process. I stopped here because this unit permits one measured
improvement, and that improvement was the exact-title prompt change; adding a
retry would be a second system improvement outside the required scope.

The MCP move itself did not change search results. It changed
`agent.py::run_agent` from a direct `search_listings` call to
`mcp_client.call_tool`, and the client unwraps the MCP response back into the
same native list used by the existing empty-result branch.

---

## What I'd Do Differently

I would write criterion 4 more tightly before testing by requiring the exact
selected title rather than a “recognizable description.” The additional
before/after measurement showed why: both runs met the original criterion, but
exact-title inclusion changed from 0 of 5 to 5 of 5 and revealed the prompt
improvement much more clearly.

---

## How to run this project

### 1) Set up the environment

```bash
cd /path/to/ai201-project2-fitfindr-starter-v2026
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# paste your GEMINI_API_KEY into .env
python test.py
```

You are ready when `python test.py` passes.

### 2) Run the app

```bash
python app.py fields
python app.py listings --full -n 6
python app.py examples
python app.py ask 'vintage graphic tee under $30'
python app.py ask 'designer ballgown size XXS under $5'
```

### 3) Run the evaluation log

```bash
python run_eval.py --label before
python run_eval.py --label after
```

### 4) Optional trace output

```bash
python app.py ask 'vintage graphic tee under $30' --trace
```

This project is also documented in [RUNNING.md](RUNNING.md), but the commands above are the direct setup and execution flow for this repo.
