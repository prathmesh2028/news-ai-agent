"""
news_fetcher.py — News Article Fetcher
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Connects to NewsAPI (newsapi.org) and downloads the latest AI and tech news.
  Returns a clean, standardised Python list of articles that the rest of the
  pipeline (summarizer, email_sender) can work with.

WHAT THIS FILE DOES NOT DO:
  - It does NOT summarise articles (that's summarizer.py)
  - It does NOT send emails (that's email_sender.py)
  - It only fetches and cleans raw news data.

HOW TO TEST THIS FILE IN ISOLATION:
  Run directly from the terminal:
      python news_fetcher.py

  It will print the fetched articles to the terminal so you can verify
  everything is working before wiring it into the full pipeline.

NEWSAPI DOCS: https://newsapi.org/docs/endpoints/everything
═══════════════════════════════════════════════════════════════════════════════
"""

import requests                # For making HTTP requests to the NewsAPI
import datetime                # For timestamps in error messages
from typing import Optional    # For type hints — helps readability

# Import our settings from config.py (the single source of truth).
# We never hardcode API keys here — they live in .env only.
import config
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# The base URL for the NewsAPI "everything" endpoint.
# "everything" lets us search by keyword across thousands of sources.
# Alternative endpoint: "top-headlines" (only major outlets, less flexible).
NEWSAPI_URL = "https://newsapi.org/v2/everything"

# How many seconds to wait for NewsAPI to respond before giving up.
# If the server is slow or down, we don't want to hang forever.
REQUEST_TIMEOUT_SECONDS = 10


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Build the request parameters for one query
# ─────────────────────────────────────────────────────────────────────────────

def _build_params(query: str, max_articles: int) -> dict[str, any]:
    """
    Build the dictionary of URL parameters for a single NewsAPI request.

    NewsAPI accepts parameters like ?q=...&sortBy=...&apiKey=... in the URL.
    Using a dict is cleaner — the `requests` library builds the URL for us.

    Args:
        query       : The search keyword(s), e.g. "artificial intelligence"
        max_articles: How many articles to request (NewsAPI calls this pageSize)

    Returns:
        A dict of parameters ready to pass to requests.get(params=...)
    """
    return {
        "q":          query,           # Search keyword(s)
        "sortBy":     "publishedAt",   # Sort by newest first
        "language":   "en",            # English articles only
        "pageSize":   max_articles,    # Max articles to return
        "apiKey":     config.NEWS_API_KEY,  # Our secret key from .env
    }


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Normalise a raw NewsAPI article into our standard format
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_article(raw: dict[str, any]) -> Optional[dict[str, str]]:
    """
    Convert a raw article dict from NewsAPI into our clean, standard format.

    Why do we need this?
    NewsAPI returns raw JSON with many fields we don't need (author, urlToImage,
    content, etc.) and some that might be null/None. This function:
      1. Picks only the 5 fields we care about.
      2. Skips articles that are missing title or URL (useless without them).
      3. Cleans up None values so downstream code never crashes on missing data.

    Args:
        raw: A single article dict straight from the NewsAPI JSON response.

    Returns:
        A clean article dict, or None if the article should be skipped.
    """
    title = raw.get("title", "").strip()
    url   = raw.get("url",   "").strip()

    # Skip articles with no title or URL — they're unusable.
    if not title or not url:
        return None

    # Skip NewsAPI's placeholder "[Removed]" articles (deleted/paywalled).
    if title == "[Removed]" or url == "https://removed.com":
        return None

    return {
        "title":       title,
        "description": (raw.get("description") or "No description available.").strip(),
        "url":         url,
        "publishedAt": raw.get("publishedAt", "Unknown date"),
        "source":      raw.get("source", {}).get("name", "Unknown source"),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Make one HTTP request to NewsAPI for a given query
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_single_query(query: str, max_articles: int) -> list[dict[str, any]]:
    """
    Send one request to NewsAPI and return a list of normalised articles.

    This function handles ALL possible failure modes so the caller never
    needs to deal with raw exceptions:
      - No internet connection → returns []
      - NewsAPI is slow/down   → returns [] (after timeout)
      - Invalid API key (401)  → prints a clear message, returns []
      - Rate limit hit (429)   → prints a clear message, returns []
      - Empty results          → returns []
      - Any other error        → prints details, returns []

    Args:
        query       : The search keyword string
        max_articles: How many articles to fetch for this query

    Returns:
        A list of clean article dicts. Empty list if anything goes wrong.
    """
    params = _build_params(query, max_articles)

    try:
        # ── Make the HTTP GET request ──────────────────────────────────────
        # timeout= tells requests to give up after N seconds.
        # Without this, the program could hang indefinitely if NewsAPI is slow.
        response = requests.get(
            NEWSAPI_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        # ── Handle HTTP error codes ────────────────────────────────────────
        # HTTP status codes tell us what went wrong:
        #   200 = OK (success)
        #   401 = Unauthorised (bad API key)
        #   429 = Too Many Requests (rate limited)
        #   500 = NewsAPI server error
        if response.status_code == 401:
            msg = (
                "\n❌ [NewsAPI] Invalid API key (401 Unauthorised).\n"
                "   Check that NEWS_API_KEY in your .env file is correct.\n"
                "   Get a key at: https://newsapi.org/register\n"
            )
            print(msg)
            logger.error("NewsAPI invalid API key (401 Unauthorized)")
            return []

        if response.status_code == 429:
            msg = (
                "\n⚠️  [NewsAPI] Rate limit reached (429 Too Many Requests).\n"
                "   You've made too many requests. Wait a minute and try again.\n"
                "   Free tier limit: 100 requests/day.\n"
            )
            print(msg)
            logger.warning("NewsAPI rate limit reached (429 Too Many Requests)")
            return []

        if response.status_code != 200:
            msg = (
                f"\n⚠️  [NewsAPI] Unexpected response: HTTP {response.status_code}\n"
                f"   Query: '{query}'\n"
                f"   Message: {response.text[:200]}\n"
            )
            print(msg)
            logger.error(f"NewsAPI error: HTTP {response.status_code} for query '{query}'")
            return []

        # ── Parse the JSON response ────────────────────────────────────────
        # NewsAPI returns JSON like:
        #   { "status": "ok", "totalResults": 42, "articles": [...] }
        data = response.json()

        if data.get("status") != "ok":
            print(
                f"\n⚠️  [NewsAPI] API returned an error status.\n"
                f"   Code: {data.get('code')}\n"
                f"   Message: {data.get('message')}\n"
            )
            return []

        raw_articles = data.get("articles", [])

        if not raw_articles:
            print(f"   ℹ️  [NewsAPI] No articles found for query: '{query}'")
            return []

        # ── Normalise each raw article ─────────────────────────────────────
        # We use a list comprehension with a filter:
        #   [f(x) for x in items if condition]
        # _normalise_article returns None for bad articles, so we filter those out.
        clean_articles = [
            article
            for raw in raw_articles
            if (article := _normalise_article(raw)) is not None
        ]

        return clean_articles

    except requests.exceptions.ConnectionError as error:
        # Raised when there's no internet connection or DNS can't resolve the host.
        print(
            "\n❌ [NewsAPI] No internet connection.\n"
            "   Please check your network and try again.\n"
        )
        logger.error(f"NewsAPI ConnectionError: {error}")
        return []

    except requests.exceptions.Timeout as error:
        # Raised when the server didn't respond within REQUEST_TIMEOUT_SECONDS.
        print(
            f"\n❌ [NewsAPI] Request timed out after {REQUEST_TIMEOUT_SECONDS}s.\n"
            "   NewsAPI may be slow or down. Try again in a moment.\n"
        )
        logger.error(f"NewsAPI request timed out: {error}")
        return []

    except requests.exceptions.RequestException as error:
        # Catch-all for any other requests-related error.
        print(f"\n❌ [NewsAPI] Unexpected network error: {error}\n")
        logger.error(f"NewsAPI RequestException: {error}")
        return []

    except Exception as error:
        # Last resort — catch anything we didn't anticipate.
        print(f"\n❌ [NewsAPI] Unexpected error while fetching '{query}': {error}\n")
        logger.error(f"Unexpected error in _fetch_single_query for '{query}': {error}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Deduplicate articles by URL
# ─────────────────────────────────────────────────────────────────────────────

def _deduplicate(articles: list[dict[str, any]]) -> list[dict[str, any]]:
    """
    Remove duplicate articles that appear across multiple queries.

    Why do we need this?
    We run multiple search queries (e.g., "artificial intelligence" AND
    "machine learning"). A popular article might appear in both result sets.
    We use the article's URL as the unique identifier since each article
    has one canonical URL.

    Args:
        articles: A flat list of article dicts, possibly with duplicates.

    Returns:
        A new list with each URL appearing only once (first occurrence kept).
    """
    seen_urls = set()   # A set is like a list but only stores UNIQUE values.
    unique = []

    for article in articles:
        url = article["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)

    return unique


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PUBLIC FUNCTION: fetch_ai_news()
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ai_news() -> list[dict[str, any]]:
    """
    Fetch the latest AI and tech news from NewsAPI.

    This is the ONLY function other modules need to call.
    All the complexity of multiple queries, deduplication, and splitting
    between tech and breaking news is handled here internally.

    Strategy (driven by config.py settings):
      1. Run each query in config.NEWS_PRIMARY_QUERIES to get tech/AI news.
      2. Run config.NEWS_BREAKING_QUERY to catch urgent non-tech news.
      3. Merge and deduplicate all results.
      4. Split by NEWS_TECH_RATIO (default 80% tech, 20% breaking).
      5. Return the final list capped at NEWS_MAX_ARTICLES.

    Returns:
        A list of article dicts, each containing:
          - title       (str): Headline of the article
          - description (str): Short summary from the news source
          - url         (str): Link to the full article
          - publishedAt (str): ISO 8601 timestamp, e.g. "2026-06-30T05:00:00Z"
          - source      (str): Publisher name, e.g. "TechCrunch"

        Returns an empty list [] if all fetches fail (never raises exceptions).
    """
    print("\n🔍 Fetching AI & Tech news...")

    # ── Phase 1: Fetch primary tech/AI articles ────────────────────────────
    # We ask for a small number per query so we don't hit rate limits.
    # articles_per_query: split our budget across the number of queries.
    n_primary = len(config.NEWS_PRIMARY_QUERIES)
    # Allocate total tech slots according to the ratio (default 80% of budget).
    tech_budget  = int(config.NEWS_MAX_ARTICLES * config.NEWS_TECH_RATIO) + 2
    # +2 extra buffer because dedup will remove some articles.
    articles_per_query = max(3, tech_budget // n_primary)

    tech_articles = []
    for query in config.NEWS_PRIMARY_QUERIES:
        print(f"   📡 Querying: '{query}'")
        results = _fetch_single_query(query, articles_per_query)
        tech_articles.extend(results)

    # ── Phase 2: Fetch breaking/urgent non-tech news ───────────────────────
    # Calculate how many slots are left for breaking news.
    breaking_budget = config.NEWS_MAX_ARTICLES - int(
        config.NEWS_MAX_ARTICLES * config.NEWS_TECH_RATIO
    )
    breaking_budget = max(1, breaking_budget)  # Always at least 1 slot

    print(f"   📡 Querying breaking news...")
    breaking_articles = _fetch_single_query(
        config.NEWS_BREAKING_QUERY,
        breaking_budget + 2,  # +2 buffer for dedup losses
    )

    # ── Phase 3: Deduplicate each category separately ─────────────────────
    tech_articles     = _deduplicate(tech_articles)
    breaking_articles = _deduplicate(breaking_articles)

    # ── Phase 4: Apply ratio split ─────────────────────────────────────────
    # Take the first N tech articles, then the first M breaking articles.
    # math is: total = N + M = NEWS_MAX_ARTICLES
    tech_count     = int(config.NEWS_MAX_ARTICLES * config.NEWS_TECH_RATIO)
    breaking_count = config.NEWS_MAX_ARTICLES - tech_count

    selected_tech     = tech_articles[:tech_count]
    selected_breaking = breaking_articles[:breaking_count]

    # ── Phase 5: Merge and final dedup (just in case) ─────────────────────
    # Tech articles come first (higher priority in the digest).
    all_articles = _deduplicate(selected_tech + selected_breaking)

    # ── Final cap ─────────────────────────────────────────────────────────
    final = all_articles[:config.NEWS_MAX_ARTICLES]

    # ── Summary ───────────────────────────────────────────────────────────
    if final:
        print(
            f"\n✅ Fetched {len(final)} articles "
            f"({len(selected_tech)} tech/AI + up to {len(selected_breaking)} breaking)\n"
        )
        logger.info(
            f"Successfully fetched and filtered {len(final)} articles "
            f"({len(selected_tech)} tech/AI, {len(selected_breaking)} breaking)"
        )
    else:
        print(
            "\n⚠️  No articles fetched. Possible reasons:\n"
            "   • No internet connection\n"
            "   • Daily NewsAPI quota reached (100 requests)\n"
            "   • Invalid API key in .env\n"
        )
        logger.warning("No articles fetched from NewsAPI during run")

    return final


# ─────────────────────────────────────────────────────────────────────────────
#  QUICK TEST: Run this file directly to see articles in the terminal
# ─────────────────────────────────────────────────────────────────────────────
# This block only runs when you execute:   python news_fetcher.py
# It does NOT run when other files import this module.
# This is a Python best practice for making modules testable in isolation.

if __name__ == "__main__":
    # Show the config first so we know what settings are in use.
    config.print_config_summary()

    # Fetch the news.
    articles = fetch_ai_news()

    if not articles:
        print("No articles to display.")
    else:
        print("=" * 70)
        print(f"  RESULTS: {len(articles)} Articles Fetched")
        print("=" * 70)

        for i, article in enumerate(articles, start=1):
            # Format the timestamp into something readable.
            # NewsAPI gives us "2026-06-30T05:00:00Z" — we make it "Jun 30, 2026"
            try:
                dt = datetime.datetime.fromisoformat(
                    article["publishedAt"].replace("Z", "+00:00")
                )
                published = dt.strftime("%b %d, %Y %H:%M UTC")
            except Exception:
                published = article["publishedAt"]

            print(f"\n[{i}] {article['title']}")
            print(f"     Source : {article['source']}")
            print(f"     Date   : {published}")
            print(f"     Desc   : {article['description'][:120]}...")
            print(f"     URL    : {article['url']}")

        print("\n" + "=" * 70)
        print("  ✅ news_fetcher.py is working correctly!")
        print("=" * 70 + "\n")
