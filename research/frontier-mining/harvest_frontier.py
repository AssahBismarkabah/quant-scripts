"""Harvest + score the recent quant-finance research frontier into a testable shortlist.

Sources (all free, machine-accessible APIs - no scraping, no ToS risk):
  1. arXiv q-fin  (open API)                         - math/method + quant finance working papers
  2. OpenAlex     (free API, indexes SSRN + journals) - captures SSRN-published preprints cleanly
  3. Crossref     (free API, bibliographic)          - journals, meticulous metadata

Together these cover the widely-used portals (SSRN/CrossRef/arXiv) without browser
automation. Google Scholar has no index and blocks scrapers -> it stays a manual/
browser-only item (documented, not scraped).

Scoring applies the market-edge framework's pillars to each paper:
  (a) forced/mandate counterparty
  (b) documented mechanism
  (c) data testable by us free/cheap + enough events
  (d) plausibly non-decayed (recent / fresh)
Output: ranked shortlist of candidates worth a full research pass.
Suppress future lint as needed; this is a research tool.
"""

from __future__ import annotations

import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ARXIV_API = "http://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"
CROSSREF_API = "https://api.crossref.org/works"
SSRN_SOURCE = "S4210172589"  # SSRN Electronic Journal in OpenAlex
CATEGORIES = ["q-fin.ST", "q-fin.TR", "q-fin.GN", "q-fin.RM", "q-fin.MF", "q-fin.CP", "q-fin.PM"]
OUT = Path(__file__).resolve().parent / "outputs"
USER_AGENT = "quant-research-funnel/1.0 (mailto:research@example.com)"


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def fetch_arxiv(cats: list[str], max_results: int) -> list[dict]:
    query = " OR ".join(f"cat:{c}" for c in cats)
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_results,
    }
    r = requests.get(ARXIV_API, params=params, headers={"User-Agent": "research"}, timeout=60)
    r.raise_for_status()
    rows = []
    for e in re.findall(r"<entry>(.*?)</entry>", r.text, re.S):
        def g(pat):
            m = re.search(pat, e, re.S)
            return m.group(1) if m else ""
        title = _clean(re.sub(r"<.*?>", "", g(r"<title>(.*?)</title>")))
        abstract = _clean(re.sub(r"<.*?>", "", g(r"<summary>(.*?)</summary>")))
        pub = g(r"<published>(.*?)</published>")
        link = g(r"<id>(.*?)</id>")
        rows.append({"date": pub[:10] if pub else "", "title": title, "abstract": abstract, "url": link, "source": "arxiv"})
    return rows


def fetch_openalex(from_date: str, per_page: int = 100, pages: int = 1) -> list[dict]:
    """Recent works whose primary location is SSRN (covers SSRN preprints), free API."""
    rows = []
    for page in range(1, pages + 1):
        params = {
            "filter": f"locations.source.id:{SSRN_SOURCE},from_publication_date:{from_date},type:article",
            "search": "market OR anomaly OR return OR flow OR rebalancing OR hedging OR momentum OR reversal OR carry",
            "per-page": per_page,
            "page": page,
            "sort": "publication_date:desc",
        }
        r = requests.get(OPENALEX_API, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        r.raise_for_status()
        d = r.json()
        for w in d.get("results", []):
            loc = w.get("primary_location") or {}
            src = loc.get("source") or {}
            author = ""
            try:
                authl = (w.get("authorships") or [])
                author = (authl[0].get("author") or {}).get("display_name", "") if authl else ""
            except Exception:
                author = ""
            rows.append(
                {
                    "date": (w.get("publication_date") or "")[:10],
                    "title": _clean(w.get("title") or ""),
                    "abstract": _clean(((w.get("abstract_inverted_index") or {}) and "") or (w.get("title") or "")),
                    "url": "https://doi.org/" + str(w.get("doi")) if w.get("doi") else "",
                    "source": "ssrn(openalex)",
                    "authors": author,
                }
            )
        if not d.get("results") or page >= 1 and pages == 1:
            break
    return rows


def fetch_crossref(from_date: str, rows: int = 100) -> list[dict]:
    """Recent journal works from Crossref (free)."""
    params = {
        "query": "stock market anomaly forced flow rebalancing hedging momentum reversal carry",
        "filter": f"from-pub-date:{from_date},type:journal-article",
        "rows": rows,
        "select": "title,DOI,container-title,published",
    }
    r = None
    for attempt in range(3):
        r = requests.get(
            CROSSREF_API,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        if r.status_code != 429 or attempt == 2:
            break
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()
    out = []
    for it in r.json()["message"]["items"]:
        pubd = (it.get("published") or {}).get("date-parts", [[None]])[0]
        y = pubd[0] if isinstance(pubd, list) and pubd else None
        m = pubd[1] if isinstance(pubd, list) and len(pubd) > 1 else 1
        dte = f"{y:04d}-{m:02d}-01" if y else ""
        out.append(
            {
                "date": dte,
                "title": _clean((it.get("title") or [""])[0]),
                "abstract": "",
                "url": "https://doi.org/" + (it.get("DOI") or ""),
                "source": "crossref",
                "journal": (it.get("container-title") or [""])[0],
            }
        )
    return out


# ---- scorecard (see module docstring) ----
FORCED_FLOW = re.compile(
    r"(forced|mandat|rebalanc|hedging|dealer|index fund|passive|buyback|repurchase|"
    r"margin|collateral|liquidation|settlement|withdraw|expiry|roll|flow|convex|window.?dress|"
    r"reconstitution|passive inflow|ETF flow)",
    re.I,
)
DOCUMENTED = re.compile(
    r"(effect|anomal|return|premium|drift|arbitrage|mispri|predict|reversal|momentum|carry|"
    r"spread|impact|abnormal)",
    re.I,
)
DATA_HEAVY = re.compile(r"(intraday|order.?flow|tick|microstructure|high.?frequenc|secret|private data|proprietary)", re.I)
METHOD = re.compile(
    r"(conformal|optimal transport|signature|topological|neural|deep learning|foundation model|"
    r"machine learning|stochastic control|optimal control|stopping|martingale|measure-the|"
    r"asymptotic|gaussian boson|quantum|tsbootstrap|volatility surface|interpolat|goodness-of-fit|"
    r"markov|ergodic|estimation|forecasting model|probabilistic forecasting|implied vol|fractional|"
    r"LLM|large language|regulation|policy|ESG|climate|real estate|crypto tokenomics)",
    re.I,
)
EMPIRICAL = re.compile(
    r"(anomal|return predict|predictability|reversal|momentum|drift|carry|premium|arbitrage|"
    r"out-of-sample|out of sample|event|long-run|short-run|dealer|index|hedg|buyback|rebalance|"
    r"forced|flow|mandate|mispric|abnormal|threshold|passive)",
    re.I,
)


def text_hit(t: str, pat: re.Pattern) -> bool:
    return bool(pat.search(t))


def score(row: dict, days: int) -> dict:
    blob = row["title"] + " " + row.get("abstract", "") + " " + row.get("journal", "")
    forced = text_hit(blob, FORCED_FLOW)
    documented = text_hit(blob, DOCUMENTED)
    empirical = text_hit(blob, EMPIRICAL)
    data_heavy = text_hit(blob, DATA_HEAVY)
    method = text_hit(blob, METHOD)
    try:
        d = datetime.strptime(row["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - d).days
    except Exception:
        age = days + 1
    recent = age <= days
    s = 0.0
    if forced:
        s += 3
    if documented:
        s += 2
    if empirical:
        s += 2
    if not data_heavy:
        s += 1
    if recent:
        s += 1
    if method:
        s -= 4
    return {
        "score": s,
        "forced": forced,
        "documented": documented,
        "empirical": empirical,
        "method": method,
        "data_heavy": data_heavy,
        "recent": recent,
        "age_days": age,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--max-arxiv", type=int, default=300)
    p.add_argument("--openalex-pages", type=int, default=1)
    p.add_argument("--crossref-rows", type=int, default=60)
    p.add_argument("--sources", default="arxiv,openalex,crossref")
    p.add_argument("--out", default=str(OUT / "frontier_papers.csv"))
    args = p.parse_args()

    from datetime import timedelta
    from_date = (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()

    rows: list[dict] = []
    srcs = [x.strip() for x in args.sources.split(",")]
    if "arxiv" in srcs:
        rows += fetch_arxiv(CATEGORIES, args.max_arxiv)
    if "openalex" in srcs:
        rows += fetch_openalex(from_date, pages=args.openalex_pages)
    if "crossref" in srcs:
        time.sleep(0.5)
        rows += fetch_crossref(from_date, rows=args.crossref_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if df.empty:
        print("no rows harvested")
        return 0
    meta = [score(r, args.days) for r in rows]
    for k in ["score", "forced", "documented", "empirical", "method", "data_heavy", "recent", "age_days"]:
        df[k] = [m[k] for m in meta]
    df = df.sort_values("score", ascending=False)
    df.to_csv(args.out, index=False)
    df.to_parquet(Path(args.out).with_suffix(".parquet"))

    print(f"harvested {len(df)} papers from {sorted(df['source'].unique())}; recent (<={args.days}d): {int(df['recent'].sum())}")
    print(f"\n=== TOP TESTABLE CANDIDATES (empirical, non-method, non-data-heavy) ===")
    short = df[(df["empirical"]) & (~df["method"]) & (~df["data_heavy"])].head(15)
    for _, r in short.iterrows():
        print(f"[{r['score']:.0f}] {r['date']} {r['source']:18}| {r['title'][:70]}")
        if r.get("url"):
            print(f"      {r['url']}")
    print("\nsaved:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
