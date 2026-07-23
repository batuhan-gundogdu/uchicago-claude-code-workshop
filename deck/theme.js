/**
 * "simple" — minimalist deck style for pptxgenjs.
 * White background, generous whitespace, Avenir Next, one muted-teal accent.
 *
 * Signature elements (from the reference template):
 *  - small uppercase gray micro-label (kicker) with a short teal rule under it
 *  - big bold black page titles, pinned top-left
 *  - a giant faint watermark word behind the cover title
 *  - teal used sparingly for emphasis, section numbers, and the stat figure
 *
 * Semantic point colors from the old house style are remapped:
 *  INK -> black · ACCENTBLUE/GREEN -> teal (emphasis) · MAROON -> black bold
 *  (punchlines) · BLUE -> gray. So build.js keeps working unchanged.
 */
const pptxgen = require("pptxgenjs");

// ---- TOKENS -----------------------------------------------------------------
const COLOR = {
  BG:   "FFFFFF",
  INK:  "111111",   // titles + default body
  MUTE: "9A9A9A",   // micro-labels, subtitles
  TEAL: "2E7A72",   // the single accent
  WM:   "F1F2F1",   // watermark ghost text
};

const FONT = "Avenir Next";

const SIZE = {
  TITLE: 54,    // cover headline
  WM:    210,   // cover watermark word
  SUB:   14,    // cover subtitle (uppercase, gray)
  LABEL: 14,    // cover teal label
  H:     40,    // page/content title
  KICKER:12,    // micro-label
  SECNUM:15,    // section kicker
  SECTITLE:44,  // section title
  BODY:  20,
  SMALL: 15,
  STAT:  130,
};

const W = 13.33, HGT = 7.5;
const M = 0.9;                 // airy left/right margin
const RULE_W = 0.62;           // length of the teal accent rule

// point-color remap: old semantic name -> { color, bold }
const POINT = {
  INK:        { color: COLOR.INK },
  ACCENTBLUE: { color: COLOR.TEAL },
  GREEN:      { color: COLOR.TEAL },
  MAROON:     { color: COLOR.INK, bold: true },
  BLUE:       { color: COLOR.MUTE },
  MUTE:       { color: COLOR.MUTE },
  TEAL:       { color: COLOR.TEAL },
};
const styleFor = (name) => POINT[name] || POINT.INK;

// ---- SETUP ------------------------------------------------------------------
function newDeck(opts = {}) {
  const p = new pptxgen();
  p.defineLayout({ name: "WIDE", width: W, height: HGT });
  p.layout = "WIDE";
  p.author = opts.author || "";
  p.title = opts.title || "";
  p.defineSlideMaster({ title: "BASE", background: { color: COLOR.BG } });
  return p;
}

// short teal accent rule (a thin rectangle)
function rule(s, x, y, w = RULE_W) {
  s.addShape("rect", { x, y, w, h: 0.045, fill: { color: COLOR.TEAL }, line: { type: "none" } });
}

// micro-label + rule; returns the y where the title should start
function kickerBlock(s, kicker, x = M, y = 0.72) {
  if (!kicker) return 1.2;
  s.addText(String(kicker).toUpperCase(), {
    x, y, w: W - 2 * M, h: 0.3,
    fontFace: FONT, fontSize: SIZE.KICKER, bold: true, color: COLOR.MUTE,
    charSpacing: 2.5, align: "left", valign: "top", margin: 0,
  });
  rule(s, x, y + 0.34);
  return y + 0.55;
}

// Page title: Avenir Next Bold, black, top-left (below optional kicker).
function heading(s, text, y = 1.2) {
  s.addText(text || "", {
    x: M, y, w: W - 2 * M, h: 1.3,
    fontFace: FONT, fontSize: SIZE.H, bold: true, color: COLOR.INK,
    align: "left", valign: "top", margin: 0, lineSpacingMultiple: 0.98,
  });
}

// ---- SLIDE BUILDERS ---------------------------------------------------------

// Title slide: giant faint watermark word + bold title + gray subtitle + teal label.
function titleSlide(p, { title, author, label, watermark } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (watermark) {
    s.addText(String(watermark).toLowerCase(), {
      x: -0.4, y: 1.4, w: W + 0.8, h: 4.6,
      fontFace: FONT, fontSize: SIZE.WM, bold: true, color: COLOR.WM,
      align: "left", valign: "middle", margin: 0,
    });
  }
  s.addText(title || "", {
    x: M, y: 2.55, w: W - 2 * M, h: 2.0,
    fontFace: FONT, fontSize: SIZE.TITLE, bold: true, color: COLOR.INK,
    align: "left", valign: "middle", margin: 0, lineSpacingMultiple: 1.0,
  });
  rule(s, M, 4.62, 1.0);
  if (author) {
    s.addText(String(author).toUpperCase(), {
      x: M, y: 4.8, w: W - 2 * M, h: 0.6,
      fontFace: FONT, fontSize: SIZE.SUB, color: COLOR.MUTE,
      charSpacing: 1.5, align: "left", valign: "top", margin: 0,
    });
  }
  if (label) {
    s.addText(String(label).toUpperCase(), {
      x: M, y: 5.5, w: W - 2 * M, h: 0.5,
      fontFace: FONT, fontSize: SIZE.LABEL, bold: true, color: COLOR.TEAL,
      charSpacing: 2, align: "left", valign: "top", margin: 0,
    });
  }
  return s;
}

// Section divider: teal kicker + big black title, centered vertically.
function section(p, { kicker, title } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (kicker) {
    s.addText(String(kicker).toUpperCase(), {
      x: M, y: 2.75, w: W - 2 * M, h: 0.4,
      fontFace: FONT, fontSize: SIZE.SECNUM, bold: true, color: COLOR.TEAL,
      charSpacing: 3, align: "left", valign: "bottom", margin: 0,
    });
    rule(s, M, 3.2);
  }
  s.addText(title || "", {
    x: M, y: 3.4, w: W - 2 * M, h: 1.6,
    fontFace: FONT, fontSize: SIZE.SECTITLE, bold: true, color: COLOR.INK,
    align: "left", valign: "top", margin: 0, lineSpacingMultiple: 0.98,
  });
  return s;
}

// Content: optional kicker + heading + body. points: strings or {text,color}.
function content(p, { title, kicker, points = [] } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  const ty = kickerBlock(s, kicker);
  heading(s, title, ty);
  if (points.length) {
    s.addText(
      points.map((pt) => {
        const o = typeof pt === "string" ? { text: pt } : pt;
        const st = styleFor(o.color);
        return { text: o.text, options: { color: st.color, bold: !!st.bold, bullet: false, paraSpaceAfter: 16, breakLine: true } };
      }),
      { x: M, y: ty + 1.4, w: W - 2 * M, h: HGT - (ty + 1.4) - 0.5,
        fontFace: FONT, fontSize: SIZE.BODY, align: "left", valign: "top", margin: 0, lineSpacingMultiple: 1.15 }
    );
  }
  return s;
}

// Two-column content.
function twoColumn(p, { title, kicker, left, right } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  const ty = kickerBlock(s, kicker);
  heading(s, title, ty);
  const colW = (W - 2 * M - 0.8) / 2;
  const by = ty + 1.4;
  const block = (items, x) =>
    s.addText(
      (items || []).map((pt) => {
        const o = typeof pt === "string" ? { text: pt } : pt;
        const st = styleFor(o.color);
        return { text: o.text, options: { color: st.color, bold: !!st.bold, paraSpaceAfter: 14, breakLine: true } };
      }),
      { x, y: by, w: colW, h: HGT - by - 0.5, fontFace: FONT, fontSize: SIZE.BODY, align: "left", valign: "top", margin: 0, lineSpacingMultiple: 1.15 }
    );
  block(left, M);
  block(right, M + colW + 0.8);
  return s;
}

// Stat: giant teal figure + label.
function stat(p, { value, label, kicker } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  const ty = kickerBlock(s, kicker);
  s.addText(String(value), {
    x: M - 0.05, y: 1.5, w: W - 2 * M, h: 3.2,
    fontFace: FONT, fontSize: SIZE.STAT, bold: true, color: COLOR.TEAL,
    align: "left", valign: "middle", margin: 0,
  });
  if (label) {
    s.addText(label, {
      x: M, y: 4.9, w: W - 2 * M - 2.0, h: 1.4,
      fontFace: FONT, fontSize: SIZE.SMALL, color: COLOR.INK,
      align: "left", valign: "top", margin: 0, lineSpacingMultiple: 1.2,
    });
  }
  return s;
}

module.exports = { COLOR, FONT, SIZE, W, H: HGT, M, newDeck, heading, titleSlide, section, content, twoColumn, stat };
