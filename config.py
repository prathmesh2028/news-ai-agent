"""
config.py — Configuration & Settings Loader
═════════════════════════════════════════════════════════════════════════════
PURPOSE:
  This is the SINGLE source of truth for all settings in the application.
  Every other module imports its settings from here — nobody reads the .env
  file directly except this file.

HOW IT WORKS:
  1. python-dotenv reads your .env file and loads each line into
     Python's os.environ (the system's environment variable store).
  2. We then call os.getenv("VARIABLE_NAME") to read each value.
  3. We validate that all REQUIRED variables are present.
  4. We expose everything as clean, named Python variables.

HOW OTHER MODULES USE IT:
  from config import GEMINI_API_KEY, SMTP_SERVER   ← clean & simple

NEVER hardcode secrets like API keys in .py files. Always put them in .env.
═════════════════════════════════════════════════════════════════════════════
"""

import os          # os lets us read environment variables from the system
import sys         # sys lets us exit the program with an error message

from dotenv import load_dotenv   # reads the .env file and loads variables


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Load the .env file
# ─────────────────────────────────────────────────────────────────────────────
# load_dotenv() searches for a file named ".env" in the current directory
# and loads every KEY=VALUE pair into the environment.
# We set override=True to ensure that values in the .env file take precedence
# over any existing system or terminal environment variables.

load_dotenv(override=True)


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Define which variables are REQUIRED
# ─────────────────────────────────────────────────────────────────────────────
# These are the variable names that MUST exist in the .env file.
# If any of these is missing, the program will refuse to start and
# tell you exactly which one is missing and how to fix it.

REQUIRED_VARIABLES: list[str] = [
    "GEMINI_API_KEY",    # Google Gemini AI — for summarizing news
    "NEWS_API_KEY",      # NewsAPI.org      — for fetching news articles
    "EMAIL_ADDRESS",     # Gmail address    — the account that SENDS the email
    "EMAIL_PASSWORD",    # Gmail App Password — authenticates the sender account
    "SMTP_SERVER",       # Mail server hostname (e.g. smtp.gmail.com)
    "SMTP_PORT",         # Mail server port number (e.g. 587)
]


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3: Validate — fail early with a clear error message
# ─────────────────────────────────────────────────────────────────────────────
# "Fail early" means: check for problems at startup, not halfway through
# a run. This saves you from confusing errors later in the pipeline.

def _validate_config() -> None:
    """
    Check that every required environment variable is set.
    If anything is missing, print a helpful error message and exit.
    The underscore prefix (_) is a Python convention meaning:
      "this function is for internal use only — don't import it."
    """
    missing = []  # We'll collect ALL missing variables, not just the first one.

    for var_name in REQUIRED_VARIABLES:
        value = os.getenv(var_name)

        # os.getenv returns None if the variable doesn't exist.
        # We also treat an empty string ("") as missing.
        if not value or value.strip() == "":
            missing.append(var_name)

    if missing:
        # Build a clear, actionable error message.
        missing_list = "\n  ".join(f"• {name}" for name in missing)
        print(
            "\n"
            "╔══════════════════════════════════════════════════════════╗\n"
            "║          ❌  CONFIGURATION ERROR                         ║\n"
            "╚══════════════════════════════════════════════════════════╝\n"
            "\n"
            "The following required variables are missing from your .env file:\n"
            f"\n  {missing_list}\n"
            "\n"
            "HOW TO FIX:\n"
            "  1. Open the file named  .env  in your project folder.\n"
            "  2. Fill in the missing values.\n"
            "  3. If .env doesn't exist, copy .env.example → .env first.\n"
            "\n"
            "  Windows: copy .env.example .env\n"
            "  Mac/Linux: cp .env.example .env\n"
        )
        sys.exit(1)   # Exit with code 1 = "program failed" (not a normal exit)


# Run validation immediately when this module is imported.
# This means any module that does  "from config import ..."
# will trigger validation right away — before anything else runs.
_validate_config()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4: Read and expose all settings as named variables
# ─────────────────────────────────────────────────────────────────────────────
# After this point we KNOW all required variables exist (validation passed).
# We use os.getenv(name, default) — the second argument is the default value
# if the variable is missing (only used for OPTIONAL variables below).


# ── Gemini AI ─────────────────────────────────────────────────────────────
# The secret key that authorises us to use Google's Gemini AI model.
# Used in: summarizer.py
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")


# ── NewsAPI ───────────────────────────────────────────────────────────────
# The secret key for NewsAPI.org — gives us access to thousands of sources.
# Used in: fetcher.py
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")

# Maximum number of articles to fetch in one run.
# We use int() to convert the string "15" from the .env file into the number 15.
# Default: 15 — enough to get a good digest without hitting API rate limits.
NEWS_MAX_ARTICLES: int = int(os.getenv("NEWS_MAX_ARTICLES", "15"))

# ── News Focus Strategy ───────────────────────────────────────────────────
# These control WHAT kind of news the agent fetches and prioritises.
#
# PRIMARY queries → always fetched. These are tech/AI focused.
# SECONDARY query → fetched only if breaking news is detected.
# Gemini will be told to prioritise these categories in its summaries.
#
# You don't need to change these — but you can if you want.
NEWS_PRIMARY_QUERIES: list[str] = [
    "artificial intelligence",       # Core AI news
    "technology",                    # Broad tech industry
    "machine learning deep learning", # ML/DL research & breakthroughs
    "big tech Google Microsoft Apple OpenAI",  # Major tech companies
    "cybersecurity data breach",     # Critical tech security news
]

# Breaking/urgent news topics — only included if highly significant.
# Examples: major government AI regulation, global tech policy, economic crises.
NEWS_BREAKING_QUERY: str = (
    "breaking urgent government regulation AI policy OR "
    "global technology crisis OR major cyberattack"
)

# The ratio split for the digest:
#   e.g., 0.8 = 80% tech/AI articles, 20% important general/breaking news.
NEWS_TECH_RATIO: float = float(os.getenv("NEWS_TECH_RATIO", "0.80"))


# ── Email — Sender Account ────────────────────────────────────────────────
# The Gmail address that will log into Gmail's SMTP server and send the email.
# Used in: email_sender.py
EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")

# The Gmail App Password (16 characters, spaces are fine — Gmail ignores them).
# This is NOT your normal Gmail password. See README for how to create one.
# Used in: email_sender.py
EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")

# The email address that will RECEIVE the digest.
# Can be the same as EMAIL_ADDRESS if you're sending to yourself.
# Used in: email_sender.py
EMAIL_RECIPIENT: str = os.getenv("EMAIL_RECIPIENT", EMAIL_ADDRESS)
# ↑ If EMAIL_RECIPIENT is not set, it defaults to EMAIL_ADDRESS (send to self).


# ── Email — SMTP Server Settings ─────────────────────────────────────────
# SMTP (Simple Mail Transfer Protocol) is the standard for sending email.
# smtp.gmail.com = Gmail's outgoing mail server.
# Used in: email_sender.py
SMTP_SERVER: str = os.getenv("SMTP_SERVER")

# Port 587 uses STARTTLS encryption — the modern, secure way to send email.
# (Port 465 uses SSL, port 25 is legacy/unencrypted — avoid those.)
# We convert the string "587" from .env to the integer 587.
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))


# ── Scheduler ────────────────────────────────────────────────────────────
# The time (HH:MM, 24-hour format) to automatically send the digest each day.
# Example: "07:00" = 7:00 AM,  "18:30" = 6:30 PM
# Used in: scheduler.py
SEND_TIME: str = os.getenv("SEND_TIME", "08:00")

# Alias — scheduler.py uses SCHEDULE_TIME, which points to the same value.
SCHEDULE_TIME: str = SEND_TIME


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5: Derived / computed settings (not from .env — calculated here)
# ─────────────────────────────────────────────────────────────────────────────

# Email subject line — includes today's date automatically.
# email_sender.py will use this as the email's Subject: header.
import datetime
today_str = datetime.date.today().strftime("%B %d, %Y")   # e.g. "June 30, 2026"
EMAIL_SUBJECT: str = f"🤖 Your AI & Tech News Digest — {today_str}"

# Gemini model to use for summarization.
# "gemini-2.5-flash" = fast, free tier, excellent for summarization tasks.
# "gemini-2.5-flash-lite" = optimized version for high-volume tasks.
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ── Template Configuration ──────────────────────────────────────────────────
# Standard path for Jinja2 HTML email templates. Centralizing this here prevents
# duplicate calculations across app.py, email_sender.py, and preview_email.py.
from pathlib import Path
TEMPLATE_DIR: Path = Path(__file__).parent / "templates"
TEMPLATE_FILE: str = "email.html"


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 6: Print a startup confirmation (helpful during development)
# ─────────────────────────────────────────────────────────────────────────────
# This shows a summary of what was loaded so you can verify it's correct
# without printing actual secrets (we only show the first/last 4 characters).

def _mask(secret: str, visible: int = 4) -> str:
    """
    Partially hide a secret string for safe display.
    Example: "AIzaSyDOk101FmH4..." → "AIza...qnk"
    """
    if not secret or len(secret) <= visible * 2:
        return "****"
    return f"{secret[:visible]}...{secret[-visible:]}"


def print_config_summary() -> None:
    """
    Print a human-readable summary of the loaded config.
    Secrets are partially masked so they're never shown in full.
    Call this function from main.py at startup for a sanity check.
    """
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════╗\n"
        "║          ✅  Configuration Loaded Successfully           ║\n"
        "╚══════════════════════════════════════════════════════════╝\n"
        f"\n  🤖 Gemini model    : {GEMINI_MODEL}"
        f"\n  🔑 Gemini API key  : {_mask(GEMINI_API_KEY)}"
        f"\n  📰 NewsAPI key     : {_mask(NEWS_API_KEY)}"
        f"\n  📬 Sending from    : {EMAIL_ADDRESS}"
        f"\n  📥 Sending to      : {EMAIL_RECIPIENT}"
        f"\n  🌐 SMTP server     : {SMTP_SERVER}:{SMTP_PORT}"
        f"\n  ⏰ Schedule        : Daily at {SEND_TIME}"
        f"\n  📊 Max articles    : {NEWS_MAX_ARTICLES}"
        f"\n  📡 Tech/AI ratio   : {int(NEWS_TECH_RATIO * 100)}% tech, "
        f"{int((1 - NEWS_TECH_RATIO) * 100)}% breaking/general"
        "\n"
    )
