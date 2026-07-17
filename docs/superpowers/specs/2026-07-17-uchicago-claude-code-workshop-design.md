# UChicago Claude Code Intro Workshop - Design Spec

Date: 2026-07-17
Author: Batu (gundogdu@uchicago.edu), with Claude Code

## Purpose

A 1-hour introductory workshop for UChicago staff and faculty (non-developers), introducing Claude Code as an everyday tool.
UChicago just signed a contract with Anthropic and is moving to a Claude Code integrated environment.

The single big idea: **you talk to your computer in plain English, it builds you the thing, and when you want it different you just say so - never touching code.**

The signature recurring beat: **editing the generated UI by talking** ("make it dark", "move the total to the top", "add a pie chart"). This is the moment that converts skeptics.

The closing brag: **the slides, the four example apps, and the workshop repo were all built in a single Claude Code session.**

## Audience

University staff and faculty. Non-technical. Mixed enthusiasm, captured by the opening poll:
1. I already use it every day - here to see what else I can do.
2. I don't know much - having my FOMO right now.
3. I'm a skeptic - don't think much of it, but here I am anyway.

## Scope of THIS session (preparation)

In this session, Claude Code will both **build the real artifacts** (safety-net files + deck) and **train Batu** on the moves so he can reproduce each app live in a fresh session on workshop day, with the pre-built HTML as fallback.

Deliverables:

1. **Deck** - UChicago house style (white, Calibri, maroon accents, phoenix on title, footer lockup). Built as .pptx.
2. **Four example apps** - simple, self-contained single-file HTML + localStorage, openable offline, hostable on GitHub Pages:
   - **Budget Controller** - income/expenses by category, running totals, chart. Primary canvas for the UI-tweak demo.
   - **Research Paper Tracker** - papers with status (to-read/reading/done), tags, notes, "review by" nudge.
   - **Daily Dashboard** - todos + reminders + "review this paper" nudges on one glanceable page. (Real inbox reading via connectors is mentioned as a next step, not built.)
   - **Teaching Assistant** - quiz/flashcard generator: type a topic and questions, get a clean self-contained quiz page.
3. **Cheat-sheet per app** - the exact opening prompt + 3 UI-tweak prompts to keep in pocket for the live demo.
4. **GitHub repo** (owner: batuhan-gundogdu) - hosts apps on Pages, holds deck + cheat-sheets, and is itself proof of the brag. Created private during prep; flipped to public for Pages once Batu has reviewed.
5. **The brag** - README + closing slide.

## Workshop 60-minute arc

- 0-5 - Poll Everywhere QR on screen (3 options), bars fill, read the room.
- 5-14 - The big idea + a light tease that the whole workshop was built this way.
- 14-49 - Live builds, fresh session each, ~8 min apiece, UI-tweak beat in every one. Plan: build 2 fully live; for the other 2, open the pre-built file and do only a live UI tweak.
- 49-57 - The reveal/brag + "how you personally start on Monday at UChicago."
- 57-60 - QR to the GitHub repo + Q&A.

## Decisions made

- Live poll uses Batu's existing **Poll Everywhere** account (robust in a live room; the poll widget was never the interesting artifact). We build the QR slide + question copy only.
- Deck uses **UChicago house style** via the deck-style skill.
- **GitHub repo created now** (private during prep, public at the end for Pages).
- Build order: **deck skeleton first**, then apps.
- App format: **self-contained HTML tools** (safety-net), demoed live from fresh sessions on the day.

## Non-goals

- No live email/calendar connector demos in the room (higher risk; mentioned verbally only).
- No self-built poll backend.
- Apps are intentionally simple - not production tools.

## Success criteria

- Batu can walk on stage, open a fresh session per app, and reproduce it - or fall back to the pre-built HTML - without stress.
- At least one live "I changed the UI just by asking" moment lands per app.
- The audience leaves knowing one concrete thing they will try themselves.
- The closing brag is literally true.
