# Quiz generator - how it was built

> A clean transcript of the Claude Code conversation that built this app.
> Session `978c7a29` · 2026-07-23 · 4 prompts from Batu.
>
> Claude's tool actions (editing files, running commands, browsing the preview) are
> collapsed into one-line summaries so the conversation reads as a narrative.


---

### 🧔🏻‍♂️ Batu

We will build a quiz app under apps. In the folder I put a pdf. In this document you'll see a bunch of test questions and the answer sheet at the bottom. Can you write the code that creates a quiz app that shows the questions to me one by one and marks the correct answer as I click. I should be able to take the exam again and again as needed. Use pastel colors. Show me the progress on an artifact.

### 🤖 Claude

I'll start by finding and reading the PDF to understand the quiz content.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `find "/Users/batuhangundogdu/Claude Code Workshop/apps" -iname "*.pdf" -maxdepth 3 2>/dev/…`  _( Find the PDF in apps folder )_

### 🤖 Claude

Found it. Let me read the PDF to understand the questions and answer sheet.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop/apps/quiz" && python3 -c "import pypdf; r=…`  _( Check PDF page count )_
> - Read `dsd_ds9.pdf`

### 🤖 Claude

Let me read the rest of the PDF to capture all questions and the answer sheet.


<sub>*Behind the scenes, Claude:*</sub>
> - Read `dsd_ds9.pdf`

### 🤖 Claude

I now have the complete picture of the workbook. It contains two sections:
- **Traffic Sign Identification** - match 24 sign images (a-x) to 24 sign names (answer key: a=19, b=1, ...).
- **Written Exam** - 62 questions (True/False + multiple choice a/b/c), with a full answer key.

Let me look at how the sibling apps are built to match conventions, and check whether I can extract the sign images from the PDF.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== apps tree ===" && ls -la app…`  _( Inspect sibling apps and image extraction tools )_

### 🤖 Claude

budget2 is a single self-contained `budget.html`. Let me check its style to match conventions, and inspect what's on the sign page.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== budget.html head ===" && hea…`  _( Inspect budget.html conventions and sign page images )_

### 🤖 Claude

budget2 sets a clear house style: single self-contained HTML, inline CSS/JS, no libraries or network calls, pastel CSS-variable palette. I'll match that exactly. Let me confirm whether the sign images on page 13 are extractable raster images or vector art.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && pdfimages -list "apps/quiz/dsd_ds9.pdf…`  _( List raster images on PDF page 13 )_

### 🤖 Claude

Confirmed: the signs on page 13 are vector art (no raster images to extract), so the sign-matching section would mean hand-drawing 24 standard signs as inline SVG - crisp and dependency-free, matching the budget2 house style, but meaningful effort.

I have enough to plan. Two things genuinely change what I build, so let me confirm them with you.

#### 🤔 Claude checks in

- **Q:** The workbook has two sections. Which should the quiz app cover?
  **Batu:** _Both sections_
- **Q:** How do you want to use the finished quiz?
  **Batu:** _Saved HTML file + live artifact_

### 🤖 Claude

Both sections, and a saved file plus a live inline artifact. That's everything I need. Let me capture the answer key and write the plan.


<sub>*Behind the scenes, Claude:*</sub>
> - Wrote `we-will-build-a-radiant-gem.md`

### 🤖 Claude

The plan is ready.


<sub>*Behind the scenes, Claude:*</sub>
> - Used tool `ExitPlanMode`

### 🤖 Claude

Plan approved. Let me build the app. First, a task list to track the work.


<sub>*Behind the scenes, Claude:*</sub>
> - Updated the task checklist

### 🤖 Claude

Now I'll write the app.


<sub>*Behind the scenes, Claude:*</sub>
> - Wrote `quiz.html`
> - Updated the task checklist

### 🤖 Claude

The file is open in the Browser pane. Let me verify it works - check for errors and test the flow.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: list

### 🤖 Claude

The Browser pane shows the file, but I want to drive it programmatically to verify. Let me start a simple static server and test the flow end to end.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cat > "/Users/batuhangundogdu/Claude Code Workshop/.claude/launch.json" 2>/dev/null << 'EO…`  _( Create launch.json for static quiz server )_
> - Wrote `launch.json`
> - Browser preview: start
> - Edited `launch.json`
> - Browser preview: start
> - Browser preview: eval
> - Browser preview: console_logs

### 🤖 Claude

No errors. Let me take a screenshot of the start screen and then drive the quiz flow.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: screenshot

### 🤖 Claude

The start screen looks great. Let me test the "Signs only" mode to verify SVG rendering and the answer-marking logic in one pass. First select it, then start.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: click
> - Browser preview: click
> - Browser preview: click
> - Browser preview: screenshot

### 🤖 Claude

STOP renders perfectly and options are shuffled. Let me test the answer-marking: click a wrong option (A = "No Passing Zone") and confirm the correct one is revealed.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: click
> - Browser preview: eval

### 🤖 Claude

Marking logic is correct: wrong choice flagged ✗, correct "Stop" revealed ✓, others dimmed, Next enabled, score correctly stayed 0. Now let me confirm score increments on a correct answer. Advance to Q2 (sign "b" = Winding Road Ahead with shuffle off) and click that option.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: click
> - Browser preview: eval

### 🤖 Claude

Score increments correctly (now 1, "✓ Correct!"). The UI flow is solid. Now let me validate the underlying data for transcription errors - answer-key completeness, the sign mapping being a true 1-24 bijection, and every multiple-choice answer matching a real option.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop/apps/quiz" && python3 - << 'PY' import re …`  _( Validate quiz data integrity )_

### 🤖 Claude

All data checks pass. The last regex just failed to match my SVG formatting - let me confirm all 24 sign artworks exist properly.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop/apps/quiz" && python3 - << 'PY' import re …`  _( Confirm all 24 sign artwork keys exist )_

### 🤖 Claude

All 24 sign artworks present and the mapping is a verified bijection. Now let me exercise the results + review + retake path. I'll auto-play through the rest of this run (clicking the first option each time) to reach the results screen.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: eval

### 🤖 Claude

Results screen works: score 5/24, donut shows 21%, verdict correct, 19 missed items in review with sign SVGs rendering. Let me screenshot it and then confirm retake works.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: screenshot

### 🤖 Claude

Results and review render beautifully - signs shown with "you chose / correct" lines. Let me confirm "Take it again" starts a fresh run.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: click
> - Browser preview: eval

### 🤖 Claude

Retake works - fresh run, score reset, bar at 0%. Last check: written-question rendering (True/False) and the best-score box on the home screen. Let me go home and start a written run.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: eval
> - Browser preview: eval

### 🤖 Claude

Everything works. Best-score persists (`🏆 Your best so far: 21% (5/24)`), written mode shows True/False options with the sign area hidden, 62 questions. Let me capture the written-question view.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: screenshot

### 🤖 Claude

The saved file is fully verified: start screen, both question types, instant answer marking, score, progress bar, results with sign-illustrated review, unlimited retake, and persistent best score - all working with no console errors. Let me stop the test server and mark verification done.


<sub>*Behind the scenes, Claude:*</sub>
> - Browser preview: stop
> - Updated the task checklist

### 🤖 Claude

Now the live inline artifact you asked for.


<sub>*Behind the scenes, Claude:*</sub>
> - Used tool `read_me`

### 🤖 Claude

The saved file is the source of truth. Here's a live inline copy so you can try it right now.


<sub>*Behind the scenes, Claude:*</sub>
> - Used tool `show_widget`

### 🤖 Claude

Both deliverables are ready and verified.

## What you've got

**[apps/quiz/quiz.html](apps/quiz/quiz.html)** - a single self-contained file (no libraries, no network), matching the pastel house style of your budget2 app. Plus the live copy above, which you can play right now.

**How it works**
- Pick a section on the start screen: **Both** (86 questions), **Written only** (62), or **Signs only** (24), with a shuffle toggle.
- Questions appear one at a time. The moment you click an answer, the correct one turns green and a wrong pick turns red - so you learn as you go.
- A progress bar and running score sit up top; the end screen shows a percentage donut, an 80%-pass verdict, and a scrollable review of everything you missed (traffic-sign questions show the sign right in the review).
- **Take it again** reshuffles and restarts - unlimited retakes. Your best score is remembered between attempts.

**Where the content came from** - every question and answer is transcribed from the workbook and cross-checked against the answer key on page 29. I verified programmatically: all 62 written questions present, all 10 multiple-choice answers valid, and the 24 traffic signs form a correct 1-to-1 map. The 24 signs are hand-drawn as inline SVG (the PDF had no extractable images), so they stay crisp and dependency-free.

**To open the file directly**, either double-click it, or I left a preview config so you can run:

```bash
python3 -m http.server 8753 --directory "apps/quiz"
```

then visit `http://localhost:8753/quiz.html`.

One note: I added `.claude/launch.json` (a small preview config for the browser pane) - harmless tooling, easy to delete if you don't want it. Want me to commit this, or adjust anything (e.g. pass threshold, distractor count for sign questions, or an explanation blurb per answer)?


---

### 🧔🏻‍♂️ Batu

Ran the `/create-pr` slash command.

### 🤖 Claude

I'll create a PR for the quiz app. Let me first check the current state.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== branch ===" && git branch --…`  _( Check branch, status, remote )_

### 🤖 Claude

On main with untracked files. I'll create a feature branch and commit only the quiz work, not the unrelated budget2 artifacts. Let me inspect `.claude/` since I only added `launch.json` there this session.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== .claude contents ===" && ls …`  _( Inspect .claude and apps/quiz contents )_

### 🤖 Claude

`.claude/` has my `launch.json` plus a personal `settings.local.json` (not mine, pre-existing) - I'll include only `launch.json`. I'll create a branch and stage just the quiz work, leaving the unrelated budget2 artifacts alone.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && git checkout -b add-illinois-rules-qui…`  _( Create branch and stage quiz files )_

### 🤖 Claude

Staged exactly the three quiz files. Now commit (no co-author, per your global instructions).


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && git commit -q -m "Add Illinois Rules o…`  _( Commit the quiz app )_
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && git push -u origin add-illinois-rules-…`  _( Push branch to remote )_
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && gh pr create --base main --head add-il…`  _( Create the pull request )_

### 🤖 Claude

Done. The PR is open.

<pr-created>https://github.com/batuhan-gundogdu/uchicago-claude-code-workshop/pull/1</pr-created>

**Summary of what I did:**
- Created branch `add-illinois-rules-quiz-app` off `main` (avoided committing directly to main).
- Committed three files: `apps/quiz/quiz.html` (the app), `apps/quiz/dsd_ds9.pdf` (source workbook), and `.claude/launch.json` (preview config).
- Deliberately left the unrelated untracked items (`apps/budget2/.gitignore`, `apps/budget2/scripts/__pycache__/`, and the personal `.claude/settings.local.json`) out of the PR.
- Commit message has no agent co-author, per your global instructions.

One thing worth flagging for review: the PR includes the **7 MB source PDF**. I included it so the quiz questions are traceable, but if you'd rather keep the repo lean, say the word and I'll drop it from the branch (the quiz app itself has all the content embedded and doesn't need the PDF at runtime).


---

### 🧔🏻‍♂️ Batu

When I look at the apps/quiz folder, I don't see any other files that you might have created for this app. Where did they go?

### 🤖 Claude

There are no other files - that's by design, not a mislplacement. The entire app is the single file `apps/quiz/quiz.html`. Let me show you exactly what's in the folder:


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== everything in apps/quiz (inc…`  _( List all files in apps/quiz )_

### 🤖 Claude

The folder holds exactly two files, and that's the complete app:

- **`quiz.html`** (43 KB) - the whole application. There is no separate CSS file, JS file, question-data file, or image assets. Everything is inline in this one file:
  - the HTML markup for all three screens (start / quiz / results),
  - the CSS (the pastel styling, inside a `<style>` block),
  - the JavaScript quiz engine,
  - the question data (all 62 written questions + the 24-sign answer mapping, as JS objects),
  - the 24 traffic signs (hand-drawn as inline SVG strings in the JS).
- **`dsd_ds9.pdf`** (7 MB) - the source workbook you dropped in; I only read from it.

This was a deliberate design choice, matching your `budget2` app, which is also a single self-contained `budget.html`. A one-file app has no build step, no dependencies, and no network calls - you just double-click it (or open the file) and it runs. If I'd split it into `index.html` + `styles.css` + `app.js` + `questions.json` + a `signs/` image folder, you'd have ~30 files and would need a local server for the browser to load them.

The only file I created *outside* `apps/quiz/` was `.claude/launch.json` - the small config that lets the browser preview the app. That's tooling, not part of the app itself.

So nothing went missing - the app just is `quiz.html`. If you'd actually prefer it broken out into separate files (e.g. for teaching/readability in the workshop), I'm happy to split it that way. Want me to?


---

### 🧔🏻‍♂️ Batu

nope, you can merge


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && gh pr merge 1 --merge --delete-branch …`  _( Merge PR #1 and delete branch )_

### 🤖 Claude

Merged. Let me confirm the local state is clean.


<sub>*Behind the scenes, Claude:*</sub>
> - Ran command: `cd "/Users/batuhangundogdu/Claude Code Workshop" && echo "=== branch ===" && git branch --…`  _( Verify merge and local state )_

### 🤖 Claude

Merged and cleaned up:

- **PR #1** is `MERGED` into `main`.
- Local checkout is back on `main`, fast-forwarded to the merge commit `25e8d7a`.
- The feature branch was deleted (both remote and local).

The quiz app is now on `main`. Nothing left outstanding.
