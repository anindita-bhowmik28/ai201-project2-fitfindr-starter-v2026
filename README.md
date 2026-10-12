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

I reviewed the five criteria against the targets from `criteria.md` and rated each one plainly from the three runs and the actual outputs.

| #   | Criterion                       | Target | Verdict | How I decided                                                                                                                          |
| --- | ------------------------------- | ------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | matching query completes        | 4 of 5 | MET     | All five runs completed the end-to-end loop and produced both an outfit suggestion and a fit card, exceeding the 4-of-5 target.        |
| 2   | impossible query stops early    | 5 of 5 | MET     | Every impossible query returned no results and stopped before `suggest_outfit`, matching the required 5-of-5 branch behavior.          |
| 3   | state item transfer             | 5 of 5 | MET     | The selected item in the session matched the item passed through the loop in every run, so the state handoff was consistent.           |
| 4   | fit card mentions selected item | 4 of 5 | MET     | Every generated fit card named the selected item or a clear descriptive phrase that clearly anchored the caption to the right listing. |
| 5   | price ceiling respected         | 5 of 5 | MET     | Each search respected the max-price cap, and the returned item was always at or below the requested ceiling.                           |

**Diagnoses**

- No miss criteria required a repair. The implementation held steady against every target, so there were no broken measurements to revise.
- The one improvement I made later was not a fix for a missed criterion; it was a tightening of the fit-card prompt so it would more explicitly include the item identity, price, and platform in a more reliable way.

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

**What I changed:** I tightened the `create_fit_card` prompt to explicitly require the caption to name the selected item, mention the price, and mention the platform, while keeping the tone casual and not catalog-like.

**Which failure it was meant to fix:** This was meant to make the fit-card wording more explicitly anchored to the selected item, not to rescue a missed criterion; the original run already met the acceptance test, but I wanted the model output to be more consistently item-specific.

### Run Log — After

This log was produced by `run_eval.py::main` in `results/run_2026-10-05_0232_after.md`.

| Criterion                          | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| ---------------------------------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes        | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET     |
| 2. impossible query stops early    | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET     |
| 3. state item transfer             | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET     |
| 4. fit card mentions selected item | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET     |
| 5. price ceiling respected         | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | MET     |

**Did it help, and how do I know:** It did not change the pass/fail verdicts because the original system already met every criterion. The evidence is that the after-run table still produced five PASSes in every row, and the improvement was a prompt tightening rather than a scoring change. It made the item naming more explicit, but the measurable outcomes were unchanged.

---

## What's Still Broken

No criterion is still missed after the improvement run. The system is meeting the targets as written, and the remaining issue is not a failing test but a product-quality concern: the fit-card wording is still model-generated and therefore varies a little between runs even when the criterion passes.

If I were to tighten the system further, I would make the fit-card criterion more specific about requiring the exact item title or a very clear item descriptor, because that is the most likely place where variability could still drift away from the user’s mental model.

---

## What I'd Do Differently

I would write criterion 4 more tightly in the next unit by requiring the fit card to include either the exact selected title or a very clear descriptor of the selected item, not just any mention of a thrifted garment. That would better reflect what a user actually wants from a caption: a caption that unmistakably points to the item they just bought.

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
