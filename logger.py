"""
logger.py — Project Logging System Configuration
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Configures the standard Python logging library. It creates a folder named 
  "logs/" and a log file named "app.log" inside it.

  This file acts as the central logging initializer for all modules in our 
  AI News Agent.

─────────────────────────────────────────────────────────────────────────────
EXPLAINING PYTHON LOGGING LEVELS (for beginners):
─────────────────────────────────────────────────────────────────────────────

  Python's logging module has 5 standard levels, represented by integers.
  They allow you to filter messages by severity.

  1. DEBUG (Value: 10)
     • What it is: Extremely detailed diagnostic information.
     • Use case: "Connecting to database at IP 192.168.1.5", "Parsing line 52".
     • Active: Typically turned off in production, only enabled by developers.

  2. INFO (Value: 20)
     • What it is: General confirmation that things are working as expected.
     • Use case: "Job started", "Fetched 12 articles", "Email sent to recipient".
     • Active: Yes, this is the default level for tracking normal operations.

  3. WARNING (Value: 30)
     • What it is: Something unexpected happened, but the app is still working.
     • Use case: "Connection dropped, retrying in 5s", "Gemini rate limit warning".
     • Active: Yes, warns you about potential future failures.

  4. ERROR (Value: 40)
     • What it is: A serious problem that prevented a specific function from working.
     • Use case: "Failed to parse API response", "Could not send email due to bad password".
     • Active: Yes, always logged to diagnose app failures.

  5. CRITICAL (Value: 50)
     • What it is: A catastrophic error indicating the program cannot continue.
     • Use case: "Out of memory", "Database connection lost permanently, shutting down".
     • Active: Yes, highest priority logs.

─────────────────────────────────────────────────────────────────────────────
HOW TO USE IN OTHER MODULES:
─────────────────────────────────────────────────────────────────────────────
  from logger import logger

  logger.info("This is an info message")
  logger.error("Something went wrong!")
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Create the logs directory
# ─────────────────────────────────────────────────────────────────────────────
# Create the "logs" directory if it doesn't already exist.
# os.makedirs is the Python equivalent of 'mkdir -p' in terminal.
os.makedirs("logs", exist_ok=True)

LOG_FILE = os.path.join("logs", "app.log")

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Set up the logger
# ─────────────────────────────────────────────────────────────────────────────
# We get (or create) a logger named "ai_news_agent".
# This prevents our logs from being mixed up with libraries' logs (like urllib3).
logger = logging.getLogger("ai_news_agent")

# Set global threshold level to INFO.
# This means DEBUG logs are ignored, but INFO, WARNING, ERROR, and CRITICAL
# logs will be recorded.
logger.setLevel(logging.INFO)

# To prevent duplicate log handlers if imported multiple times
if not logger.handlers:
    # ── Formatter ──────────────────────────────────────────────────────────
    # format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    # This formats each log line like:
    # 2026-06-30 11:25:00 - INFO - [app.py:100] - Fetching news articles...
    log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ── Rotating File Handler ──────────────────────────────────────────────
    # Writes log messages to logs/app.log.
    # We use a RotatingFileHandler:
    #   - maxBytes=1MB  →  if the file reaches 1MB, it gets renamed to app.log.1
    #   - backupCount=3 →  keeps up to 3 old log files (saves disk space)
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=1024 * 1024,  # 1 MegaByte
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    # ── Add Handlers to Logger ─────────────────────────────────────────────
    logger.addHandler(file_handler)

    # Note: We do not add a StreamHandler (console handler) here because we want
    # to keep the terminal output formatted exactly as the user requested in app.py.
    # This ensures that app.log records background details while the terminal
    # remains clean, readable, and beginner-friendly.
