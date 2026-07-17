# Budget Demo Cheat-Sheet

The anchor demo.
It tells a three-stage story: Stone Age, Modern, Connected.
Keep this file open on a second screen while you present.

## The story in one line

"Here is how I budget today (a spreadsheet).
Watch me turn it into something I can use from my phone, just by talking to my computer."

## Before you walk in (prep checklist)

- Open the real `Wayne Budget.xlsx` in Excel, ready on a tab, for Stage 1 only.
- Have the pre-built safety-net files open in a browser tab, hidden behind the live session.
- Have `apps/budget/sample-transactions.json` and `apps/budget/sample-statement.csv` in the repo folder.
- Start the live session with its working directory set to the workshop repo folder.
- Never type real bank credentials into anything on stage. There is no live bank connection in this demo.

## Stage 1: Stone Age (just show it, do not build)

Open the real Excel workbook and talk over it for about a minute.
Point at the Monthly Budget grid, then the Groceries and Enjoy detail sheets.
Say the pain out loud: "It only lives on my laptop, I type every number by hand, and I have to re-total the detail sheets back into the master."
That pain is the reason the next two stages exist.

## Stage 2: Modern (build this live)

Goal: a web and phone page where you tap in a purchase, pick a category, and it rolls into the monthly totals with a chart.

**Opening prompt (drop the sanitized file in first):**

> This is a sanitized version of how I budget today: apps/budget/sample-transactions.json.
> Read it and tell me how my budget works before we build anything.

Let it summarize. That "it read my file" moment is the first gasp.

**Then build in small, visible steps, one prompt at a time:**

> Build a single self-contained HTML page called a Budget Controller.
> Load these sample transactions, show a form to add a new one (description, amount, type, category), list them, and show income, expenses, and balance.

> Add a chart of spending by category under the form.

> Make it work well on my phone.

**The three rehearsed tweaks (this is the moment that converts skeptics):**

Practice these until they are muscle memory. Do them by talking, never by touching code.

1. > Make it dark.
2. > Move the balance to the top so it is the first thing I see.
3. > Add a pie chart of spending by category next to the bar chart.

Say each one out loud, then let the room watch the page change.

## Stage 3: Connected (stretch, only if time and energy are good)

Goal: import a credit card statement and split each purchase across three budgets: personal, home, professional.
This is CSV import, not a live bank connection. That keeps it simple and safe.

**Opening prompt (drop the sample statement in):**

> Here is a credit card statement: apps/budget/sample-statement.csv.
> List each transaction and let me tag it as personal, home, or professional, then show the total for each of the three budgets.

**A good follow-up tweak:**

> Guess a sensible tag for each row based on the merchant, and let me correct the ones you got wrong.

If Stage 3 wobbles at all, drop it and go straight to the reveal. It is a bonus, not a promise.

## If it breaks (fallback)

If a live session stalls, open the matching pre-built file from `apps/budget/` and keep going.
Describe the symptom, not a fix: "on my phone the total is cut off at the bottom" works better than guessing at the cause.
Nobody in the room can tell the difference between live and pre-built.

## Safety and privacy rules

- The real `Wayne Budget.xlsx` and any real figures stay out of the public repo.
- Demos use the sanitized sample data only.
- No real bank logins, no real card numbers, ever, on stage.
