# Family Budget App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace an Excel budget workbook with a single self-contained `budget.html` app that reads and writes a `budget.json` file on disk.

**Architecture:** One `budget.html` file containing all markup, CSS, and vanilla JavaScript. A one-time Python script converts `budget_fake.xlsx` into the initial `budget.json`. The app loads that JSON via the File System Access API, auto-saves on every change, and renders four tabbed pages. Charts are hand-drawn inline SVG. No build step, no server, no runtime dependencies.

**Tech Stack:** Vanilla HTML/CSS/JavaScript (ES modules inline, no framework), File System Access API, inline SVG for charts. Python + openpyxl for the one-time data conversion only.

## Global Constraints

- Single self-contained file: all app code inline in `budget.html`. No external libraries, no network calls at runtime.
- Source of truth is `budget.json` on disk. Auto-save via File System Access API (Chrome/Edge); Export/Import buttons as universal fallback.
- Money displayed as `$#,##0.00`. Never use the em dash in any UI copy or code comments; use a plain dash.
- Months are open-ended across years, keyed as `YYYY-MM`. No fixed budget-year window.
- Budget lines come from `settings`, never hardcoded in page logic.
- The four detailed categories (Groceries, Enjoy, Home Expenses, Car Expenses) aggregate from `entries`. Car Expenses combines park, gas, and insurance.

---

## Data contract (shared by all tasks)

`budget.json` shape (produced by Task 1, consumed by Tasks 2-6):

```json
{
  "version": 1,
  "settings": {
    "stores": ["Trader Joes", "Jewel Osco", "..."],
    "lines": [
      { "id": "mortgage", "name": "Mortgage", "type": "expense",
        "category": "housing", "detailed": false,
        "anticipated": 4450, "recurringDefault": 4450 },
      { "id": "groceries", "name": "Groceries", "type": "expense",
        "category": "groceries", "detailed": true,
        "anticipated": 1100, "recurringDefault": null }
    ]
  },
  "entries": [
    { "id": "e_001", "date": "2025-11-13", "line": "home_expenses",
      "amount": 46.92, "item": "Wallmount", "store": null, "note": null }
  ],
  "monthlyActuals": {
    "2026-01": { "comed": 115, "water": 68.87, "rent_income": 2150 }
  },
  "fundsLedger": [
    { "id": "f_001", "date": "2025-11-28", "fund": "house",
      "amount": 157100, "note": "Received from the sales" }
  ]
}
```

Line ids (stable, snake_case): `mortgage`, `hoa`, `internet`, `comed`, `water`, `gas`, `groceries`, `car_loan`, `car_expenses`, `home_expenses`, `enjoy`, `vacation_savings`, `rainy_day_savings`, `payment_to_principal`, `rent_income`, `batu_contribution`, `natalie_contribution`.

Fund ids: `vacation`, `rainy_day`, `house`.

Fund auto-feed mapping (computed, not stored): `vacation_savings` -> `vacation`, `rainy_day_savings` -> `rainy_day`, `payment_to_principal` -> `house`.

---

## Task 1: Convert the spreadsheet to budget.json

**Files:**
- Create: `scripts/xlsx_to_json.py`
- Create: `budget.json` (generated output)
- Test: `scripts/test_xlsx_to_json.py`

**Interfaces:**
- Produces: `budget.json` matching the Data contract above.
- Produces: `build_budget(xlsx_path) -> dict` in `scripts/xlsx_to_json.py`.

- [ ] **Step 1: Write the failing test**

```python
# scripts/test_xlsx_to_json.py
from xlsx_to_json import build_budget

def test_totals_match_spreadsheet():
    b = build_budget("budget_fake.xlsx")
    # Line structure
    ids = {l["id"] for l in b["settings"]["lines"]}
    assert "car_expenses" in ids and "car_loan" in ids
    assert len(b["settings"]["lines"]) == 17
    # Grocery entries for January sum to the sheet's TOTAL (1132.72)
    jan_groc = sum(e["amount"] for e in b["entries"]
                   if e["line"] == "groceries" and e["date"].startswith("2026-01"))
    assert abs(jan_groc - 1132.72) < 0.01
    # Home expenses November total (813.1462)
    nov_home = sum(e["amount"] for e in b["entries"]
                   if e["line"] == "home_expenses" and e["date"].startswith("2025-11"))
    assert abs(nov_home - 813.1462) < 0.01
    # Funds ledger has the house-sale one-off
    assert any(abs(f["amount"] - 157100) < 0.01 for f in b["fundsLedger"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python -m pytest test_xlsx_to_json.py -v`
Expected: FAIL (ModuleNotFoundError / build_budget not defined)

- [ ] **Step 3: Implement build_budget**

Read the six sheets with `openpyxl` (`data_only=True`). Map:
- `Monthly Budget` column B -> each line's `anticipated`; fixed lines also set `recurringDefault = anticipated`. Combine the three car rows: `Car` -> `car_loan`; `Car Insurance` + `Gas + Park for Car` -> `car_expenses` anticipated is their sum. Variable non-detailed monthly cells (Comed, Water, Gas, Rent Income, Car Insurance, savings, principal) -> `monthlyActuals[YYYY-MM][line_id]`. Contributions and Rent map to income lines.
- `Groceries` sheet: each numeric cell under a month column -> one entry `{line:"groceries", date, amount, store}`. The leftmost column holds a day serial; combine with the month column header + inferred year (Nov/Dec = 2025, Jan-Jun = 2026) to build the ISO `date`. Store = the two-name header joined, or first name.
- `Enjoy` sheet: same as Groceries but `line:"enjoy"`, no store.
- `Home Expenses` sheet: Date/Item/Price triples per month block -> entries `{line:"home_expenses", date, item, amount}`.
- `Car`: the spreadsheet's `Gas + Park for Car` monthly figures go to `monthlyActuals` under `car_expenses` (no per-item detail exists), plus insurance folded in.
- `Bookkeeping` sheet: each non-empty movement in Vacation/Rainy Day/Arlington columns -> `fundsLedger` row with `fund` in {`vacation`,`rainy_day`,`house`} and the note from column E. Skip rows that duplicate the auto-fed monthly savings (the small recurring 480-540 contributions) so they are not double counted; keep genuine one-offs (sale, loans, Tulum, deposits).
- `stores`: unique store names collected from the Groceries headers.

Map skipped-vs-kept decisions with an inline comment naming the rule.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python -m pytest test_xlsx_to_json.py -v`
Expected: PASS

- [ ] **Step 5: Generate the file and eyeball it**

Run: `cd scripts && python -c "import json,xlsx_to_json as x; json.dump(x.build_budget('../budget_fake.xlsx'), open('../budget.json','w'), indent=2)"`
Then open `budget.json` and confirm the line list, a few entries, and the funds ledger look right.

- [ ] **Step 6: Commit**

```bash
git add scripts/xlsx_to_json.py scripts/test_xlsx_to_json.py budget.json
git commit -m "Add xlsx-to-json converter and generated budget.json"
```

---

## Task 2: App shell, storage layer, and navigation

**Files:**
- Create: `budget.html`
- Create: `.claude/launch.json` (static server for preview)

**Interfaces:**
- Produces (global `App` object / module functions):
  - `openFile()` -> prompts for `budget.json`, loads it into `state`, calls `render()`.
  - `save()` -> writes `state` back to the file handle (debounced); updates save indicator.
  - `exportJson()` / `importJson(file)` -> fallback download / upload.
  - `state` -> the parsed `budget.json` object, the single in-memory source of truth.
  - `render()` -> re-renders the active tab.
  - `money(n)` -> `"$1,234.56"`; `monthKey(date)` -> `"YYYY-MM"`; `uid(prefix)` -> unique id.
  - `setTab(name)` where name in `entry|monthly|funds|analysis`.

- [ ] **Step 1: Build the shell**

Create `budget.html` with: inline CSS (pastel palette, rounded cards, system font), a top bar (title, `budget.json - saved` indicator, Open/Export/Import buttons, month indicator), a tab strip (Entry, Monthly View, Funds, Analysis with icons), and a `<main id="view">`. Implement the storage layer and helpers above. On load, if a stored handle exists (IndexedDB) reopen silently; else show an "Open budget file" prompt. Auto-save is debounced 400ms after any `state` mutation.

- [ ] **Step 2: Add the launch config**

```json
{
  "version": "0.0.1",
  "configurations": [
    { "name": "budget", "runtimeExecutable": "python3",
      "runtimeArgs": ["-m", "http.server", "8123"], "port": 8123 }
  ]
}
```

- [ ] **Step 3: Verify in the browser**

Start the `budget` server, open `http://localhost:8123/budget.html`. Use `preview_snapshot` to confirm the four tabs render and the top bar shows the Open/Export/Import controls. Click each tab; confirm `setTab` switches the active view without error (`preview_console_logs` clean).

- [ ] **Step 4: Verify load via Import fallback**

Use `preview_*` to trigger `importJson` with the generated `budget.json` (the File System Access picker cannot be driven headless, so verify through Import). Confirm `state.settings.lines.length === 17` via `preview_eval`.

- [ ] **Step 5: Commit**

```bash
git add budget.html .claude/launch.json
git commit -m "Add app shell, storage layer, and navigation"
```

---

## Task 3: Entry page

**Files:**
- Modify: `budget.html`

**Interfaces:**
- Consumes: `state`, `save()`, `render()`, `money()`, `uid()`.
- Produces: `renderEntry()`, `addEntry(obj)`, `updateEntry(id, patch)`, `deleteEntry(id)`, `addMonthlyActual(month, lineId, amount)`.

- [ ] **Step 1: Category picker + adaptive form**

Render the four detailed category icon buttons plus "Bill / other line". Selecting a category shows the matching fields (Groceries: date/amount/store; Enjoy: date/amount/note; Home & Car: date/item/amount; Bill/other: month/line-dropdown/amount with `recurringDefault` prefilled). Submitting a detailed entry calls `addEntry`; submitting Bill/other calls `addMonthlyActual`.

- [ ] **Step 2: Recent entries list**

Below the form, list recent entries for the selected category, newest first, each with inline Edit and Delete wired to `updateEntry` / `deleteEntry`. Each mutation calls `save()`.

- [ ] **Step 3: Verify**

In the browser: select Groceries, add an entry (date 2026-07-01, amount 42.50, store Costco). Use `preview_snapshot` to confirm it appears at the top of the recent list; `preview_eval` to confirm `state.entries` grew by one and the store persisted. Delete it and confirm removal. Confirm `preview_console_logs` is clean.

- [ ] **Step 4: Commit**

```bash
git add budget.html
git commit -m "Add Entry page"
```

---

## Task 4: Monthly View page

**Files:**
- Modify: `budget.html`

**Interfaces:**
- Consumes: `state`, `money()`, `monthKey()`.
- Produces: `renderMonthly(month)`, `actualForLine(lineId, month)`, `plannedForLine(lineId)`, `availableMonths()`.

- [ ] **Step 1: Aggregation helpers**

`actualForLine`: for detailed lines sum `entries` matching `line` and month; for others read `monthlyActuals[month][lineId]`, falling back to `recurringDefault` for fixed lines. `availableMonths` returns sorted `YYYY-MM` keys present across entries + monthlyActuals.

- [ ] **Step 2: Table + month picker**

Month picker populated from `availableMonths`. Expense table with Planned / Actual / Difference columns; row background light green when `actual <= planned`, pink when over. Separate income section. Net row = sum(income actual) - sum(expense actual). Detailed lines expand to show the entries behind them.

- [ ] **Step 3: Verify against the spreadsheet**

Open Monthly View for `2026-01`. Use `preview_snapshot` / `preview_inspect` to confirm Groceries actual reads `$1,132.72` and its row/tint matches over/under vs planned 1100 (over -> pink). Confirm the net figure matches the spreadsheet's January net (1384.20 within rounding). Console clean.

- [ ] **Step 4: Commit**

```bash
git add budget.html
git commit -m "Add Monthly View page"
```

---

## Task 5: Funds page

**Files:**
- Modify: `budget.html`

**Interfaces:**
- Consumes: `state`, `money()`, `actualForLine()`, `availableMonths()`.
- Produces: `renderFunds()`, `fundBalance(fundId)`, `autoContributions()`, `addLedgerRow(obj)`, `deleteLedgerRow(id)`, `monthsOfRunway()`.

- [ ] **Step 1: Balance computation**

`autoContributions` derives per-month contributions from `monthlyActuals` for the three savings/principal lines mapped to their funds. `fundBalance` = sum(manual ledger rows for fund) + sum(auto contributions for fund). `monthsOfRunway` = total funds / average monthly expense burn.

- [ ] **Step 2: Cards + ledger**

Three balance cards + runway card. Ledger table newest first: auto rows rendered read-only tagged "auto"; manual rows add/edit/delete via `addLedgerRow`/`deleteLedgerRow`, each calling `save()`.

- [ ] **Step 3: Verify**

Confirm the house fund balance reflects the 157100 sale plus loans/principal, and that an auto contribution row appears for a month with `payment_to_principal`. Add a manual one-off, confirm balance updates and it persists in `state.fundsLedger`. Console clean.

- [ ] **Step 4: Commit**

```bash
git add budget.html
git commit -m "Add Funds page"
```

---

## Task 6: Analysis page

**Files:**
- Modify: `budget.html`

**Interfaces:**
- Consumes: `state`, `actualForLine()`, `availableMonths()`, `money()`.
- Produces: `renderAnalysis()`, `svgLine(series)`, `svgDonut(slices)`, `svgBars(pairs)`.

- [ ] **Step 1: Inline SVG chart helpers**

Implement `svgLine`, `svgDonut`, `svgBars` returning SVG strings sized to their container, using the pastel palette. No external library.

- [ ] **Step 2: Charts**

Month-by-month total spending (line), spending by category for selected month or all-time (donut), planned vs actual per line (grouped bars), and lists of biggest single expenses and biggest categories.

- [ ] **Step 3: Verify**

Open Analysis. `preview_snapshot` confirms all charts render as SVG with non-empty paths, and the biggest-expense list shows the largest `entries`/actuals. `preview_screenshot` to eyeball. Console clean.

- [ ] **Step 4: Commit**

```bash
git add budget.html
git commit -m "Add Analysis page"
```

---

## Task 7: Polish and final verification

**Files:**
- Modify: `budget.html`

- [ ] **Step 1: Empty-state and reset**

Add friendly empty states (no file open; a month with no data) and a "Start fresh / wipe data" action that replaces `state` with an empty-but-structured object (keeps `settings.lines`).

- [ ] **Step 2: Full walkthrough**

With `budget.json` loaded: visit all four tabs, add one entry of each type, switch months, add a ledger one-off. Confirm auto-save indicator toggles and, after a `window.location.reload()`, re-import shows the changes. Console and network clean across the run.

- [ ] **Step 3: Screenshot proof + commit**

```bash
git add budget.html
git commit -m "Add empty states and final polish"
```

---

## Self-Review notes

- Spec coverage: storage (Task 2), data model (Task 1 contract), all four pages (Tasks 3-6), fund auto-feed (Task 5), open-ended months (Task 4 helpers), import from spreadsheet (Task 1), fallbacks and empty states (Tasks 2, 7). Covered.
- Car line folding (three sheet rows -> `car_loan` + `car_expenses`) is handled explicitly in Task 1 Step 3.
- Function names are shared through the Interfaces blocks and reused verbatim across tasks.
