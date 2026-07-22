# Family Budget App - Design

Date: 2026-07-22
Status: Approved

## Purpose

Replace a multi-sheet Excel workbook (`budget_fake.xlsx`) with a single, self-contained HTML app for tracking a household budget.
The app must run locally on a personal computer with no server and no build step, and must keep years of financial records safely.

## Delivery and architecture

The app ships as one self-contained file, `budget.html`.
All markup, styling, and logic live inline in that file.
There is no build step, no server, and no external runtime dependency, so the file opens directly in a browser and will keep working for years.

Charts are drawn with a small inline routine (hand-written SVG/canvas), not an external charting library, to preserve the single-file, fully-offline promise.

## Storage

The source of truth is a `budget.json` file on disk.

- On first launch the user clicks "Open budget file" and selects `budget.json`.
- The app holds the file handle (File System Access API) and auto-saves every change back to that file.
- The file is portable: it can be copied, backed up, or synced through iCloud/Dropbox.
- Auto-save requires Chrome or Edge. Other browsers (including Safari) use the manual Export / Import fallback described below.

The app always exposes plain Export and Import buttons as a universal fallback and backup mechanism.

An initial `budget.json` is generated from `budget_fake.xlsx` so the app opens fully populated and the data can be verified against the spreadsheet.
The user can wipe and replace it with real data later.

## Data model

`budget.json` contains four top-level pieces.

### settings

Defines the budget lines.
Each line has: a stable `id`, a display `name`, a `type` (`expense` or `income`), a `category` used for grouping, an `anticipated` (planned) amount, and an optional `recurringDefault` for fixed lines.

The lines mirror the spreadsheet:

Expenses: Mortgage, HOA, Internet, Comed, Water, Gas, Groceries, Car Loan, Car Expenses, Home Expenses, Enjoy, Vacation Savings, Rainy Day Savings, Payment to Principal.
Income: Rent Income, Batu Contribution, Natalie Contribution.

Four lines are "detailed" and aggregate from individual entries: Groceries, Enjoy, Home Expenses, Car Expenses.
Car Expenses combines park, gas, and insurance into one line.

### entries

The detailed purchase log.
One record per purchase, with fields: `id`, `date`, `amount`, `line` (the budget line id it maps to), and optional `store` (Groceries), `item` (Home, Car), and `note`.
This single list powers the Groceries, Enjoy, Home, and Car views by filtering on `line`.

### monthlyActuals

Quick-logged actual amounts for the non-detailed lines (utilities, rent, mortgage, savings, and so on).
Keyed by month and line id.
Fixed lines carry a `recurringDefault` that prefills the amount; the user confirms or edits it.

### fundsLedger

One-off fund movements that never appear in the monthly budget (house sale proceeds, taking a loan, the Tulum trip, deposits).
Each row has `id`, `date`, `fund`, `amount`, and `note`.
Funds tracked: Vacation Funds, Rainy Day, and the House/Cash fund.

Monthly Vacation Savings, Rainy Day Savings, and Payment to Principal amounts auto-post into the matching fund as contributions.
These are computed from `monthlyActuals`, not stored in `fundsLedger`, so there is no double entry.

## Month handling

Months are open-ended across years - any month, any year, not a fixed window.
The data set grows over time.
The Monthly View has a month picker.

## Pages

A persistent top bar shows file/save status, the four navigation tabs, and a global month indicator.
The visual style uses a pastel palette, rounded cards, and friendly category icons.

### 1. Entry

The fast-input page.

A category picker at the top offers the four detailed categories as icon buttons, plus a "Bill / other line" button for quick-logging utilities, rent, savings, and other non-detailed lines.

The form adapts to the selection:

- Groceries: Date, Amount, Store (dropdown of known stores plus free text).
- Enjoy: Date, Amount, optional note.
- Home / Car: Date, Item, Amount.
- Bill / other: Month, Line (dropdown), Amount, with the recurring default prefilled.

Below the form, a live list shows recent entries for the selected category, newest first, each editable and deletable inline.

### 2. Monthly View

The "Monthly Budget" sheet, one month at a time, with a month picker.

A table shows each budget line with Planned, Actual, and Difference.
Rows tint light green when actual is at or under planned, and pink when over.
Detailed categories show their aggregated total and can expand to reveal the entries behind them.
Income is a separate section from expenses.
A net figure at the bottom shows income minus expenses.

### 3. Funds

The Bookkeeping ledger.

Cards at the top show the balances for Vacation Funds, Rainy Day, and the House/Cash fund, plus months of runway (funds divided by average monthly burn).
Below, a dated ledger shows movements newest first.
Auto-fed monthly contributions appear as read-only rows tagged "auto".
One-offs are manual rows the user adds, edits, and deletes with a note.

### 4. Analysis

The insights page.

- Month-by-month total spending trend (line chart).
- Spending by category (donut) for the selected month or all-time.
- Planned vs actual per line (bar chart) to spot chronic over- or under-spending.
- Biggest single expenses and biggest categories.

All charts are drawn with the inline chart routine.

## Non-goals

- No multi-user support, accounts, or authentication.
- No cloud service or backend.
- No external libraries or network calls at runtime.
- No fixed budget-year window.
