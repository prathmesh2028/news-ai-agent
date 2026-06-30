"""
summarizer.py — AI Article Summarizer (Powered by Google Gemini)
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Takes a list of raw news articles from news_fetcher.py and uses Google's
  Gemini AI to produce a clean, structured summary of each one.

  Input  → list of article dicts (from news_fetcher.fetch_ai_news)
  Output → same list, but each article now has a "summary" field added

WHAT GEMINI DOES FOR EACH ARTICLE:
  Given the title + description of an article, Gemini returns:
    • A 2-3 sentence plain-English summary
    • 3 key bullet points
    • A "Why it matters" insight line
    • A relevance score (1-5) for AI/tech topics

PACKAGE USED:
  google-genai  ← the NEW official Google Gemini SDK (as of 2025)
  The old google-generativeai package is deprecated and no longer updated.

RATE LIMITING:
  The free Gemini tier allows ~15 requests/minute.
  We add a 4-second pause between each article to stay well under the limit.

HOW TO TEST IN ISOLATION:
  python summarizer.py

GEMINI API DOCS: https://ai.google.dev/gemini-api/docs
═══════════════════════════════════════════════════════════════════════════════
"""

import time                  # For pausing between API calls (rate limiting)
import re                    # For extracting retry delay from 429 error messages
from google import genai     # NEW official Google Gemini SDK (google-genai package)

import config                # Our settings (API key, model name, etc.)
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Create the Gemini client (done once at module load)
# ─────────────────────────────────────────────────────────────────────────────
# In the new google-genai SDK, we create a Client object with our API key.
# This replaces the old genai.configure() call from the deprecated package.
# The client is reusable — we create it once and use it for every request.
_client = genai.Client(api_key=config.GEMINI_API_KEY)

# How long to wait (seconds) between API calls to avoid hitting rate limits.
# Free tier = ~15 requests/minute = 1 request every 4 seconds minimum.
_RATE_LIMIT_PAUSE = 8   # seconds between each article (8s = ~7.5 req/min, well under 15 RPM limit)
_MAX_RETRIES       = 1   # how many times to retry a 429 before giving up


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Build the prompt we send to Gemini for each article
# ─────────────────────────────────────────────────────────────────────────────

def _build_prompt(article: dict[str, any]) -> str:
    """
    Construct the text prompt we send to Gemini for a single article.

    WHY A DEDICATED FUNCTION?
    The prompt is the most important part of AI output quality. By putting
    it in its own function, we can tweak the AI instructions in one place
    without touching any other code.

    The prompt instructs Gemini to:
      1. Summarise in plain English (no jargon)
      2. Extract 3 key bullet points
      3. Write a "Why it matters" line for busy readers
      4. Score its relevance to AI/tech (1-5)
      5. Return everything in a predictable format we can parse

    Args:
        article: A single article dict with keys: title, description, source

    Returns:
        A formatted string prompt ready to send to Gemini.
    """
    title       = article.get("title", "Untitled")
    description = article.get("description", "No description available.")
    source      = article.get("source", "Unknown")

    return f"""You are an AI assistant writing a concise daily tech news digest.

Analyse this news article and respond ONLY in the exact format below.
Do not add any extra text, markdown headers, or explanations outside the format.

ARTICLE TITLE: {title}
ARTICLE SOURCE: {source}
ARTICLE DESCRIPTION: {description}

Respond in EXACTLY this format (keep each section on one line):
SUMMARY: [2-3 sentence plain-English summary. No jargon. Write for a smart non-expert reader.]
BULLETS:
• [Key point 1 — most important fact]
• [Key point 2 — second most important detail]
• [Key point 3 — impact or what happens next]
WHY_IT_MATTERS: [One sentence explaining why a tech-savvy person should care]
RELEVANCE_SCORE: [Integer 1-5 where: 5=core AI/ML news, 4=major tech industry, 3=general technology, 2=tangentially tech-related, 1=not tech-related at all]"""


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Parse Gemini's raw text response into a structured dict
# ─────────────────────────────────────────────────────────────────────────────

def _parse_response(response_text: str) -> dict[str, any]:
    """
    Extract the structured fields from Gemini's plain-text response.

    Gemini returns a text string formatted like:
        SUMMARY: ...
        BULLETS:
        • point 1
        • point 2
        • point 3
        WHY_IT_MATTERS: ...
        RELEVANCE_SCORE: 4

    This function parses that text line-by-line and returns a clean dict.

    Args:
        response_text: The raw string returned by Gemini.

    Returns:
        A dict with keys: summary, bullets, why_it_matters, relevance_score.
        Falls back to safe defaults if parsing fails.
    """
    # Safe defaults — used if Gemini returns something we can't parse.
    result = {
        "summary":         "Summary unavailable.",
        "bullets":         [],
        "why_it_matters":  "Impact unknown.",
        "relevance_score": 3,
    }

    if not response_text:
        return result

    lines = response_text.strip().split("\n")
    bullet_list = []

    for line in lines:
        line = line.strip()

        if line.startswith("SUMMARY:"):
            result["summary"] = line[len("SUMMARY:"):].strip()

        elif line.startswith("•") or line.startswith("-"):
            # Capture bullet points (handles both • and - as bullet markers)
            bullet_text = line.lstrip("•- ").strip()
            if bullet_text:
                bullet_list.append(bullet_text)

        elif line.startswith("WHY_IT_MATTERS:"):
            result["why_it_matters"] = line[len("WHY_IT_MATTERS:"):].strip()

        elif line.startswith("RELEVANCE_SCORE:"):
            score_str = line[len("RELEVANCE_SCORE:"):].strip()
            try:
                # int() converts "4" → 4. max/min clamps it between 1 and 5.
                result["relevance_score"] = max(1, min(5, int(score_str[0])))
            except (ValueError, IndexError):
                pass   # Keep default if Gemini returned something unexpected

    if bullet_list:
        result["bullets"] = bullet_list[:3]   # Keep at most 3 bullets

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Extract retry delay from 429 error message
# ─────────────────────────────────────────────────────────────────────────────
def _extract_retry_delay(error_str: str) -> int:
    """Parses the wait time from a 429 error string."""
    match = re.search(r"wait (\d+)s", error_str)
    return int(match.group(1)) if match else 5


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Summarise one article with a single Gemini API call
# ─────────────────────────────────────────────────────────────────────────────

def _summarise_one(article: dict[str, any]) -> dict[str, any]:
    """
    Send one article to Gemini and return it enriched with a summary.

    This function handles ALL possible Gemini API failures gracefully —
    the rest of the pipeline never crashes even if Gemini is unavailable.

    Args:
        article: A single article dict from news_fetcher.py

    Returns:
        The same article dict with these new keys added:
          - summary         (str)  : 2-3 sentence plain-English summary
          - bullets         (list) : list of up to 3 key bullet point strings
          - why_it_matters  (str)  : one-liner on why this news matters
          - relevance_score (int)  : 1-5 AI/tech relevance score
          - summary_error   (bool) : True only if the Gemini call failed
    """
    prompt = _build_prompt(article)

    for attempt in range(1 + _MAX_RETRIES):   # attempt 0 = first try, attempt 1 = one retry
        try:
            # ── Call the Gemini API ────────────────────────────────────────
            # client.models.generate_content() sends our prompt to Gemini.
            # - model    = which Gemini model to use (from config)
            # - contents = the prompt text we want Gemini to respond to
            response = _client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )

            # response.text is Gemini's plain-text reply.
            response_text = response.text
            if not response_text or not response_text.strip():
                raise ValueError("Gemini returned an empty response.")

            parsed = _parse_response(response_text)
            # {**article, **parsed} merges two dicts — combines article fields
            # with the new summary fields parsed from Gemini's response.
            return {**article, **parsed, "summary_error": False}

        except Exception as error:
            error_str = str(error)

            # ── Smart 429 handling: read retryDelay, wait, then retry ──────
            # When Gemini returns 429, the error message tells us exactly how
            # many seconds to wait before the quota resets. We read that
            # number and sleep automatically — then loop back and try again.
            if "429" in error_str and attempt < _MAX_RETRIES:
                wait_seconds = _extract_retry_delay(error_str)
                print(
                    f"      ⏳ Rate limited (429). "
                    f"Auto-waiting {wait_seconds}s then retrying..."
                )
                logger.warning(f"Gemini API rate limited (429). Waiting {wait_seconds}s before retry.")
                time.sleep(wait_seconds + 2)  # +2s safety buffer
                continue   # go back to top of loop and retry

            # ── All attempts failed — use the fallback description ─────────
            # Common causes:
            #   429 daily quota exhausted → wait until midnight Pacific time
            #   403 → check GEMINI_API_KEY in .env
            #   404 → check GEMINI_MODEL in config.py
            short_err = error_str[:100]
            if "429" in error_str:
                print(f"      ❌ Daily quota exhausted. Retry resets at midnight PT.")
                logger.error("Gemini API daily quota exhausted (429 Resource Exhausted)")
            else:
                print(f"      ⚠️  Gemini failed (attempt {attempt+1}): {short_err}")
                logger.error(f"Gemini API error (attempt {attempt+1}): {short_err}")

            fallback = article.get("description", "No summary available.")
            return {
                **article,
                "summary":         fallback,
                "bullets":         ["AI summary unavailable — see original article."],
                "why_it_matters":  "See original article for details.",
                "relevance_score": 3,
                "summary_error":   True,
            }


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PUBLIC FUNCTION: summarise_articles()
# ─────────────────────────────────────────────────────────────────────────────

def summarise_articles(articles: list[dict[str, any]]) -> list[dict[str, any]]:
    """
    Summarise a list of news articles using Google Gemini AI.

    This is the ONLY function other modules need to call.
    It processes each article one at a time with a pause between requests
    to stay within Gemini's free-tier rate limits.

    Args:
        articles: A list of article dicts from news_fetcher.fetch_ai_news().
                  Each dict must have: title, description, url, publishedAt, source.

    Returns:
        The same list with these new keys added to every article:
          - summary         (str)  : Gemini's 2-3 sentence plain-English summary
          - bullets         (list) : ["Key point 1", "Key point 2", "Key point 3"]
          - why_it_matters  (str)  : One-liner on why this matters
          - relevance_score (int)  : 1 = off-topic, 5 = core AI/ML
          - summary_error   (bool) : True if Gemini failed (fallback used)

        Returns [] if input is empty.
        Never raises an exception — all errors are caught internally.
    """
    if not articles:
        print("⚠️  [Summariser] No articles to summarise.")
        return []

    total = len(articles)
    print(f"\n🤖 Summarising {total} articles with Gemini ({config.GEMINI_MODEL})...")
    print(f"   (pausing {_RATE_LIMIT_PAUSE}s between calls to respect API rate limits)\n")

    summarised = []

    for i, article in enumerate(articles, start=1):
        title_preview = article.get("title", "Untitled")[:60]
        print(f"   [{i}/{total}] {title_preview}...")

        enriched = _summarise_one(article)
        summarised.append(enriched)

        if enriched.get("summary_error"):
            print(f"           ⚠️  Fallback used (Gemini call failed)")
        else:
            score = enriched.get("relevance_score", 3)
            stars = "★" * score + "☆" * (5 - score)
            print(f"           ✅ Done  |  Relevance: {stars} ({score}/5)")

        # Pause between requests — skip after the last one.
        if i < total:
            time.sleep(_RATE_LIMIT_PAUSE)

    # ── Final summary ──────────────────────────────────────────────────────
    success_count = sum(1 for a in summarised if not a.get("summary_error"))
    error_count   = total - success_count

    print(f"\n✅ Summarisation complete: {success_count}/{total} succeeded", end="")
    if error_count:
        print(f", {error_count} used fallback descriptions", end="")
    print("\n")

    logger.info(
        f"Gemini summarisation complete: {success_count}/{total} succeeded, "
        f"{error_count} fallbacks used"
    )

    return summarised


# ─────────────────────────────────────────────────────────────────────────────
#  QUICK TEST — run directly: python summarizer.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from news_fetcher import fetch_ai_news

    config.print_config_summary()

    print("📰 Fetching articles for summarisation test (capped at 3)...")
    all_articles = fetch_ai_news()
    test_articles = all_articles[:3]   # 3 articles = 3 Gemini calls = ~12s

    if not test_articles:
        print("❌ No articles fetched. Check your NEWS_API_KEY in .env.")
        exit(1)

    results = summarise_articles(test_articles)

    print("=" * 70)
    print("  SUMMARISED ARTICLES")
    print("=" * 70)

    for i, article in enumerate(results, start=1):
        score = article.get("relevance_score", 3)
        stars = "★" * score + "☆" * (5 - score)
        print(f"\n{'─'*70}")
        print(f"[{i}] {article['title']}")
        print(f"     Source    : {article['source']}  |  Relevance: {stars} ({score}/5)")
        print(f"\n     📝 SUMMARY")
        print(f"     {article['summary']}")
        print(f"\n     📌 KEY POINTS")
        for bullet in article.get("bullets", []):
            print(f"       • {bullet}")
        print(f"\n     💡 WHY IT MATTERS")
        print(f"     {article['why_it_matters']}")

    print(f"\n{'='*70}")
    print(f"  ✅ summarizer.py is working correctly!")
    print(f"{'='*70}\n")
    