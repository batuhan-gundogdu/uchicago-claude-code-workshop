# Real Budget App - Design Spec

Date: 2026-07-17
Author: Batu (gundogdu@uchicago.edu), with Claude Code

## Purpose

A real, synced household budget app that Batu uses every day, replacing the manual `Wayne Budget.xlsx` workbook.
It also becomes the finale of the workshop ("here is how far you can take it"), but it is NOT the app rebuilt live on stage.
The live workshop demo stays a simple local version. This is the real product.

## Privacy and repo decisions

- This repo stays PRIVATE and holds real financial data.
- There is no public workshop repo and no "scan the QR for the repo" moment. The deck's closing slides change accordingly.
- No secrets in the repo. The frontend uses only Supabase's public anon key, which is safe to expose because Row Level Security enforces access.
- Real numbers live in the database, not in git.

## Stack (decided)

- Database + auth + sync: Supabase (managed Postgres, built-in auth, Row Level Security).
- Frontend: static web app, modern HTML/CSS/JS, minimal dependencies, no build step. Supabase JS client via ESM CDN. Charts hand-drawn in CSS/SVG (no chart library).
- Hosting: Vercel (free static hosting, real URL, installable to phone home screen).
- Auth: Supabase email magic link to Batu's address. Single user for now; RLS keeps data private per user.

## V1 scope

Modeled on the real workbook.

1. Fast logging: amount, category, type (income/expense), optional note, date defaults to today. Optimized for phone.
2. Current-month view: total income, total expenses, balance, and actual vs anticipated per category (the heart of the Monthly Budget sheet).
3. Category breakdown chart (expenses by category, current month).
4. Savings buckets: Vacation, Rainy Day, Arlington. Each with a running balance and dated deposit/withdrawal entries (the Bookkeeping sheet).
5. Everything synced across phone and web, private to Batu's login.

## Later phases (not V1)

- Per-person contributions detail (Batu / Natalie / Madre / Arlington).
- Itemized Home Expenses and Home Maintenance history.
- One-time import of real history from `Wayne Budget.xlsx` to seed the database.
- Per-month targets (V1 uses one anticipated amount per category).

## Data model

All tables carry `user_id uuid` defaulting to `auth.uid()`, with RLS policies restricting every row to its owner.

- `categories`: id, user_id, name, kind (`income` | `expense`), monthly_target numeric, sort_order int, archived bool.
  Seeded from the real workbook categories (Mortgage, HOA, Internet, Electric, Water, Gas, Groceries, Car, Car Insurance, Gas + Parking, Home Expenses, Enjoy, plus income/contribution categories).
- `transactions`: id, user_id, date, amount numeric (positive), category_id fk, type (`income` | `expense`), note text, created_at.
- `savings_buckets`: id, user_id, name, target numeric, sort_order int.
  Seeded with Vacation, Rainy Day, Arlington.
- `savings_entries`: id, user_id, bucket_id fk, date, amount numeric (positive deposit, negative withdrawal), note text, created_at.

Derived, not stored:
- Monthly actual per category = sum of `transactions.amount` for that category in the selected month.
- Bucket balance = sum of `savings_entries.amount` for that bucket.

## Security model

- RLS enabled on every table.
- Policy per table: `user_id = auth.uid()` for select/insert/update/delete.
- Anon key in the frontend is public-safe under RLS.
- Service-role key is never used in the frontend and never committed.

## Build sequence

1. Write `schema.sql` (tables, RLS policies, seed data) - Batu runs it in the Supabase SQL editor.
2. Build the static frontend (auth gate, logging form, monthly view, chart, savings buckets) against the Supabase client, with config placeholders.
3. Batu creates the Supabase project (signs in with GitHub) and provides project URL + anon key. Claude cannot create accounts.
4. Wire the real config, test end to end locally.
5. Deploy to Vercel (Batu authorizes the Vercel connection).

## Success criteria

- Batu can log a purchase on his phone and see it on his laptop moments later.
- The current-month view shows actual vs anticipated per category, matching how the workbook reads.
- Savings buckets show correct running balances.
- No real financial data is ever committed to git.
- Data is private to Batu's login (verified: a second account sees nothing).
