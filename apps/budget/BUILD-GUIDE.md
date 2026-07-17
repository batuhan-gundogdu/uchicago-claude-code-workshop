# Budget App - Build Guide (real synced version)

This is written to you, to drive in a fresh Claude Code session.
Read a step, do it, check the result, move on.
Keep this file open on the side while you work.

## What you end up with

A real budget app that you use on your phone and laptop, with the same data on both.
It logs purchases, shows this month against your anticipated amounts per category, and tracks your savings buckets (Vacation, Rainy Day, Arlington).
Your data lives in a private database that only you can read.

## The shape of it (so the prompts make sense)

- Data, login, and sync: Supabase (a hosted Postgres database with built-in login).
- The app itself: a small static web page (HTML, CSS, JavaScript), no build step.
- Hosting: Vercel, which gives you a URL you open on both devices.
- Your real spreadsheet, `batu_budget.xlsx`, stays on your machine and is git-ignored. It is only used to seed the database once. Real numbers never get committed.

## Before you open the session

- Have `apps/budget/batu_budget.xlsx` in place (it already is).
- Open the workshop repo folder as the working directory.
- Have two browser tabs ready: Supabase and Vercel.

---

## Part 1: Stand up Supabase (about 5 minutes, you do this by hand)

Claude cannot create accounts for you, so this part is manual.

1. Go to supabase.com and sign in with GitHub.
2. Create a new project. Give it a name and a strong database password (save the password in your password manager).
3. Wait for it to finish provisioning.
4. Open the SQL editor: left sidebar, "SQL", then "New query".
5. Paste the whole schema below, then click Run. You should see "Success".
6. Get your two public values from Project Settings -> API: the Project URL and the anon public key. Keep them handy for Part 3. These two are safe to expose; the database rules below make sure the anon key can only touch your own rows.

### The schema (paste this into the Supabase SQL editor)

```sql
-- Real Budget App schema. Row Level Security means every row is visible
-- only to the user who created it, so the public anon key is safe in the frontend.

create table if not exists categories (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users on delete cascade,
  name          text not null,
  kind          text not null check (kind in ('income', 'expense')),
  monthly_target numeric not null default 0,
  sort_order    int not null default 0,
  archived      boolean not null default false,
  created_at    timestamptz not null default now()
);

create table if not exists transactions (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users on delete cascade,
  date        date not null default current_date,
  amount      numeric not null check (amount >= 0),
  category_id uuid references categories on delete set null,
  type        text not null check (type in ('income', 'expense')),
  note        text not null default '',
  created_at  timestamptz not null default now()
);

create table if not exists savings_buckets (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null default auth.uid() references auth.users on delete cascade,
  name       text not null,
  target     numeric not null default 0,
  sort_order int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists savings_entries (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null default auth.uid() references auth.users on delete cascade,
  bucket_id  uuid not null references savings_buckets on delete cascade,
  date       date not null default current_date,
  amount     numeric not null,          -- positive = deposit, negative = withdrawal
  note       text not null default '',
  created_at timestamptz not null default now()
);

create index if not exists idx_tx_user_date  on transactions (user_id, date);
create index if not exists idx_tx_category    on transactions (category_id);
create index if not exists idx_entries_bucket on savings_entries (bucket_id);
create index if not exists idx_categories_user on categories (user_id);

alter table categories      enable row level security;
alter table transactions    enable row level security;
alter table savings_buckets enable row level security;
alter table savings_entries enable row level security;

do $$
declare t text;
begin
  foreach t in array array['categories', 'transactions', 'savings_buckets', 'savings_entries']
  loop
    execute format('drop policy if exists own_rows on %I', t);
    execute format(
      'create policy own_rows on %I for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())',
      t
    );
  end loop;
end $$;
```

---

## Part 2: Build the frontend (in the fresh Claude session)

Work through these prompts one at a time.
After each one, look at what it built before sending the next.
This is exactly the rhythm you will show the room: describe an outcome, look, adjust.

**Prompt 1 - give it the context and the goal.**

> I am building a personal budget app in the folder apps/budget.
> The data lives in Supabase (Postgres with auth and row level security); the schema has four tables: categories, transactions, savings_buckets, savings_entries.
> Build a single static web app (index.html, styles.css, app.js as an ES module, no build step) that uses the Supabase JS client from a CDN.
> Read config from a global window.BUDGET_CONFIG (SUPABASE_URL and SUPABASE_ANON_KEY) loaded from a config.js file; if it is missing, show a friendly setup message.
> Start with just the login screen: an email field that sends a Supabase magic link, and sign out.

**Prompt 2 - first-run defaults.**

> When a logged-in user has no categories yet, create a sensible default set of expense and income categories, and three savings buckets named Vacation, Rainy Day, and Arlington. Do not hard-code any dollar amounts; targets start at zero and I set them in the app.

**Prompt 3 - logging and the month view.**

> Add the main screen: a form to log a transaction (description, amount, type, category, date defaulting to today), a monthly summary of income, expenses, and balance, and a list of recent transactions with a delete option. Add a previous/next month switcher at the top.

**Prompt 4 - anticipated vs actual.**

> Under the summary, show each category for the selected month: the amount spent so far, my anticipated monthly target, and a bar showing progress against the target. Let me edit a category's target inline.

**Prompt 5 - savings buckets.**

> Add a savings section: each bucket shows its running balance, and I can add a dated deposit or withdrawal with a note. A deposit is a positive amount, a withdrawal is negative.

**Prompt 6 - make it feel like a phone app.**

> Make it phone-first and responsive, with large tap targets, and make it look clean and calm. It should be pleasant to open every day.

---

## Part 3: Wire your config and test locally

1. In the fresh session:

> Create config.example.js with placeholder SUPABASE_URL and SUPABASE_ANON_KEY, and make sure config.js is git-ignored.

2. Copy the example to the real config and paste in your two Supabase values:

> Copy config.example.js to config.js and I will paste my real values in.

3. Serve the folder and open it:

> Serve apps/budget locally so I can open it in a browser, and tell me the URL.

4. Sign in with your email, click the magic link, and confirm you can add a transaction and see it persist after a refresh.

---

## Part 4: Deploy to Vercel (so your phone can reach it)

1. Go to vercel.com, sign in with GitHub, and import this repo.
2. Set the project's root directory to `apps/budget`. There is no build command; it is a static site.
3. Deploy. Vercel gives you a URL.
4. In Supabase, add that URL to the allowed redirect URLs (Authentication -> URL Configuration) so magic-link login works from the deployed site.
5. Open the URL on your phone and add it to your home screen.

---

## Part 5: Seed your real history (optional, once)

Only after login works end to end.

> Here is my real budget: apps/budget/batu_budget.xlsx.
> Read the Monthly Budget, Groceries, Enjoy, and Bookkeeping sheets and write a one-off script that inserts my history into Supabase as transactions and savings entries under my account. Show me the plan before you run it.

Keep the xlsx local. It is git-ignored on purpose.

---

## The "change it by talking" beats (rehearse three)

These are the moments the audience remembers. Practice them until they are automatic.

1. > Make it dark.
2. > Move the balance to the top so it is the first thing I see.
3. > Add a pie chart of this month's spending by category.

---

## If something breaks

- Describe the symptom, not a fix: "the magic link opens but I land on the login screen again" beats guessing.
- If login misbehaves after deploy, it is almost always a missing redirect URL in Supabase (Part 4, step 4).
- If the page is blank, open the browser console and paste the first red error to Claude.

## Safety rules

- Never type a real bank login into anything.
- The real xlsx and real figures stay out of git (they already are).
- The only keys in the frontend are the Supabase URL and anon key, which are safe under row level security. The service-role key never goes in the frontend and never gets committed.
