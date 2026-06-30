"""
test_fetcher.py — Quick manual test for news_fetcher.py
────────────────────────────────────────────────────────
Run this from your terminal to verify news_fetcher.py is working:

    python test_fetcher.py

What it checks:
  1. config.py loads without errors
  2. NewsAPI responds successfully
  3. Articles are returned in the correct format
  4. All 5 required fields are present on every article
"""

import sys

print("\n" + "=" * 60)
print("  AI News Agent — Fetcher Test")
print("=" * 60)

# ── Test 1: Config loads ──────────────────────────────────────
print("\n[1/3] Loading configuration...")
try:
    import config
    config.print_config_summary()
    print("✅ Config loaded OK")
except SystemExit:
    print("❌ Config failed — check your .env file")
    sys.exit(1)

# ── Test 2: Fetch articles ────────────────────────────────────
print("\n[2/3] Fetching news articles...")
try:
    import news_fetcher
    articles = news_fetcher.fetch_ai_news()
except Exception as e:
    print(f"❌ news_fetcher crashed with an unexpected error: {e}")
    sys.exit(1)

# ── Test 3: Validate article format ──────────────────────────
print("\n[3/3] Validating article format...")

REQUIRED_FIELDS = ["title", "description", "url", "publishedAt", "source"]

if not articles:
    print("⚠️  No articles returned (check internet / API key)")
else:
    errors = 0
    for i, article in enumerate(articles):
        for field in REQUIRED_FIELDS:
            if field not in article:
                print(f"❌ Article {i+1} is missing field: '{field}'")
                errors += 1

    if errors == 0:
        print(f"✅ All {len(articles)} articles have correct format\n")
    else:
        print(f"❌ {errors} format error(s) found\n")

# ── Print a sample article ────────────────────────────────────
print("=" * 60)
print("  SAMPLE OUTPUT (first 3 articles)")
print("=" * 60)

for i, article in enumerate(articles[:3], start=1):
    print(f"\n[{i}] {article['title']}")
    print(f"     Source : {article['source']}")
    print(f"     Date   : {article['publishedAt']}")
    print(f"     Desc   : {article['description'][:100]}...")
    print(f"     URL    : {article['url']}")

print("\n" + "=" * 60)
if articles:
    print(f"  ✅ SUCCESS: {len(articles)} articles fetched and validated!")
else:
    print("  ⚠️  PARTIAL: Fetcher ran but returned 0 articles")
print("=" * 60 + "\n")
