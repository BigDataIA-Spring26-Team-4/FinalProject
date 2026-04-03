"""
POC 2: GDELT Geopolitical Event Extraction & EDA
==================================================
Queries GDELT 2.0 Doc API for maritime/shipping-related news articles
and performs exploratory data analysis.

Prerequisites:
    No API key required — GDELT Doc API is free and open.

Usage:
    poetry run python poc/poc2_gdelt_eda.py
"""

import sys
import time
from datetime import datetime, timedelta

print("🚢 Maritime AI Sentinel — POC 2: GDELT Geopolitical EDA")
print(f"{'=' * 60}")

try:
    from gdeltdoc import GdeltDoc, Filters
    import pandas as pd
except ImportError:
    print("❌ Required packages not installed. Run: poetry install")
    sys.exit(1)

# ── Configuration ──
MARITIME_KEYWORDS = [
    "shipping route disruption",
    "strait of hormuz",
    "maritime chokepoint",
    "red sea attack",
    "suez canal shipping",
    "naval blockade",
    "port congestion delay",
    "houthi ship attack",
    "vessel sanctions OFAC",
    "maritime security threat",
]

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=30)


def query_gdelt_with_retry(keyword: str, max_records: int = 250, retries: int = 2) -> pd.DataFrame:
    """Query GDELT Doc API with retry logic and delay between calls."""
    gd = GdeltDoc()
    for attempt in range(retries + 1):
        try:
            f = Filters(
                keyword=keyword,
                start_date=START_DATE.strftime("%Y-%m-%d"),
                end_date=END_DATE.strftime("%Y-%m-%d"),
                num_records=max_records,
            )
            articles = gd.article_search(f)
            return articles
        except Exception as e:
            if attempt < retries:
                wait = 3 * (attempt + 1)
                print(f" (retry in {wait}s)...", end="", flush=True)
                time.sleep(wait)
            else:
                print(f" ⚠️ Failed: {str(e)[:60]}", end="")
                return pd.DataFrame()
    return pd.DataFrame()


def main():
    # ═══════════════════════════════════════════
    # 1. Collect articles across all maritime keywords
    # ═══════════════════════════════════════════
    print(f"\n📡 Querying GDELT Doc API for maritime events...")
    print(f"   Date range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"   Keywords: {len(MARITIME_KEYWORDS)}")
    print(f"   Retry: up to 2 retries per keyword with backoff")
    print()

    all_articles = []
    keyword_counts = {}

    for i, keyword in enumerate(MARITIME_KEYWORDS):
        print(f"  🔍 [{i + 1}/{len(MARITIME_KEYWORDS)}] '{keyword}'...", end=" ", flush=True)

        # Delay between requests to avoid GDELT throttling
        if i > 0:
            time.sleep(2)

        df = query_gdelt_with_retry(keyword, max_records=250)
        count = len(df)
        keyword_counts[keyword] = count
        if count > 0:
            df["search_keyword"] = keyword
            all_articles.append(df)
        print(f"→ {count} articles")

    if not all_articles:
        print("\n❌ No articles found. GDELT API may be temporarily unavailable.")
        sys.exit(1)

    # Combine and deduplicate by URL
    df_all = pd.concat(all_articles, ignore_index=True)
    total_before_dedup = len(df_all)
    df_all = df_all.drop_duplicates(subset=["url"], keep="first")
    total_after_dedup = len(df_all)

    print(f"\n{'=' * 60}")
    print(f"📊 EDA RESULTS")
    print(f"{'=' * 60}")

    # ═══════════════════════════════════════════
    # 2. Basic statistics
    # ═══════════════════════════════════════════
    print(f"\n── Dataset Overview ──")
    print(f"  Total articles (raw):          {total_before_dedup}")
    print(f"  Total articles (deduplicated): {total_after_dedup}")
    print(f"  Unique domains:                {df_all['domain'].nunique() if 'domain' in df_all.columns else 'N/A'}")
    print(f"  Keywords with results:         {sum(1 for c in keyword_counts.values() if c > 0)}/{len(MARITIME_KEYWORDS)}")

    if "seendate" in df_all.columns:
        df_all["date"] = pd.to_datetime(df_all["seendate"], format="%Y%m%dT%H%M%S", errors="coerce")
        date_range = df_all["date"].dropna()
        if len(date_range) > 0:
            print(f"  Date range:                    {date_range.min().strftime('%Y-%m-%d')} to {date_range.max().strftime('%Y-%m-%d')}")

    # ═══════════════════════════════════════════
    # 3. Articles per keyword
    # ═══════════════════════════════════════════
    print(f"\n── Articles per Keyword ──")
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    for keyword, count in sorted_keywords:
        bar = "█" * (count // 10) if count > 0 else "░"
        print(f"  {keyword:<30s} {count:>4d}  {bar}")

    # ═══════════════════════════════════════════
    # 4. Top source domains
    # ═══════════════════════════════════════════
    if "domain" in df_all.columns:
        print(f"\n── Top 15 Source Domains ──")
        top_domains = df_all["domain"].value_counts().head(15)
        for domain, count in top_domains.items():
            print(f"  {domain:<40s} {count:>4d}")

    # ═══════════════════════════════════════════
    # 5. Top source countries
    # ═══════════════════════════════════════════
    if "sourcecountry" in df_all.columns:
        print(f"\n── Top 10 Source Countries ──")
        top_countries = df_all["sourcecountry"].value_counts().head(10)
        for country, count in top_countries.items():
            print(f"  {country:<30s} {count:>4d}")

    # ═══════════════════════════════════════════
    # 6. Language distribution
    # ═══════════════════════════════════════════
    if "language" in df_all.columns:
        print(f"\n── Language Distribution ──")
        top_langs = df_all["language"].value_counts().head(10)
        for lang, count in top_langs.items():
            print(f"  {lang:<20s} {count:>4d}")

    # ═══════════════════════════════════════════
    # 7. Sample articles
    # ═══════════════════════════════════════════
    print(f"\n── Sample Articles (first 10) ──")
    sample_cols = ["title", "domain", "seendate"]
    available_cols = [c for c in sample_cols if c in df_all.columns]
    if available_cols:
        for _, row in df_all[available_cols].head(10).iterrows():
            title = str(row.get("title", "N/A"))[:80]
            domain = str(row.get("domain", "N/A"))
            date = str(row.get("seendate", "N/A"))[:10]
            print(f"  [{date}] {domain:<25s} {title}")

    # ═══════════════════════════════════════════
    # 8. Data volume estimation
    # ═══════════════════════════════════════════
    memory_mb = df_all.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"\n── Data Volume ──")
    print(f"  DataFrame memory:    {memory_mb:.2f} MB ({total_after_dedup} articles)")
    print(f"  Columns:             {list(df_all.columns)}")
    print(f"  Note: This is the Doc API (article metadata only).")
    print(f"  Full pipeline uses GDELT Events + GKG via BigQuery = ~550 MB/day")

    # ═══════════════════════════════════════════
    # 9. Save to CSV for further analysis
    # ═══════════════════════════════════════════
    output_path = "poc/gdelt_maritime_articles.csv"
    df_all.to_csv(output_path, index=False)
    print(f"\n💾 Saved {total_after_dedup} articles to {output_path}")

    print(f"\n{'=' * 60}")
    print(f"✅ POC 2 complete — real GDELT data via Doc API")
    print(f"   This proves: API connectivity, data volume, EDA feasibility")
    print(f"   Next: Ingest GDELT Events + GKG via BigQuery for full 45+ GB pipeline")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
