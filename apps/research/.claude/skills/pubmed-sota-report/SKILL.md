---
name: pubmed-sota-report
description: Use when the user asks for a literature review, survey, or state-of-the-art report on a biomedical or medical-imaging research topic, especially when they want it formatted to Springer Nature guidelines with proper citations and a categorized table of related work. Retrieves papers from PubMed/MEDLINE with the bundled build_corpus.py script, ranks impact using NIH iCite citation data, and writes a LaTeX report from the Springer sn-jnl template.
---

# PubMed state-of-the-art report

Produce a Springer-formatted state-of-the-art report on a biomedical research topic, sourced from PubMed/MEDLINE, with an impact-ranked narrative and a categorized related-work table. Follow every step and constraint below. They are directives, not suggestions.

## Step 1 — Build the corpus (do this first, always)

Run the bundled fetcher from the working directory:

```bash
python scripts/build_corpus.py "<TOPIC>" --max-results 25 --email <contact-email> --outdir .
```

It performs a PubMed relevance search (`esearch`), fetches full records (`efetch`), and enriches each with NIH iCite citation data. It writes `corpus.json` (title, authors, year, journal, DOI, `pubmed_url`, abstract, `mesh_terms`, `citation_count`, `relative_citation_ratio`, `nih_percentile`) and `references.bib` (BibTeX `@article`, keyed by PMID). Read `corpus.json`; do not paste raw abstracts wholesale. If the fetch fails, stop and report the error rather than writing from memory.

## Step 2 — Analyze the corpus

From `corpus.json` (already relevance-ordered), identify:
- **Pioneers**: the earliest foundational works. Corroborate with a high `citation_count`.
- **Most impactful works**: rank primarily by `relative_citation_ratio` (RCR), which is field- and year-normalized, and report the raw `citation_count` alongside it.
- **Recent advancements**: papers from the last two years.

If `meta.impact_source` is `unavailable` (iCite was unreachable), state plainly in the report that impact ranking is approximate and based on relevance and recency only. Never invent citation numbers.

## Step 3 — Write the report

Copy `templates/report.tex` into the working directory and fill it in. The report must:
- Be at most 5 pages, roughly 2,500 to 3,000 words. Track length by word count, not by guessing pages.
- Contain these sections: Abstract, Introduction, Pioneering Work, Most Impactful Contributions, Recent Advances, Related Work (the table), Conclusion, References.
- Cite only with `\cite{key}` where `key` exists in `references.bib`. Every claim about a specific paper must be supported by that paper's abstract in `corpus.json`. Do not cite anything that was not retrieved.

For detailed formatting and style rules, read `references/report_style.md`.

## Step 4 — Compile to PDF (always finish here)

Do not stop at the `.tex` source. Compile the report to `report.pdf` and confirm it built before you finish.

The report ships with the Springer `sn-jnl` class, which uses BibTeX, so the build has multiple passes. Use whichever toolchain is available:

```bash
# Preferred: a single self-contained command (fetches packages on demand, runs
# the LaTeX and BibTeX passes for you). Install with `brew install tectonic` if missing.
tectonic -X compile report.tex

# Or a classic TeX Live toolchain:
pdflatex report && bibtex report && pdflatex report && pdflatex report
```

After compiling:
- Verify `report.pdf` exists and open the log for errors. Fix any compile error rather than leaving a broken build.
- Sanity-check the rendered output: citations must appear as numbered `[1]` brackets (not author-year), the related-work table must fit the page width, and the reference list must be populated. Render a page to an image if you need to confirm.
- The Springer `sn-jnl.cls` and matching `.bst` are required to build. If they are missing, tell the user where to get them (see Output) and stop; do not fabricate a PDF.

If you had to work around a class or engine incompatibility (for example, missing package loads or a `dvips`-only `breakurl` under a XeTeX engine), document the fix in the `report.tex` preamble so the build stays reproducible.

## Non-negotiable constraints

- **Single author**, exactly as written: Batuhan Gundogdu, University of Chicago Data Science Institute.
- **Never use em dashes.** Use commas, parentheses, or separate sentences instead. Check the finished text before finishing.
- **Numbered Springer citation style** (`[1]`, in order of appearance), handled by the `sn-mathphys-num` class option in the template.
- **Truthful citations only.** No fabricated DOIs, years, findings, or citation numbers. When a fact is not in the retrieved corpus, leave it out.

## The related-work table

Build it only from information present in `corpus.json`. Columns, in order:
1. **Work** — first author "et al." as a hyperlink to `pubmed_url` (e.g. `\href{https://pubmed.ncbi.nlm.nih.gov/30022098/}{Doe et al.}`).
2. **Year** — sort the table ascending by year.
3. **Physics model** — e.g. IVIM, DTI, DKI, NODDI, VERDICT, SMT. Read it from the abstract.
4. **Method** — e.g. NLLS, MLE, physics-informed deep learning, self-supervised learning, dictionary matching, digital twin.
5. **Body part** — e.g. brain, breast, prostate, kidney, liver. The `mesh_terms` field often names the anatomy directly (Brain, Prostate, Kidney), so use it to seed this column.

If a cell cannot be determined from the abstract or MeSH terms, write "not specified". Never guess.

## Output

Leave `report.tex`, `references.bib`, and the compiled `report.pdf` in the working directory. The PDF is the final deliverable: the task is not done until it has been built and verified (Step 4). The Springer `sn-jnl.cls` and matching `.bst` are required to build; they ship with the official Springer Nature LaTeX template (https://www.springernature.com/gp/authors/campaigns/latex-author-support). Tell the user where to get them if they are missing.
