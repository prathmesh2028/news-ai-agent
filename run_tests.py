"""
run_tests.py — Interactive Test Suite for Beginners
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  A single, menu-driven script designed to help beginners test each module 
  of the AI News Agent individually. 

  It contains dedicated, isolated tests for:
    1. Configuration Loading (config.py)
    2. News Fetching (news_fetcher.py)
    3. Gemini Summarization (summarizer.py)
    4. Email Dispatching (email_sender.py)
    5. Daily Scheduler (scheduler.py)

HOW TO RUN:
  python run_tests.py
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import datetime
import time

# Visual separators
_LINE = "─" * 65
_DLINE = "═" * 65


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 1: Configuration Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_config():
    print(f"\n{_DLINE}")
    print(" 🛠️  TEST 1: Configuration System Verification")
    print(f"{_DLINE}\n")

    print("→ Importing 'config' module...")
    try:
        import config
        config.print_config_summary()
        print("✅ SUCCESS: Configuration validated. Environment variables loaded successfully.")
    except Exception as error:
        print(f"\n❌ FAILURE: Failed to load config module.")
        print(f"   Error details: {error}")
        print("\n💡 BEGINNER TIP:")
        print("   Make sure you have a file named '.env' in your project root folder.")
        print("   Check that you copied '.env.example' and renamed it to '.env'.")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 2: News Fetcher API Check
# ─────────────────────────────────────────────────────────────────────────────

def test_fetcher():
    print(f"\n{_DLINE}")
    print(" 📰  TEST 2: News Fetcher API Verification")
    print(f"{_DLINE}\n")

    print("→ Importing 'news_fetcher'...")
    try:
        from news_fetcher import fetch_ai_news
    except Exception as error:
        print(f"❌ FAILURE: Import failed: {error}")
        return

    print("→ Querying NewsAPI for latest articles (this needs active internet)...")
    try:
        # Capping at 3 to preserve rate limits
        articles = fetch_ai_news()
        
        if not articles:
            print("\n⚠️  WARNING: Fetcher executed but returned 0 articles.")
            print("\n💡 BEGINNER TIP:")
            print("   • Double-check your NEWS_API_KEY inside your '.env' file.")
            print("   • Ensure you have an active internet connection.")
            return

        print(f"\n✅ SUCCESS: Successfully fetched {len(articles)} articles!")
        print(f"\n{_LINE}")
        print("  SAMPLE ARTICLE DETAILS")
        print(f"{_LINE}")
        
        sample = articles[0]
        print(f"  Title   : {sample.get('title')}")
        print(f"  Source  : {sample.get('source')}")
        print(f"  Date    : {sample.get('publishedAt')}")
        print(f"  URL     : {sample.get('url')}")
        print(f"  Desc    : {sample.get('description', '')[:100]}...")
        print(f"{_LINE}")

    except Exception as error:
        print(f"\n❌ FAILURE: Fetching crashed with unexpected error.")
        print(f"   Error: {error}")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 3: Gemini Summarizer API Check
# ─────────────────────────────────────────────────────────────────────────────

def test_summarizer():
    print(f"\n{_DLINE}")
    print(" 🤖  TEST 3: Google Gemini API & Parsing Verification")
    print(f"{_DLINE}\n")

    print("→ Importing 'summarizer'...")
    try:
        from summarizer import summarise_articles
    except Exception as error:
        print(f"❌ FAILURE: Import failed: {error}")
        return

    # Create a simple, realistic sample article
    test_article = {
        "title": "OpenAI releases next-generation reasoning model",
        "description": "OpenAI today introduced its new reasoning model with improved logical coding capabilities.",
        "source": "TechCrunch",
        "url": "https://techcrunch.com/sample"
    }

    print("→ Submitting 1 test article to Google Gemini...")
    print(f"   Using model: gemini-2.0-flash (this will hit active Google servers)")
    
    start = time.time()
    results = summarise_articles([test_article])
    elapsed = time.time() - start

    if not results or results[0].get("summary_error"):
        print("\n❌ FAILURE: Gemini could not summarise the article (fallback was used).")
        print("\n💡 BEGINNER TIP:")
        # Check if it was 429
        print("   Common Causes:")
        print("   • 429 RESOURCE_EXHAUSTED: You ran tests too fast or exhausted daily free credits.")
        print("   • 403 Forbidden: Invalid GEMINI_API_KEY in your '.env' file.")
        print("   • 404 Not Found: Check if GEMINI_MODEL name is typed correctly in your config.")
        return

    summary = results[0]
    print(f"\n✅ SUCCESS: Gemini summary completed in {elapsed:.1f} seconds!")
    print(f"\n{_LINE}")
    print("  GEMINI RESPONSE OUTPUT")
    print(f"{_LINE}")
    print(f"  🤖 AI Summary : {summary.get('summary')}")
    print(f"  💡 Insight    : {summary.get('why_it_matters')}")
    print(f"  📊 Relevance  : {summary.get('relevance_score')}/5")
    print(f"  📌 Key Points :")
    for bullet in summary.get("bullets", []):
        print(f"     • {bullet}")
    print(f"{_LINE}")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 4: Email Sender SMTP Connection
# ─────────────────────────────────────────────────────────────────────────────

def test_email():
    print(f"\n{_DLINE}")
    print(" 📧  TEST 4: SMTP Email Connection Verification")
    print(f"{_DLINE}\n")

    print("→ Importing 'email_sender'...")
    try:
        from email_sender import send_email
        import config
    except Exception as error:
        print(f"❌ FAILURE: Import failed: {error}")
        return

    # Basic test message
    test_html = """
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f0f1a; color: #ffffff; padding: 20px;">
        <h2 style="color: #63b3ed;">🤖 AI News Agent Connection Test</h2>
        <p>If you received this message, your Gmail SMTP connection is fully working!</p>
        <hr style="border: 0; border-top: 1px solid #718096; margin: 20px 0;"/>
        <p style="font-size: 12px; color: #718096;">Sent at: """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
      </body>
    </html>
    """

    print("→ Connecting to Gmail SMTP server and sending test email...")
    print(f"   Sending to: {config.EMAIL_RECIPIENT}")

    success = send_email(
        recipient=config.EMAIL_RECIPIENT,
        subject="🧪 AI News Agent Test Email",
        html_body=test_html
    )

    if success:
        print("\n✅ SUCCESS: Test email delivered. Please check your inbox.")
    else:
        print("\n❌ FAILURE: Email delivery failed.")
        print("\n💡 BEGINNER TIP:")
        print("   Gmail requires a 16-character App Password (NOT your login password).")
        print("   Make sure you turned on 2FA and generated an App Password here:")
        print("   👉 https://myaccount.google.com/apppasswords")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 5: Scheduler Dry Run
# ─────────────────────────────────────────────────────────────────────────────

def test_scheduler():
    print(f"\n{_DLINE}")
    print(" ⏰  TEST 5: Scheduler Configuration Verification")
    print(f"{_DLINE}\n")

    print("→ Importing 'scheduler'...")
    try:
        import scheduler
        import config
    except Exception as error:
        print(f"❌ FAILURE: Import failed: {error}")
        return

    print("→ Parsing scheduler settings...")
    try:
        scheduler.setup_schedule()
        import schedule
        next_run = schedule.next_run()
        
        print(f"   ⏰ Configured Daily Time : {config.SCHEDULE_TIME}")
        print(f"   📅 Next Run Scheduled At : {next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else 'Unknown'}")
        
        delta = next_run - datetime.datetime.now()
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        print(f"   ⏳ Time until next run   : {hours} hours, {minutes} minutes")
        
        print("\n✅ SUCCESS: Scheduler config loaded OK. Daily job is correctly scheduled.")

    except Exception as error:
        print(f"\n❌ FAILURE: Scheduler config error: {error}")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────

def main():
    while True:
        print(f"\n{_DLINE}")
        print("           🤖  AI NEWS AGENT - MODULE TEST RUNNER  🤖")
        print(f"{_DLINE}")
        print("  [1] Test Configuration (config.py)")
        print("  [2] Test News Fetcher (news_fetcher.py)")
        print("  [3] Test Gemini Summarizer (summarizer.py)")
        print("  [4] Test Email Sender (email_sender.py)")
        print("  [5] Test Scheduler Configuration (scheduler.py)")
        print("  [6] Run ALL Tests Sequentially")
        print("  [0] Exit")
        print(f"{_DLINE}")

        try:
            choice = input("Enter choice (0-6): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if choice == "0":
            print("\nGoodbye!")
            break
        elif choice == "1":
            test_config()
        elif choice == "2":
            test_fetcher()
        elif choice == "3":
            test_summarizer()
        elif choice == "4":
            test_email()
        elif choice == "5":
            test_scheduler()
        elif choice == "6":
            test_config()
            time.sleep(1)
            test_fetcher()
            time.sleep(1)
            test_summarizer()
            time.sleep(1)
            test_email()
            time.sleep(1)
            test_scheduler()
        else:
            print("\n⚠️  Invalid choice. Please enter a number between 0 and 6.")
        
        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
