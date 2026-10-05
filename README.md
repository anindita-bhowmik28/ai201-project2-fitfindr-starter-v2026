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
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
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

<!-- Three or four sentences: what a user asks for, and what they get back. -->

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
- **Inputs:** `description` (str) — describes the item the user wants; `size` (str) — the requested clothing size; `max_price` (float) — the highest price the user is willing to pay.
- **Returns:** A list of matching listing dictionaries. Each listing contains information such as the item's id, title, description, category, style tags, size, condition, price, colors, brand, and platform.
- **When it has nothing:** Returns an empty list `[]` when no listings match the user's search requirements.

### `suggest_outfit`

- **What it does:** Takes the selected listing and the user's wardrobe and suggests an outfit that combines the new item with clothing the user already owns.
- **Inputs:** `new_item` (dict) — the listing selected from the search results; `wardrobe` (list) — a list of dictionaries representing clothing items the user already owns.
- **Returns:** A string containing an outfit suggestion that explains how the selected item can be styled with items from the user's wardrobe.
- **When it has nothing:** If the wardrobe is empty, returns general styling advice for the selected item instead of failing.

### `create_fit_card`

- **What it does:** Creates a short, post-ready caption for the outfit and the selected new clothing item.
- **Inputs:** `outfit` (str) — the outfit suggestion produced by `suggest_outfit`; `new_item` (dict) — the selected clothing listing.
- **Returns:** A string containing a short fit-card caption describing the outfit and new item.
- **When it has nothing:** If the required outfit or new item is missing, it does not create a normal fit card and returns an appropriate empty/error result according to the tool implementation.

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

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

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

This log was produced by `run_eval.py::main` in `results/run_2026-10-05_0229_before.md` with caching off, five real tries per scenario.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 3. state item transfer | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 4. fit card mentions selected item | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. price ceiling respected | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |

**Real output from one run**, naming the file and function that produced it:

- File: `results/run_2026-10-05_0229_before.md`
- Function: `run_eval.py::main`

```text
### matching query completes
- Query: `vintage graphic tee under $30`
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Fit card:
```
Nothing beats the pastel butterfly print on this little Y2K baby tee. Styled it two ways because I couldn't decide between full-on baggy denim streetwear or mixing it up with cargos and boots—which vibe are we leaning into today? 🦋✨
```

```text
### impossible query stops early
- stopped early: yes — No matching listings found. Try a different item description, size, or max price.
- selected_item: (none)
- search_results: 0
```

```text
### state item transfer
- selected_item: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
- search_results: 10

Fit card:
```
Can’t decide if I’m channeling off-duty supermodel or just running errands I’ll definitely be late for, but this $45 thrifted 90s track jacket makes the whole fit work either way. Seriously the easiest piece to throw on over a tank and baggy denim (or trousers if I'm feeling fancy). ✨
```

```text
### fit card mentions selected item
- selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
- search_results: 10

Fit card:
```
Pulled this dreamy floral slip from the archives and I'm obsessed with how versatile it is—throw it on with an oversized crewneck and boots for peak 90s grunge, or dress it down with a denim jacket and sneakers. Grabbed this little beauty on Depop for just $30 and honestly, nothing beats vintage silk.
```

```text
### price ceiling respected
- Query: `platform sneakers size 8 under $60`
- selected_item: Platform Sneakers — White Chunky Sole ($48.0, poshmark)
- search_results: 1
```

---

## Verdicts and Diagnoses

I reviewed the five criteria against the targets from `criteria.md` and rated each one plainly from the three runs and the actual outputs.

| # | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1 | matching query completes | 4 of 5 | MET | All five runs completed the end-to-end loop and produced both an outfit suggestion and a fit card, exceeding the 4-of-5 target. |
| 2 | impossible query stops early | 5 of 5 | MET | Every impossible query returned no results and stopped before `suggest_outfit`, matching the required 5-of-5 branch behavior. |
| 3 | state item transfer | 5 of 5 | MET | The selected item in the session matched the item passed through the loop in every run, so the state handoff was consistent. |
| 4 | fit card mentions selected item | 4 of 5 | MET | Every generated fit card named the selected item or a clear descriptive phrase that clearly anchored the caption to the right listing. |
| 5 | price ceiling respected | 5 of 5 | MET | Each search respected the max-price cap, and the returned item was always at or below the requested ceiling. |

**Diagnoses**

- No miss criteria required a repair. The implementation held steady against every target, so there were no broken measurements to revise.
- The one improvement I made later was not a fix for a missed criterion; it was a tightening of the fit-card prompt so it would more explicitly include the item identity, price, and platform in a more reliable way.

---

## Loop Trace

**Happy path**

```text
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] select first result
      in:  dict with keys: result_count
      out: Y2K Baby Tee — Butterfly Print ($None, None)
[3] suggest_outfit
      in:  dict with keys: item
      out: **Outfit 1: Casual Y2K Streetwear** Pair the butterfly baby tee with the baggy straight-leg dark wash jeans an…
[4] create_fit_card
      in:  dict with keys: item
      out: Nothing beats the pastel butterfly print on this little Y2K baby tee. Styled it two ways because I couldn't de…
```

**Empty search**

```text
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] empty search branch
      →    stopping because no matching listings were found
```

**On the MCP move:** The app does not yet rewire `search_listings` onto MCP in this version; the trace is still showing the local tool path, and the branch logic is visible in the trace exactly where it should be. The empty-search path stops before the second tool as required.

---

## The Improvement

**What I changed:** I tightened the `create_fit_card` prompt to explicitly require the caption to name the selected item, mention the price, and mention the platform, while keeping the tone casual and not catalog-like.

**Which failure it was meant to fix:** This was meant to make the fit-card wording more explicitly anchored to the selected item, not to rescue a missed criterion; the original run already met the acceptance test, but I wanted the model output to be more consistently item-specific.

### Run Log — After

This log was produced by `run_eval.py::main` in `results/run_2026-10-05_0232_after.md`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 3. state item transfer | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 4. fit card mentions selected item | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. price ceiling respected | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |

**Did it help, and how do I know:** It did not change the pass/fail verdicts because the original system already met every criterion. The evidence is that the after-run table still produced five PASSes in every row, and the improvement was a prompt tightening rather than a scoring change. It made the item naming more explicit, but the measurable outcomes were unchanged.

---

## What's Still Broken

No criterion is still missed after the improvement run. The system is meeting the targets as written, and the remaining issue is not a failing test but a product-quality concern: the fit-card wording is still model-generated and therefore varies a little between runs even when the criterion passes.

If I were to tighten the system further, I would make the fit-card criterion more specific about requiring the exact item title or a very clear item descriptor, because that is the most likely place where variability could still drift away from the user’s mental model.

---

## What I'd Do Differently

I would write criterion 4 more tightly in the next unit by requiring the fit card to include either the exact selected title or a very clear descriptor of the selected item, not just any mention of a thrifted garment. That would better reflect what a user actually wants from a caption: a caption that unmistakably points to the item they just bought.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
