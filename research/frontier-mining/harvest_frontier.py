"""Harvest + score the recent quant-finance research frontier into a testable shortlist.

Sources (machine-accessible APIs; Scholar via SerpApi - API-key-gated, cost per
query, no scraping of Scholar directly):
  1. arXiv q-fin  (open API)                         - math/method + quant finance working papers
  2. OpenAlex     (free API, indexes SSRN + journals) - captures SSRN-published preprints cleanly
  3. Crossref     (free API, bibliographic)          - journals, meticulous metadata
  4. Google Scholar (via SerpApi, `SERPA_API_KEY`)    - broad Scholar coverage incl. SSRN/working papers

OpenAlex is gated to finance topic T10047 and Crossref to a finance-journal
allowlist; Scholar results are gated in the same way because neither source has
a native discipline scope. ResearchGate has no machine API -> manual/browser only.

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
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ARXIV_API = "http://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"
CROSSREF_API = "https://api.crossref.org/works"
SERPAPI_API = "https://serpapi.com/search.json"
ZENROWS_API = "https://api.zenrows.com/v1/"

# ZenRows costs 5x for js_render and 10x for premium_proxy (SERP scored last).
# We cap calls and pages to keep a sample run cheap on the free credit tier.


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
SSRN_SOURCE = "S4210172589"  # SSRN Electronic Journal in OpenAlex
CATEGORIES = ["q-fin.ST", "q-fin.TR", "q-fin.GN", "q-fin.RM", "q-fin.MF", "q-fin.CP", "q-fin.PM"]
OUT = Path(__file__).resolve().parent / "outputs"
USER_AGENT = "quant-research-funnel/1.0 (mailto:research@example.com)"

# Finance-journal allowlist: Crossref has no discipline scope, so we gate by journal.
# Substrings matched (case-insensitive) against container-title.
FINANCE_JOURNALS = [
    "journal of finance",
    "journal of financial economics",
    "review of financial studies",
    "review of finance",
    "journal of banking",
    "journal of financial and quantitative analysis",
    "journal of empirical finance",
    "financial analysts journal",
    "journal of financial markets",
    "journal of portfolio management",
    "journal of financial research",
    "journal of financial intermediation",
    "critical finance",
    "financial management",
    "journal of money, credit and banking",
    "journal of financial econometrics",
    "mathematical finance",
    "finance and stochastics",
    "journal of financial stability",
    "journal of international money and finance",
    "journal of futures markets",
    "journal of derivatives",
    "journal of economic dynamics and control",
    "journal of applied econometrics",
    "journal of econometrics",
    "journal of business & economic statistics",
    "financial review",
    "european financial management",
    "journal of asset management",
    "journal of risk",
    "quantitative finance",
    "journal of investment management",
    "journal of behavioral finance",
    "journal of financial planning",
    "journal of institutional and theoretical economics",
    "journal of risk and uncertainty",
    "journal of corporate finance",
    "journal of financial services research",
    "journal of risk and financial management",
    "journal of financial economics and banking",
    "journal of applied finance",
]


def _is_finance_journal(container: str) -> bool:
    c = (container or "").lower()
    return any(j in c for j in FINANCE_JOURNALS)


SSRN_URL = re.compile(r"papers\.ssrn\.com/sol3/papers\.cfm\?abstract_id=")
SSRN_DOI = re.compile(r"10\.2139/ssrn")


def _is_ssrn(url: str) -> bool:
    """True if a row is a genuine SSRN working paper (abstract_id URL or SSRN DOI)."""
    u = url or ""
    return bool(SSRN_URL.search(u) or SSRN_DOI.search(u))


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


def _inverted_to_text(inv: dict | None) -> str:
    """Reconstruct text from OpenAlex abstract_inverted_index."""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return _clean(" ".join(pos[i] for i in sorted(pos)))


def fetch_openalex(from_date: str, per_page: int = 50, pages: int = 1) -> list[dict]:
    """Recent finance-topic works from SSRN-in-OpenAlex (free API).

    Gated to OpenAlex topic T10047 (Financial Markets and Investment Strategies)
    so SSRN's multidisciplinary noise (genetics, physics, etc.) is excluded.
    NOTE: no type filter here -- most SSRN works are typed `preprint`, and
    restricting to `type:article` would drop ~75% of the finance content.
    """
    rows = []
    for page in range(1, pages + 1):
        params = {
            "filter": f"locations.source.id:{SSRN_SOURCE},from_publication_date:{from_date},primary_topic.id:T10047",
            "per-page": per_page,
            "page": page,
            "sort": "publication_date:desc",
        }
        r = None
        for attempt in range(3):
            try:
                r = requests.get(OPENALEX_API, params=params, headers={"User-Agent": USER_AGENT}, timeout=90)
            except requests.RequestException:
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                raise
            if r.status_code in (429, 500, 502, 503, 504, 520, 521, 522) and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            break
        if r is not None:
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
                    "abstract": _inverted_to_text(w.get("abstract_inverted_index")),
                    "url": str(w.get("doi") or ""),
                    "source": "ssrn(openalex)",
                    "authors": author,
                    "container": _clean(loc.get("display_name") or src.get("display_name") or ""),
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
    for attempt in range(4):
        r = requests.get(
            CROSSREF_API,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        if r.status_code != 429 or attempt == 3:
            break
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()
    out = []
    for it in r.json()["message"]["items"]:
        container = (it.get("container-title") or [""])[0]
        if not _is_finance_journal(container):
            continue
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
                "journal": container,
            }
        )
    return out


# broad finance-topic signal used to gate Google Scholar results (it has no
# native discipline scope and would otherwise surface ocean/atmospheric/etc.)
SCHOLAR_FINANCE = re.compile(
    r"(stock|equit|shar|quote|index|bond|option|future|derivative|fund|portfolio|"
    r"asset|return|yield|premium|anomaly|momentum|reversal|hedge|volatil|liquid|"
    r"arbitrage|predict|market|invest|bank|credit|spread|collateral|margin|buyback|"
    r"rebalanc|flow|rate|cross.?section|capm|fama|factor|sentiment|mispric|trade)",
    re.I,
)


SCHOLAR_QUERIES = [
    "stock market anomaly forced flow index rebalancing hedging",
    "site:papers.ssrn.com stock anomaly momentum reversal flow",
    "site:papers.ssrn.com market anomaly forced flow hedging rebalancing",
    "site:papers.ssrn.com asset pricing anomaly cross section strategy",
    "site:papers.ssrn.com index rebalancing passive flows price impact",
    "site:papers.ssrn.com momentum reversal value premium factor",
]


def _scholar_query(key: str, q: str, max_results: int, year_lo: int) -> list[dict]:
    params = {
        "engine": "google_scholar",
        "q": q,
        "as_ylo": str(year_lo),
        "num": max_results,
        "api_key": key,
    }
    try:
        r = requests.get(SERPAPI_API, params=params, timeout=90)
    except requests.RequestException as e:
        print(f"SKIP google_scholar query '{q[:40]}': {e}")
        return []
    if r.status_code != 200:
        print(f"SKIP google_scholar query '{q[:40]}': HTTP {r.status_code} ({r.text[:120]})")
        return []
    out = []
    for it in r.json().get("organic_results", []):
        title = _clean(it.get("title") or "")
        if not title or not SCHOLAR_FINANCE.search(title):
            continue
        info = it.get("publication_info") or {}
        summary = info.get("summary") or ""
        if summary and not SCHOLAR_FINANCE.search(summary):
            continue
        year = ""
        m = re.search(r"(19|20)\d{2}", summary or "")
        if m:
            year = m.group(0)
        out.append(
            {
                "date": year + "-01-01" if year else "",
                "title": title,
                "abstract": _clean(it.get("snippet") or ""),
                "url": it.get("link") or "",
                "source": "scholar(serpapi)",
                "journal": summary,
            }
        )
    return out


def fetch_scholar_serpapi(max_results: int = 30) -> list[dict]:
    """Recent Google Scholar results via SerpApi (requires SERPA_API_KEY).

    Runs several queries incl. an SSRN-scoped one so recent SSRN papers that
    OpenAlex lags on are covered via the licensed SerpApi route (no SSRN
    scraping). Dedupes by URL.
    """
    key = os.environ.get("SERPA_API_KEY") or os.environ.get("SERPAPI_KEY")
    if not key:
        print("SKIP google_scholar: SERPA_API_KEY not set (source the repo .env)")
        return []
    year_lo = datetime.now(timezone.utc).year - 1
    per = max(5, max_results // len(SCHOLAR_QUERIES))
    seen: set[str] = set()
    out = []
    for q in SCHOLAR_QUERIES:
        rows = _scholar_query(key, q, per, year_lo)
        for r in rows:
            u = r["url"]
            if u in seen:
                continue
            seen.add(u)
            out.append(r)
    return out


# SSRN finance queries run through ZenRows against SSRN's own search UI
# (searchresults.cfm?term=...). This reads SSRN's real results + posted dates,
# closing the "exhaustive/up-to-date SSRN" gap that OpenAlex/SerpApi lag on.
SSRN_ZENROWS_QUERIES = [
    "market anomaly",
    "momentum reversal",
    "forced flow index rebalancing",
    "asset pricing cross section",
    "volatility trading flow",
]


def _parse_ssrn_date(s: str) -> str:
    """Parse SSRN 'Posted: 24 Jul 2025' -> '%Y-%m-%d' (drop if unparseable)."""
    try:
        return datetime.strptime(s.strip(), "%d %b %Y").strftime("%Y-%m-%d")
    except Exception:
        return ""


def _zenrows_get(key: str, url: str, wait_ms: int = 10000, retries: int = 2) -> str:
    """Fetch a URL through ZenRows with JS render + premium proxy; retry on fail."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(
                ZENROWS_API,
                params={
                    "apikey": key,
                    "url": url,
                    "js_render": "true",
                    "premium_proxy": "true",
                    "wait": str(wait_ms),
                },
                timeout=150,
            )
            if r.status_code == 200 and r.text:
                return r.text
        except requests.RequestException:
            pass
        if attempt < retries:
            time.sleep(3 * (attempt + 1))
    return ""


# tight finance signal for SSRN titles read via ZenRows: SSRN term= search matches
# by 'flow'/'return' broadly, so require a strong finance token, NOT bare 'flow'/'return'.
# Avoid false positives: 'Liquid' (gas-liquid eng), 'invest' inside 'investigation'.
SSRN_FINANCE = re.compile(
    r"(stock|equit|share|quote|index|bond|option|future|derivative|fund|portfolio|asset|"
    r"market|trading|dealer|bank|credit|spread|collateral|margin|buyback|rebalanc|"
    r"anomal|momentum|reversal|hedg|volatil|liquidit|arbitrage|mispric|sentiment|"
    r"capm|fama|factor|carry|premium|yield|investor|investment|investing|"
    r"cross.?section|pric|expect)",
    re.I,
)


def fetch_ssrn_zenrows(max_results: int = 100) -> list[dict]:
    """Recent SSRN search results via ZenRows (requires ZENROW_API_KEY).

    Reads SSRN's own searchresults.cfm for several finance queries, parsing title,
    abstract_id URL, and posted dates, then filtering to the recency window.
    ZenRows is the anti-bot route (js_render 5x + premium_proxy 10x credits).
    """
    key = os.environ.get("ZENROW_API_KEY")
    if not key:
        print("SKIP ssrn_zenrows: ZENROW_API_KEY not set (source the repo .env)")
        return []
    import urllib.parse as up
    seen: set[str] = set()
    out: list[dict] = []
    per = max(10, min(50, max_results // len(SSRN_ZENROWS_QUERIES)))
    for q in SSRN_ZENROWS_QUERIES:
        url = "https://papers.ssrn.com/searchresults.cfm?term=" + up.quote(q)
        html = _zenrows_get(key, url)
        if not html:
            print(f"  zenrows: no content for query '{q}'")
            continue
        # title ~ <a href=...abstract_id=N>Title</a>
        for aid, title in re.findall(r'abstract_id=(\d+)[^>]*>(.*?)</a>', html, re.S):
            tt = _clean(re.sub(r"<[^>]+>", "", title))
            # finance-domain gate: SSRN term= search matches broadly (lava, tires,
            # gas flow, convection) so keep only finance-relevant titles.
            if not tt or not SSRN_FINANCE.search(tt):
                continue
            u = f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={aid}"
            if u in seen:
                continue
            seen.add(u)
            # posted date nearest after this result
            date = ""
            m = re.search(r"Posted[s]?:?\s*(\d{1,2}\s+\w+\s+\d{4})", html[html.find(aid): html.find(aid) + 900])
            if m:
                date = _parse_ssrn_date(m.group(1))
            out.append(
                {
                    "date": date,
                    "title": tt,
                    "abstract": "",
                    "url": u,
                    "source": "ssrn(zenrows)",
                    "journal": "SSRN",
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
    p.add_argument("--scholar-results", type=int, default=30)
    p.add_argument("--zenrows-results", type=int, default=100)
    p.add_argument("--sources", default="arxiv,openalex,crossref,scholar,ssrn_zenrows")
    p.add_argument("--out", default=str(OUT / "frontier_papers.csv"))
    args = p.parse_args()

    _load_dotenv()
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
    if "scholar" in srcs:
        time.sleep(0.5)
        rows += fetch_scholar_serpapi(max_results=args.scholar_results)
    if "ssrn_zenrows" in srcs:
        time.sleep(0.5)
        rows += fetch_ssrn_zenrows(max_results=args.zenrows_results)

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if df.empty:
        print("no rows harvested")
        return 0
    meta = [score(r, args.days) for r in rows]
    for k in ["score", "forced", "documented", "empirical", "method", "data_heavy", "recent", "age_days"]:
        df[k] = [m[k] for m in meta]
    df = df.sort_values("score", ascending=False)
    df["is_ssrn"] = df["url"].astype(str).map(_is_ssrn)
    df.to_csv(args.out, index=False)
    df.to_parquet(Path(args.out).with_suffix(".parquet"))

    print(f"harvested {len(df)} papers from {sorted(df['source'].unique())}; recent (<={args.days}d): {int(df['recent'].sum())}; true SSRN: {int(df['is_ssrn'].sum())}")
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
