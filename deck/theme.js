/**
 * deck-style — UChicago MS-ADS house style for pptxgenjs decks.
 * Copied from lecture-1.pptx.
 *
 * Type: Calibri throughout. Cover title 60pt bold; page titles 50pt bold;
 * body 28pt. White background. Semantic color palette (black/blue/green/maroon).
 * UChicago footer lockup on every slide; phoenix bleeds off the right edge of
 * the title slide. Calibri is Office-safe, so QA renders are true-to-width.
 */
const pptxgen = require("pptxgenjs");
const path = require("path");
const ASSET = (f) => path.join(__dirname, "assets", f);

// ---- TOKENS -----------------------------------------------------------------
const COLOR = {
  BG: "FFFFFF",
  INK: "000000",     // headings + default body
  BLUE: "1F4E79",    // subtitle/author (deep blue, per cover)
  ACCENTBLUE: "0070C0", // questions / emphasis body
  GREEN: "00B050",   // callouts
  MAROON: "800000",  // labels ("Lecture-1"), UChicago maroon
  MUTE: "808080",
};

const FONT = "Calibri"; // headings (bold) and body both Calibri

const SIZE = {
  TITLE: 60,   // cover headline
  H: 50,       // page/content-slide title
  SUB: 20,     // cover subtitle/author
  LABEL: 40,   // cover "Lecture-N" maroon label
  BODY: 28,
  SMALL: 24,
  STAT: 140,
};

const M = 0.6;
const W = 13.33, HGT = 7.5;

// exact placements copied from the reference (EMU -> inches)
const FOOTER  = { x: 0.59, y: 6.98, w: 3.11, h: 0.52 };
const PHOENIX = { x: 9.09, y: 0.82, w: 6.31, h: 5.52 }; // bleeds off right edge
const CTITLE  = { x: 1.00, y: 1.31, w: 8.32, h: 2.61 };
const CSUB    = { x: 1.04, y: 4.03, w: 6.07, h: 0.68 };

// ---- SETUP ------------------------------------------------------------------
function newDeck(opts = {}) {
  const p = new pptxgen();
  p.defineLayout({ name: "WIDE", width: W, height: HGT });
  p.layout = "WIDE";
  p.author = opts.author || "";
  p.title = opts.title || "";
  p._brand = (opts.brand || "generic").toLowerCase(); // "generic" | "uchicago"
  p.defineSlideMaster({ title: "BASE", background: { color: COLOR.BG } });
  return p;
}

// Footer lockup, stamped directly on each slide so PowerPoint always shows it
// (master/layout graphics from pptxgenjs don't reliably render in PowerPoint).
function addFooter(s) {
  s.addImage({ path: ASSET("uchicago-footer.png"), x: FOOTER.x, y: FOOTER.y, w: FOOTER.w, h: FOOTER.h });
}

// Page title: Calibri Bold 50, black, top-left.
function heading(s, text) {
  s.addText(text || "", {
    x: M, y: 0.4, w: W - 2 * M, h: 1.3,
    fontFace: FONT, fontSize: SIZE.H, bold: true, color: COLOR.INK,
    align: "left", valign: "top", margin: 0,
  });
}

// ---- SLIDE BUILDERS ---------------------------------------------------------

// Title slide: Calibri 60 bold title, deep-blue author, maroon lecture label,
// phoenix bleeding off the right edge (matches the reference layout exactly).
function titleSlide(p, { title, author, label } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (p._brand === "uchicago") addFooter(s);
  if (p._brand === "uchicago") {
    s.addImage({ path: ASSET("phoenix.png"), x: PHOENIX.x, y: PHOENIX.y, w: PHOENIX.w, h: PHOENIX.h, transparency: 60 });
  }
  s.addText(title || "", {
    x: CTITLE.x, y: CTITLE.y, w: CTITLE.w, h: CTITLE.h,
    fontFace: FONT, fontSize: SIZE.TITLE, bold: true, color: COLOR.INK,
    align: "left", valign: "middle", margin: 0, lineSpacingMultiple: 1.0,
  });
  if (author) {
    s.addText(author, {
      x: CSUB.x, y: CSUB.y, w: CSUB.w, h: CSUB.h,
      fontFace: FONT, fontSize: SIZE.SUB, color: COLOR.BLUE,
      align: "left", valign: "top", margin: 0,
    });
  }
  if (label) {
    s.addText(label, {
      x: 3.0, y: 5.4, w: 5.0, h: 0.9,
      fontFace: FONT, fontSize: SIZE.LABEL, bold: true, color: COLOR.MAROON,
      align: "left", valign: "top", margin: 0,
    });
  }
  return s;
}

// Section divider: maroon kicker + big black Calibri bold title.
function section(p, { kicker, title } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (p._brand === "uchicago") addFooter(s);
  if (kicker) {
    s.addText(String(kicker).toUpperCase(), {
      x: M, y: 2.7, w: W - 2 * M, h: 0.5,
      fontFace: FONT, fontSize: SIZE.SMALL, color: COLOR.MAROON,
      charSpacing: 2, align: "left", valign: "bottom", margin: 0,
    });
  }
  s.addText(title || "", {
    x: M, y: 3.2, w: W - 2 * M, h: 1.6,
    fontFace: FONT, fontSize: SIZE.H, bold: true, color: COLOR.INK,
    align: "left", valign: "top", margin: 0,
  });
  return s;
}

// Content: heading + body. points may be strings or {text, color}.
// color one of: INK | ACCENTBLUE | GREEN | MAROON | BLUE
function content(p, { title, points = [] } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (p._brand === "uchicago") addFooter(s);
  heading(s, title);
  if (points.length) {
    s.addText(
      points.map((pt) => {
        const o = typeof pt === "string" ? { text: pt } : pt;
        return { text: o.text, options: { color: COLOR[o.color || "INK"] || COLOR.INK, bullet: false, paraSpaceAfter: 18, breakLine: true } };
      }),
      { x: M, y: 2.1, w: W - 2 * M, h: HGT - 2.1 - 0.7,
        fontFace: FONT, fontSize: SIZE.BODY, align: "left", valign: "top", margin: 0, lineSpacingMultiple: 1.1 }
    );
  }
  return s;
}

// Two-column content.
function twoColumn(p, { title, left, right } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (p._brand === "uchicago") addFooter(s);
  heading(s, title);
  const colW = (W - 2 * M - 0.6) / 2;
  const block = (items, x) =>
    s.addText(
      (items || []).map((pt) => {
        const o = typeof pt === "string" ? { text: pt } : pt;
        return { text: o.text, options: { color: COLOR[o.color || "INK"] || COLOR.INK, paraSpaceAfter: 16, breakLine: true } };
      }),
      { x, y: 2.1, w: colW, h: HGT - 2.1 - 0.7, fontFace: FONT, fontSize: SIZE.BODY, align: "left", valign: "top", margin: 0, lineSpacingMultiple: 1.1 }
    );
  block(left, M);
  block(right, M + colW + 0.6);
  return s;
}

// Stat: giant maroon Calibri number + label.
function stat(p, { value, label } = {}) {
  const s = p.addSlide({ masterName: "BASE" });
  if (p._brand === "uchicago") addFooter(s);
  s.addText(String(value), {
    x: M, y: 1.7, w: W - 2 * M, h: 3.0,
    fontFace: FONT, fontSize: SIZE.STAT, bold: true, color: COLOR.MAROON,
    align: "left", valign: "middle", margin: 0,
  });
  if (label) {
    s.addText(label, {
      x: M, y: 4.8, w: W - 2 * M, h: 1.0,
      fontFace: FONT, fontSize: SIZE.SMALL, color: COLOR.INK,
      align: "left", valign: "top", margin: 0,
    });
  }
  return s;
}

module.exports = { COLOR, FONT, SIZE, W, H: HGT, M, newDeck, addFooter, heading, titleSlide, section, content, twoColumn, stat };
