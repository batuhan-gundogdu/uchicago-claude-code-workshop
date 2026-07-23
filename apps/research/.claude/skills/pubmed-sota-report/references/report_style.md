# Report style reference

Read this when writing the report body. These rules refine the constraints in SKILL.md.

## Author block (verbatim)

```
Batuhan Gundogdu
University of Chicago, Data Science Institute
```

Single author. No co-authors, no corresponding-author footnote beyond the affiliation.

## Voice and structure

Write in the register of a journal survey: precise, measured, third person. The arc is fixed: first the pioneering work that defined the problem, then the contributions that proved most influential, then the most recent advances and open directions. Attribute every specific claim to a paper in the corpus with `\cite{}`.

## Em dashes are forbidden

Do not use the em dash character in any form. Replace it with a comma, a colon, a pair of parentheses, or two sentences. Scan the finished draft explicitly for stray em dashes before you finish.

## Citations and impact language

- Numbered style, bracketed, in order of appearance. The `sn-mathphys-num` class option produces this automatically from `\cite{}`.
- Keys come only from `references.bib`. If you want to cite something not in the bib, it was not retrieved, so do not cite it.
- References are journal articles (`@article` with journal, year, DOI). Let BibTeX build the reference list; do not hand-format it.
- When you call a paper "most impactful", ground it in the numbers from `corpus.json`: lead with the Relative Citation Ratio (RCR), which is normalized to field and year, and give the raw citation count in support. Do not describe a citation count you cannot see in the corpus.

## Length

At most five pages. Treat roughly 2,500 to 3,000 words as the budget and stay under it. If the material overflows, tighten prose rather than dropping the table or the references.

## The table

Use `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`), a `table*` float if it needs full width, a short `\caption`, and a `\label`. Reference it once from the Related Work section. Keep cells terse. Prefer the `mesh_terms` anatomy descriptor for the Body part column. "not specified" is a valid, honest cell and beats a guess.
