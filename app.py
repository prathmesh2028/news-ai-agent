"""
app.py — Main Pipeline Orchestrator
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  This is the ENTRY POINT for the entire AI News Agent.
  It runs the full pipeline from start to finish, in order:

  1. load_config()       → Validate .env settings
  2. fetch_news()        → Pull latest articles from NewsAPI
  3. summarise_news()    → Send each article to Gemini for summarisation
  4. generate_html()     → Render articles into the beautiful HTML template
  5. send_email_digest() → Dispatch the HTML email via Gmail SMTP
  6. print_summary()     → Show a clean completion report

  Each step is its own function — if one step fails, the error is caught
  and reported clearly without crashing the whole program.

HOW TO RUN:
  python app.py            ← Run the full pipeline once, right now

ARCHITECTURE (one-line summary per module):
  config.py       → reads .env, validates all settings, exposes variables
  news_fetcher.py → calls NewsAPI, returns list of article dicts
  summarizer.py   → calls Gemini API, adds AI summary to each article
  email_sender.py → connects to Gmail SMTP, sends the HTML email
  templates/
    email.html    → Jinja2 HTML template for the email body
═══════════════════════════════════════════════════════════════════════════════
"""

import datetime                              # For timestamps and date formatting
import sys                                   # For sys.exit() on critical failures
from pathlib import Path                     # For clean file path handling
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# ── Our own modules ──────────────────────────────────────────────────────────
# Each import loads a specific module from our project.
# If any module has a syntax error, Python will tell you the filename here.
import config                                # Step 1: settings & validation
from news_fetcher import fetch_ai_news       # Step 2: fetch news articles
from summarizer import (
    summarise_articles,      # Step 3: AI summarisation
    generate_executive_summary,  # Step 3b: executive brief
    generate_ai_quote,           # Step 3c: AI quote
    generate_market_mentions,    # Step 3d: market snapshot
)
from email_sender import send_email          # Step 5: send email
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
TEMPLATE_DIR  = config.TEMPLATE_DIR
TEMPLATE_FILE = config.TEMPLATE_FILE

# Visual separators for the log output — makes it easy to read in terminal
_LINE  = "─" * 60
_DLINE = "═" * 60


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Print a step header
# ─────────────────────────────────────────────────────────────────────────────

def _step(number: int, title: str) -> None:
    """Print a numbered step header to mark progress in the terminal."""
    print(f"\n{_LINE}")
    print(f"  STEP {number}: {title}")
    print(_LINE)


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Load & validate configuration
# ─────────────────────────────────────────────────────────────────────────────

def load_config() -> bool:
    """
    Validate that all required environment variables are loaded correctly.

    config.py runs its validation automatically when it's imported at the
    top of this file. This function just prints a confirmation and lets
    the user see their settings before the pipeline starts.

    Returns:
        True  — config is valid, pipeline can proceed.
        False — a critical setting is missing (config.py already printed why).
    """
    _step(1, "Loading Configuration")

    try:
        # This triggers config.py's validation — if something is missing,
        # it will print an error and raise a SystemExit.
        config.print_config_summary()

        # Extra check: the three most critical secrets must be non-empty.
        missing = []
        if not config.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not config.NEWS_API_KEY:
            missing.append("NEWS_API_KEY")
        if not config.EMAIL_PASSWORD:
            missing.append("EMAIL_PASSWORD")

        if missing:
            print(f"\n❌ Missing critical settings: {', '.join(missing)}")
            print("   Add them to your .env file and try again.")
            logger.error(f"Configuration is missing key environment variables: {', '.join(missing)}")
            return False

        print("\n✅ Configuration is valid — ready to run.")
        logger.info("Configuration loaded and validated successfully.")
        return True

    except SystemExit as error:
        # config.py calls sys.exit() when validation fails.
        # We catch it here so we can return False gracefully.
        logger.error(f"System exit occurred while loading configuration: {error}")
        return False

    except Exception as error:
        print(f"\n❌ Unexpected error loading config: {error}")
        logger.error(f"Unexpected error loading configuration: {error}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Fetch News Articles
# ─────────────────────────────────────────────────────────────────────────────

def fetch_news() -> list[dict[str, any]]:
    """
    Fetch the latest AI and tech news articles from NewsAPI.

    Calls news_fetcher.fetch_ai_news() which runs multiple queries
    (AI, machine learning, big tech, cybersecurity, etc.) and returns
    a deduplicated list of the most relevant articles.

    Returns:
        A list of article dicts. Each dict has:
          title, description, url, publishedAt, source, category
        Returns [] if fetching failed (error already printed by fetcher).
    """
    _step(2, "Fetching Latest News")
    print("📡 Querying NewsAPI endpoints...")

    try:
        articles = fetch_ai_news()

        if not articles:
            print("⚠️  No articles returned. Check your NEWS_API_KEY.")
            return []

        # Show a quick breakdown of what was fetched
        tech_count     = sum(1 for a in articles if a.get("category") == "tech")
        breaking_count = len(articles) - tech_count
        print(f"✅ Fetched {len(articles)} articles  "
              f"({tech_count} tech/AI  +  {breaking_count} breaking)")
        return articles

    except Exception as error:
        print(f"❌ News fetching failed: {error}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3: Summarise Articles with Gemini AI
# ─────────────────────────────────────────────────────────────────────────────

def summarise_news(articles: list[dict[str, any]]) -> list[dict[str, any]]:
    """
    Send each article to Google Gemini for AI summarisation.

    Gemini adds these fields to every article dict:
      - summary         : 2-3 sentence plain-English summary
      - bullets         : list of 3 key bullet points
      - why_it_matters  : one-liner developer insight
      - relevance_score : 1-5 (5 = core AI/ML, 1 = off-topic)
      - summary_error   : True if Gemini failed (fallback description used)

    Args:
        articles: List of raw article dicts from fetch_news().

    Returns:
        The same list, enriched with summary fields.
        If Gemini is unavailable, articles are returned with fallback summaries.
    """
    _step(3, "Summarizing with Gemini")
    print(f"🤖 Enriching articles with {config.GEMINI_MODEL}...")

    try:
        summarised = summarise_articles(articles)

        # Count successes vs fallbacks
        ok  = sum(1 for a in summarised if not a.get("summary_error"))
        err = len(summarised) - ok

        if err == 0:
            print(f"✅ All {ok} articles summarised by Gemini.")
        elif ok == 0:
            print(
                f"⚠️  Gemini summarisation failed for all articles.\n"
                f"   Fallback descriptions will be used in the email.\n"
                f"   (Daily quota may be exhausted — resets at midnight PT)"
            )
        else:
            print(f"⚠️  {ok} summarised by Gemini, {err} used fallback descriptions.")

        return summarised

    except Exception as error:
        print(f"❌ Summarisation failed unexpectedly: {error}")
        print("   Continuing with raw descriptions as fallback...")
        # Return articles as-is so the pipeline can continue.
        return articles


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4: Generate HTML Email Body
# ─────────────────────────────────────────────────────────────────────────────

def generate_html(
    articles: list[dict[str, any]],
    executive_summary: list[str] = None,
    ai_quote: dict[str, str] = None,
    market_mentions: dict[str, bool] = None,
) -> str | None:
    """
    Render the Jinja2 HTML email template with real article data.

    Loads templates/email.html and fills every {{ placeholder }} with
    real data from the summarised articles and enrichment data.

    Jinja2 works like mail-merge:
      Template has: "Hello {{ name }}"
      Data has:     {"name": "Alice"}
      Output:       "Hello Alice"

    Args:
        articles          : Summarised article list from summarise_news().
        executive_summary : List of executive brief bullet strings.
        ai_quote          : Dict with 'text' and 'author' keys.
        market_mentions   : Dict mapping company names to True/False.

    Returns:
        A complete HTML string ready to be emailed.
        Returns None if template rendering fails.
    """
    _step(4, "Generating Email Body")
    print("🎨 Rendering HTML templates...")

    try:
        # Verify the template file exists before attempting to render
        template_path = TEMPLATE_DIR / TEMPLATE_FILE
        if not template_path.exists():
            print(
                f"❌ Template not found: {template_path}\n"
                "   Make sure templates/email.html exists in your project."
            )
            return None

        # Set up Jinja2 — point it at the templates/ folder
        env      = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
        template = env.get_template(TEMPLATE_FILE)

        # Split articles: tech/AI (score >= 3) vs breaking (score < 3)
        tech_articles     = [a for a in articles if a.get("relevance_score", 3) >= 3]
        breaking_articles = [a for a in articles if a.get("relevance_score", 3) < 3]

        # Count trending stories (relevance score 4-5)
        trending_count = sum(1 for a in articles if a.get("relevance_score", 3) >= 4)

        # Calculate average read time across all articles
        read_times = [a.get("read_time_minutes", 3) for a in articles]
        avg_read_time = round(sum(read_times) / len(read_times)) if read_times else 3

        today_str = datetime.date.today().strftime("%A, %B %d, %Y")

        # Render — every {{ variable }} in the template gets replaced here
        html = template.render(
            subject             = config.EMAIL_SUBJECT,
            date                = today_str,
            send_time           = datetime.datetime.now().strftime("%H:%M"),
            model               = config.GEMINI_MODEL,
            tech_articles       = tech_articles,
            breaking_articles   = breaking_articles,
            total_articles      = len(articles),
            tech_count          = len(tech_articles),
            breaking_count      = len(breaking_articles),
            trending_count      = trending_count,
            avg_read_time       = avg_read_time,
            executive_summary   = executive_summary or [],
            ai_quote            = ai_quote or {"text": "The future belongs to those who learn more skills and combine them in creative ways.", "author": "Robert Greene"},
            market_mentions     = market_mentions or {},
            greeting_name       = "Reader",
        )

        size_kb = len(html) / 1024
        print(f"✅ Premium newsletter template compiled successfully ({size_kb:.1f} KB,  "
              f"{len(tech_articles)} tech  +  {len(breaking_articles)} breaking articles)")
        return html

    except TemplateNotFound:
        print(f"❌ Jinja2 could not find template: {TEMPLATE_FILE}")
        return None

    except Exception as error:
        print(f"❌ HTML generation failed: {error}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5: Send the Email
# ─────────────────────────────────────────────────────────────────────────────

def send_email_digest(html_body: str) -> bool:
    """
    Send the rendered HTML email via Gmail SMTP.

    Delegates entirely to email_sender.send_email() which handles:
      - SMTP connection and TLS encryption
      - Gmail App Password authentication
      - MIME email building (HTML + plain text)
      - All error cases (wrong password, network failure, etc.)

    Args:
        html_body: The rendered HTML string from generate_html().

    Returns:
        True  — email was accepted and sent.
        False — sending failed (error printed by email_sender).
    """
    _step(5, "Sending Email")
    print("📨 Dispatching via Gmail SMTP (STARTTLS)...")

    try:
        success = send_email(
            recipient = config.EMAIL_RECIPIENT,
            subject   = config.EMAIL_SUBJECT,
            html_body = html_body,
        )
        return success

    except Exception as error:
        print(f"❌ Unexpected error during email dispatch: {error}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 6: Print Final Summary
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(
    articles:      list[dict[str, any]],
    email_success: bool,
    start_time:    datetime.datetime,
) -> None:
    """
    Print a clean completion report after the pipeline finishes.

    Shows:
      - Total articles processed
      - How many had successful AI summaries
      - Whether the email was sent
      - Total time taken

    Args:
        articles      : Final list of summarised articles.
        email_success : True if the email was sent successfully.
        start_time    : datetime when run_pipeline() started.
    """
    _step(6, "Pipeline Complete")

    elapsed     = datetime.datetime.now() - start_time
    total_secs  = int(elapsed.total_seconds())
    ok_summaries = sum(1 for a in summarised if not a.get("summary_error")) if 'summarised' in locals() else sum(1 for a in articles if not a.get("summary_error"))

    print(f"""
  📊 RUN SUMMARY
  {'─'*40}
  📰 Articles processed  : {len(articles)}
  🤖 AI summaries        : {ok_summaries}/{len(articles)}
  📧 Email sent          : {'✅ Yes' if email_success else '❌ No'}
  ⏱️  Total time          : {total_secs}s
  🕐 Finished at         : {datetime.datetime.now().strftime('%H:%M:%S')}
  {'─'*40}

  {'🎉 Task completed successfully!' if email_success else '⚠️  Pipeline completed with issues.'}
""")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PIPELINE ORCHESTRATOR: run_pipeline()
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline() -> bool:
    """
    Run the complete AI News Agent pipeline from start to finish.

    This function calls each step in sequence. If a critical step fails,
    it stops early and explains what went wrong. Non-critical failures
    (like Gemini being unavailable) are handled gracefully — the pipeline
    continues with fallback content rather than crashing.

    Returns:
        True  — pipeline completed and email was sent.
        False — pipeline failed at a critical step.
    """
    start_time = datetime.datetime.now()

    print(f"\n{_DLINE}")
    print(f"  🤖 AI NEWS AGENT  —  {start_time.strftime('%A, %B %d, %Y  %H:%M')}")
    print(_DLINE)
    logger.info("Pipeline execution started.")

    # ── STEP 1: Config ────────────────────────────────────────────────────
    # Critical — without valid config, nothing else can work.
    if not load_config():
        print("\n💥 Aborting: configuration is invalid.")
        logger.critical("Pipeline aborted: invalid configuration.")
        return False

    # ── STEP 2: Fetch News ────────────────────────────────────────────────
    # Critical — without articles there is nothing to email.
    articles = fetch_news()
    if not articles:
        print("\n💥 Aborting: no articles fetched.")
        logger.critical("Pipeline aborted: no news articles were fetched.")
        return False

    # ── STEP 3: Summarise ─────────────────────────────────────────────────
    # Non-critical — if Gemini fails, we use original descriptions as fallback.
    articles = summarise_news(articles)

    # ── STEP 3b: Generate enrichment data ─────────────────────────────────
    # These are additional Gemini calls that enrich the newsletter.
    # Each has its own fallback if Gemini quota is exhausted.
    _step(3, "Generating Newsletter Enrichments")
    print("✨ Generating executive summary, AI quote, and market snapshot...")

    executive_summary = generate_executive_summary(articles)
    print(f"   ✅ Executive summary: {len(executive_summary)} bullet points")

    ai_quote = generate_ai_quote()
    print(f"   ✅ AI quote: \"{ai_quote['text'][:50]}...\"")

    market_mentions = generate_market_mentions(articles)
    mentioned = [c for c, v in market_mentions.items() if v]
    print(f"   ✅ Market mentions: {', '.join(mentioned) if mentioned else 'none found'}")

    # ── STEP 4: Generate HTML ─────────────────────────────────────────────
    # Critical — without HTML there is nothing to email.
    html = generate_html(
        articles,
        executive_summary=executive_summary,
        ai_quote=ai_quote,
        market_mentions=market_mentions,
    )
    if not html:
        print("\n💥 Aborting: HTML generation failed.")
        logger.critical("Pipeline aborted: HTML email body generation failed.")
        return False

    # ── STEP 5: Send Email ────────────────────────────────────────────────
    email_ok = send_email_digest(html)
    if email_ok:
        logger.info("Pipeline completed successfully: Email sent.")
    else:
        logger.error("Pipeline finished with errors: Email dispatch failed.")

    # ── STEP 6: Summary report ────────────────────────────────────────────
    print_summary(articles, email_ok, start_time)

    return email_ok


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
# This block runs ONLY when you execute: python app.py
# It does NOT run when other files import from app.py.
# (The `if __name__ == "__main__"` pattern is standard Python convention.)

if __name__ == "__main__":
    success = run_pipeline()

    # Exit with code 0 (success) or 1 (failure).
    # This matters when app.py is called from scheduler.py or a cron job —
    # the calling process can check the exit code to know if it worked.
    sys.exit(0 if success else 1)
