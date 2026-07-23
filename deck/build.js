// UChicago × Anthropic - "Talk to Your Computer" intro workshop deck.
// Minimalist "simple" style via ./theme (Avenir Next, one teal accent).
// Build:  node build.js   ->  writes workshop.pptx
const T = require("./theme");

const p = T.newDeck({
  title: "Talk to Your Computer",
  author: "Batuhan Gundogdu",
  brand: "generic",
});

// 1. TITLE
T.titleSlide(p, {
  title: "Talk to Your Computer",
  watermark: "talk",
  author: "Claude Code for everyday work  ·  UChicago × Anthropic  ·  Batuhan Gundogdu",
  label: "Intro Session",
});

// 2. THE POLL (Poll Everywhere QR goes here)
T.content(p, {
  title: "First - who's in the room?",
  kicker: "Warm-up poll",
  points: [
    { text: "Scan the QR and pick one.  [ Poll Everywhere QR - top right ]", color: "MAROON" },
    { text: "" },
    { text: "1 · I already use it every day - here to see what else it can do.", color: "GREEN" },
    { text: "2 · I don't know much - having my FOMO right now.", color: "ACCENTBLUE" },
    { text: "3 · I'm a skeptic - don't think much of it, but here I am anyway.", color: "INK" },
  ],
});

// 3. SECTION - the big idea
T.section(p, { kicker: "Part one", title: "The one big idea" });

// 4. Big idea
T.content(p, {
  title: "It's not a coding tool. It's a conversation.",
  kicker: "The big idea",
  points: [
    { text: "You describe what you want, in plain English.", color: "ACCENTBLUE" },
    { text: "It builds the thing - a page, a tracker, a tool.", color: "INK" },
    { text: "You want it different? You just say so.", color: "GREEN" },
    { text: "" },
    { text: "You never have to look at the code.", color: "MAROON" },
  ],
});

// 5. Myth vs reality
T.twoColumn(p, {
  title: "What people assume vs. what's true",
  kicker: "Myths vs reality",
  left: [
    { text: "The assumption", color: "MAROON" },
    "“It's for programmers.”",
    "“I'll have to learn to code.”",
    "“It'll break and I won't know why.”",
  ],
  right: [
    { text: "The reality", color: "MAROON" },
    { text: "It's for anyone with a task.", color: "GREEN" },
    { text: "You describe; it writes.", color: "GREEN" },
    { text: "You say “that's wrong, fix it.”", color: "GREEN" },
  ],
});

// 6. Light tease
T.content(p, {
  title: "One small thing before we start…",
  kicker: "Before we start",
  points: [
    { text: "These slides were made by talking to Claude Code.", color: "ACCENTBLUE" },
    { text: "So were the four apps you're about to see.", color: "ACCENTBLUE" },
    { text: "" },
    { text: "Hold that thought. We'll come back to it.", color: "MAROON" },
  ],
});

// 7. SECTION - the demos
T.section(p, { kicker: "Part two", title: "Let's build four everyday tools" });

// 8. Demo roadmap
T.content(p, {
  title: "Four tools, built live, in front of you",
  kicker: "The plan",
  points: [
    { text: "1 · A budget controller - track money, see a chart.", color: "INK" },
    { text: "2 · A research paper tracker - what to read, what's done.", color: "INK" },
    { text: "3 · A daily dashboard - todos, reminders, nudges.", color: "INK" },
    { text: "4 · A teaching assistant - turn a topic into a quiz.", color: "INK" },
    { text: "" },
    { text: "Watch for the moment I change the look - just by asking.", color: "GREEN" },
  ],
});

// 9-12. One divider per app (Batu switches to Claude Code after each)
T.section(p, { kicker: "Demo 1", title: "Budget Controller" });
T.section(p, { kicker: "Demo 2", title: "Research Paper Tracker" });
T.section(p, { kicker: "Demo 3", title: "Daily Dashboard" });
T.section(p, { kicker: "Demo 4", title: "Teaching Assistant" });

// 13. The recurring beat
T.content(p, {
  title: "Don't like it? Just say so.",
  kicker: "The recurring beat",
  points: [
    { text: "“Make it dark.”", color: "ACCENTBLUE" },
    { text: "“Move the total to the top.”", color: "ACCENTBLUE" },
    { text: "“Add a pie chart.”", color: "ACCENTBLUE" },
    { text: "" },
    { text: "No menus. No settings. No code. Just words.", color: "GREEN" },
  ],
});

// 14. SECTION - the reveal
T.section(p, { kicker: "Part three", title: "The reveal" });

// 15. The brag (stat)
T.stat(p, {
  value: "1",
  kicker: "The whole thing",
  label: "Claude Code session built this whole workshop - these slides and all four apps. No template. No help. Just conversation.",
});

// 16. How you start Monday
T.content(p, {
  title: "How you start - Monday morning",
  kicker: "Getting started",
  points: [
    { text: "Open Claude Code. Type what you wish existed.", color: "ACCENTBLUE" },
    { text: "Start tiny: a checklist, a tracker, a page.", color: "INK" },
    { text: "When it's not quite right, tell it - in plain words.", color: "INK" },
    { text: "" },
    { text: "The only skill required is describing what you want.", color: "MAROON" },
  ],
});

// 17. Closer
T.content(p, {
  title: "Your turn",
  kicker: "Your turn",
  points: [
    { text: "Open Claude Code. Describe the thing you wish existed.", color: "ACCENTBLUE" },
    { text: "You just watched me do it - no code, no template.", color: "INK" },
    { text: "" },
    { text: "Go build something you wished existed.", color: "GREEN" },
  ],
});

p.writeFile({ fileName: "workshop.pptx" }).then((f) => console.log("wrote", f));
