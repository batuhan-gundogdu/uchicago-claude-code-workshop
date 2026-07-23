#!/usr/bin/env python3
"""
Build a literature corpus for a state-of-the-art report, sourced from PubMed/MEDLINE.

Step 1: PubMed esearch -> relevance-ranked PMIDs for the topic.
Step 2: PubMed efetch  -> full records (title, abstract, authors, journal, year, DOI, MeSH).
Step 3: NIH iCite      -> citation_count and Relative Citation Ratio (RCR) per PMID.

Outputs:
  - corpus.json     structured records incl. citation_count and relative_citation_ratio
  - references.bib  BibTeX (@article, keyed by PMID) so the report can only cite
                    papers that were actually retrieved

Only the standard library is used. NCBI asks that you identify your tool and email,
so pass --email. An NCBI API key (optional, --api-key) raises the E-utilities limit
from 3 to 10 requests/second. iCite needs no key. If iCite is unreachable the script
degrades gracefully (citation fields become null) and still produces the corpus.

Usage:
  python build_corpus.py "quantitative MRI-based tissue microstructure profiling" \
      --max-results 25 --email you@uchicago.edu --outdir .
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ICITE = "https://icite.od.nih.gov/api/pubs"
UA = {"User-Agent": "sota-report-skill/1.0"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _common(tool, email, api_key):
    p = {"tool": tool, "email": email}
    if api_key:
        p["api_key"] = api_key
    return p


def _clean(t):
    return re.sub(r"\s+", " ", (t or "").strip())


def esearch(query, retmax, tool, email, api_key):
    params = {"db": "pubmed", "term": query, "retmax": retmax,
              "sort": "relevance", "retmode": "json"}
    params.update(_common(tool, email, api_key))
    data = json.loads(_get(f"{EUTILS}/esearch.fcgi?{urllib.parse.urlencode(params)}"))
    return data.get("esearchresult", {}).get("idlist", [])


def efetch(pmids, tool, email, api_key):
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    params.update(_common(tool, email, api_key))
    raw = _get(f"{EUTILS}/efetch.fcgi?{urllib.parse.urlencode(params)}")
    return parse_pubmed_xml(raw)


def parse_pubmed_xml(raw):
    root = ET.fromstring(raw)
    records = []
    for art in root.findall(".//PubmedArticle"):
        mc = art.find("MedlineCitation")
        if mc is None:
            continue
        article = mc.find("Article")
        if article is None:
            continue
        pmid = mc.findtext("PMID")

        title_el = article.find("ArticleTitle")
        title = _clean("".join(title_el.itertext())) if title_el is not None else ""

        # abstract: join structured sections, prefixing any section label
        abs_parts = []
        for at in article.findall("./Abstract/AbstractText"):
            label = at.get("Label")
            txt = _clean("".join(at.itertext()))
            abs_parts.append(f"{label}: {txt}" if label else txt)
        abstract = _clean(" ".join(abs_parts))

        authors = []
        for a in article.findall("./AuthorList/Author"):
            last = a.findtext("LastName")
            fore = a.findtext("ForeName") or a.findtext("Initials")
            if last:
                authors.append(f"{fore} {last}".strip() if fore else last)

        year = (article.findtext("./Journal/JournalIssue/PubDate/Year")
                or article.findtext("./ArticleDate/Year") or "")
        if not year:
            md = article.findtext("./Journal/JournalIssue/PubDate/MedlineDate") or ""
            m = re.search(r"\d{4}", md)
            year = m.group(0) if m else ""

        journal = _clean(article.findtext("./Journal/Title")
                         or article.findtext("./Journal/ISOAbbreviation") or "")

        doi = None
        for aid in art.findall("./PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = _clean(aid.text)
        if not doi:
            for el in article.findall("ELocationID"):
                if el.get("EIdType") == "doi":
                    doi = _clean(el.text)

        mesh = [_clean(d.text) for d in
                mc.findall("./MeshHeadingList/MeshHeading/DescriptorName") if d.text]

        records.append({
            "pmid": pmid,
            "title": title,
            "authors": authors,
            "first_author": authors[0] if authors else "Unknown",
            "year": year,
            "journal": journal,
            "doi": doi,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": abstract,
            "mesh_terms": mesh,
            "citation_count": None,
            "relative_citation_ratio": None,
            "nih_percentile": None,
        })
    return records


def enrich_icite(records):
    pmids = [r["pmid"] for r in records if r["pmid"]]
    if not pmids:
        return "unavailable"
    by_id = {}
    for i in range(0, len(pmids), 200):  # iCite accepts up to 200 ids per request
        chunk = pmids[i:i + 200]
        params = {"pmids": ",".join(chunk),
                  "fl": "pmid,citation_count,relative_citation_ratio,nih_percentile"}
        try:
            data = json.loads(_get(f"{ICITE}?{urllib.parse.urlencode(params)}"))
        except Exception as e:
            print(f"[warn] iCite unavailable ({e}); continuing without citation data.",
                  file=sys.stderr)
            return "unavailable"
        rows = data.get("data", data) if isinstance(data, dict) else data
        for row in rows:
            by_id[str(row.get("pmid"))] = row
        time.sleep(0.2)
    for r in records:
        row = by_id.get(str(r["pmid"]))
        if row:
            r["citation_count"] = row.get("citation_count")
            r["relative_citation_ratio"] = row.get("relative_citation_ratio")
            r["nih_percentile"] = row.get("nih_percentile")
    return "NIH iCite"


def to_bibtex(records):
    out = []
    for r in records:
        authors = " and ".join(r["authors"]) if r["authors"] else "Unknown"
        fields = [
            f"  title   = {{{{{r['title']}}}}}",
            f"  author  = {{{authors}}}",
            f"  journal = {{{r['journal']}}}",
            f"  year    = {{{r['year']}}}",
        ]
        if r["doi"]:
            fields.append(f"  doi     = {{{r['doi']}}}")
        fields.append(f"  note    = {{PMID: {r['pmid']}}}")
        out.append("@article{pmid" + str(r["pmid"]) + ",\n" + ",\n".join(fields) + "\n}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--max-results", type=int, default=25)
    ap.add_argument("--email", default="", help="contact email (NCBI etiquette)")
    ap.add_argument("--api-key", default="", help="optional NCBI API key (3->10 rps)")
    ap.add_argument("--tool", default="sota-report-skill")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--no-impact", action="store_true")
    args = ap.parse_args()

    print(f"[1/3] PubMed esearch: {args.topic!r}", file=sys.stderr)
    pmids = esearch(args.topic, args.max_results, args.tool, args.email, args.api_key)
    print(f"      {len(pmids)} PMIDs", file=sys.stderr)
    if not pmids:
        print("no results; check the query", file=sys.stderr)
        sys.exit(1)
    time.sleep(0.34)

    print("[2/3] PubMed efetch: records + abstracts + MeSH", file=sys.stderr)
    records = efetch(pmids, args.tool, args.email, args.api_key)

    impact_source = "skipped"
    if not args.no_impact:
        print("[3/3] NIH iCite: citation counts + RCR", file=sys.stderr)
        impact_source = enrich_icite(records)

    corpus = {
        "meta": {
            "query": args.topic,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "count": len(records),
            "source": "PubMed/MEDLINE",
            "impact_source": impact_source,
        },
        "papers": records,
    }
    od = args.outdir.rstrip("/")
    with open(f"{od}/corpus.json", "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    with open(f"{od}/references.bib", "w") as f:
        f.write(to_bibtex(records))
    print(f"wrote {od}/corpus.json and {od}/references.bib", file=sys.stderr)


if __name__ == "__main__":
    main()
