"""
scheduler.py — Automated Daily Job Runner
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Runs the full AI News pipeline (app.py) automatically every morning.
  Once started, it runs forever in the background, waking up at the
  scheduled time, running the pipeline, then going back to sleep.

HOW IT WORKS:
  ┌─────────────────────────────────────────────────────────┐
  │                  SCHEDULER LOOP                         │
  │                                                         │
  │   Start → Schedule 08:00 daily job                      │
  │       │                                                 │
  │       └──► Every 60 seconds: check if any job is due    │
  │                │                                        │
  │                ├─ Not yet: print "Waiting..." → sleep   │
  │                │                                        │
  │                └─ It's time! → run pipeline → sleep     │
  └─────────────────────────────────────────────────────────┘

  The `schedule` library handles all the timing logic.
  We just tell it WHAT to run and WHEN, then call run_pending() in a loop.

WAYS TO RUN:
  python scheduler.py          → Start the scheduler (runs at 08:00 daily)
  python scheduler.py --now    → Run the pipeline RIGHT NOW + then schedule
  python scheduler.py --test   → Dry run: show schedule info, don't send email

HOW TO KEEP IT RUNNING CONTINUOUSLY:
  See the "KEEPING IT RUNNING" section at the bottom of this file.

CHANGING THE TIME:
  Edit SCHEDULE_TIME below, or set SCHEDULE_TIME=09:30 in your .env file.
═══════════════════════════════════════════════════════════════════════════════
"""

import sys           # sys.argv for command-line flags, sys.exit() to quit
import time          # time.sleep() to pause between schedule checks
import datetime      # For timestamps in the log output
import traceback     # For printing full error stack traces on unexpected crashes

import schedule      # The scheduling library (pip install schedule)

import config        # Our settings (SCHEDULE_TIME, etc.)
from app import run_pipeline    # The full pipeline from app.py
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

# The time to send the email every day (24-hour format: "HH:MM").
# This reads SCHEDULE_TIME from .env if set, otherwise defaults to "08:00".
SCHEDULE_TIME = config.SCHEDULE_TIME   # e.g. "08:00"

# How often (in seconds) to check if a job is due.
# 60 seconds = checks once per minute. Fine for daily jobs.
POLL_INTERVAL_SECONDS = 60

# Visual separator for log output
_LINE  = "─" * 60
_DLINE = "═" * 60


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Timestamped log printer
# ─────────────────────────────────────────────────────────────────────────────

def _log(message: str) -> None:
    """
    Print a message with the current timestamp prepended.

    Example output:
        [2026-06-30 08:00:01]  🚀 Running pipeline...

    Adding timestamps to every log line makes it easy to know WHEN something
    happened — essential when the scheduler runs overnight unattended.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}]  {message}")


# ─────────────────────────────────────────────────────────────────────────────
#  THE JOB FUNCTION — this is what the scheduler calls at 08:00 every day
# ─────────────────────────────────────────────────────────────────────────────

def run_daily_job() -> None:
    """
    The function the scheduler calls at the configured time every day.

    This is the "job" — it:
      1. Prints "Running..." with a timestamp
      2. Calls run_pipeline() from app.py (the full fetch → summarise → send flow)
      3. Prints "Completed..." with success/failure status
      4. Catches ANY exception so the scheduler loop never crashes

    WHY WRAP run_pipeline() IN A TRY/EXCEPT?
    If run_pipeline() raises an unexpected error, the scheduler's infinite
    while loop would crash and stop running. By catching all exceptions here,
    the scheduler survives errors and continues to run tomorrow's job.
    """
    print(f"\n{_DLINE}")
    _log("🚀 Running...  — Starting daily AI News pipeline")
    print(_DLINE)

    try:
        # run_pipeline() does everything:
        # fetch news → summarise → render HTML → send email
        logger.info("Daily scheduled news pipeline started.")
        success = run_pipeline()

        print(_DLINE)
        if success:
            _log("✅ Completed!  — Email sent successfully.")
            logger.info("Daily scheduled news pipeline completed successfully.")
        else:
            _log("⚠️  Completed with issues — Email may not have been sent.")
            _log("   Check the logs above for details.")
            logger.warning("Daily scheduled news pipeline completed with issues.")
        print(_DLINE)

    except KeyboardInterrupt:
        # User pressed Ctrl+C while the pipeline was running.
        # Re-raise so the outer loop can exit cleanly.
        logger.warning("Daily scheduled news pipeline interrupted by user.")
        raise

    except Exception as error:
        # Something unexpected crashed inside the pipeline.
        # We log the full error (with line numbers) so it's easy to debug,
        # but we do NOT re-raise — the scheduler loop must survive.
        print(_DLINE)
        _log(f"❌ Pipeline crashed with an unexpected error:")
        _log(f"   {type(error).__name__}: {error}")
        print()
        print("   Full traceback:")
        traceback.print_exc()
        print()
        _log("   ⏭️  Scheduler will continue — next job runs tomorrow.")
        print(_DLINE)
        logger.error(f"Unexpected crash in run_daily_job: {error}", exc_info=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SCHEDULER SETUP
# ─────────────────────────────────────────────────────────────────────────────

def setup_schedule() -> None:
    """
    Register the daily job with the schedule library.

    schedule.every().day.at("08:00").do(run_daily_job)
    ─────────────────────────────────────────────────
    schedule   = the scheduling library
    .every()   = start defining a recurring trigger
    .day       = repeat daily
    .at("08:00")= at this specific time (24-hour format)
    .do(...)   = call this function when triggered

    After calling setup_schedule(), the job is REGISTERED but not yet RUNNING.
    You still need the `while True` loop (in start_scheduler()) to actually
    trigger it at the right time.
    """
    schedule.clear()   # Remove any previously registered jobs (safety measure)

    schedule.every().day.at(SCHEDULE_TIME).do(run_daily_job)

    # Calculate time until next run for a helpful startup message
    next_run = schedule.next_run()
    if next_run:
        delta   = next_run - datetime.datetime.now()
        hours   = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        _log(f"📅 Scheduled: daily at {SCHEDULE_TIME}  "
             f"(next run in {hours}h {minutes}m)")
    else:
        _log(f"📅 Scheduled: daily at {SCHEDULE_TIME}")


# ─────────────────────────────────────────────────────────────────────────────
#  THE MAIN LOOP — runs forever until you press Ctrl+C
# ─────────────────────────────────────────────────────────────────────────────

def start_scheduler(run_now_first: bool = False) -> None:
    """
    Start the infinite scheduling loop.

    HOW THE LOOP WORKS:
    ┌─ while True ────────────────────────────────────────┐
    │                                                      │
    │  schedule.run_pending()                              │
    │      → Checks if any registered job is due NOW.     │
    │      → If yes: calls run_daily_job() immediately.   │
    │      → If no:  returns immediately, does nothing.   │
    │                                                      │
    │  time.sleep(POLL_INTERVAL_SECONDS)                   │
    │      → Pauses for 60 seconds before checking again. │
    │      → Uses almost zero CPU while sleeping.         │
    │                                                      │
    └──────────────────────────────────────────────────────┘

    The loop only exits when the user presses Ctrl+C (KeyboardInterrupt).

    Args:
        run_now_first: If True, run the pipeline immediately before
                       entering the loop (useful for --now flag).
    """
    config.print_config_summary()
    print()

    # Register the job with the schedule library
    setup_schedule()
    logger.info(f"Scheduler initialized. Registered daily job at {SCHEDULE_TIME}")

    # Optional: run immediately on startup (triggered by --now flag)
    if run_now_first:
        _log("⚡ --now flag detected: running pipeline immediately...")
        logger.info("Executing immediate run (--now) before entering wait loop.")
        run_daily_job()

    print()
    _log(f"⏳ Waiting...  — Scheduler is running. Press Ctrl+C to stop.")
    _log(f"   Checking for due jobs every {POLL_INTERVAL_SECONDS}s")
    print()

    # ── THE INFINITE LOOP ──────────────────────────────────────────────────
    try:
        while True:
            # Check if any job is due and run it if so.
            schedule.run_pending()

            # Print a "still alive" heartbeat every hour so you can confirm
            # the scheduler is still running when you check the terminal.
            _maybe_print_heartbeat()

            # Sleep before the next check.
            # 60s sleep = very low CPU usage (scheduler does nothing while sleeping).
            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        # User pressed Ctrl+C — exit gracefully.
        print()
        _log("🛑 Scheduler stopped by user (Ctrl+C). Goodbye!")
        logger.info("Scheduler stopped by user request.")
        sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: Hourly heartbeat message
# ─────────────────────────────────────────────────────────────────────────────
_last_heartbeat_hour: int = -1   # Module-level variable to track last heartbeat

def _maybe_print_heartbeat() -> None:
    """
    Print a status line once per hour so you can see the scheduler is alive.

    Without this, the terminal would be completely silent between jobs.
    A periodic message lets you glance at the terminal and confirm it's running.
    """
    global _last_heartbeat_hour

    current_hour = datetime.datetime.now().hour
    if current_hour != _last_heartbeat_hour:
        _last_heartbeat_hour = current_hour

        next_run = schedule.next_run()
        if next_run:
            delta   = next_run - datetime.datetime.now()
            hours   = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            _log(f"⏳ Waiting...  — Next job in {hours}h {minutes}m  "
                 f"(scheduled for {SCHEDULE_TIME})")


# ─────────────────────────────────────────────────────────────────────────────
#  DRY RUN — shows schedule info without actually running the pipeline
# ─────────────────────────────────────────────────────────────────────────────

def dry_run() -> None:
    """
    Show schedule configuration without running the pipeline or sending email.
    Useful for verifying settings before deploying.
    """
    print(f"\n{_DLINE}")
    print("  🧪 DRY RUN  —  Scheduler configuration check")
    print(_DLINE)

    config.print_config_summary()

    setup_schedule()
    next_run = schedule.next_run()

    print(f"\n  Schedule details:")
    print(f"    Run time      : {SCHEDULE_TIME} (24-hour format)")
    print(f"    Frequency     : Every day")
    print(f"    Next run      : {next_run.strftime('%Y-%m-%d at %H:%M') if next_run else 'unknown'}")
    print(f"    Poll interval : every {POLL_INTERVAL_SECONDS}s")
    print(f"\n  Pipeline that will run:")
    print(f"    1. Fetch news (NewsAPI)")
    print(f"    2. Summarise with {config.GEMINI_MODEL} (Gemini)")
    print(f"    3. Render HTML template")
    print(f"    4. Send to {config.EMAIL_RECIPIENT} via Gmail SMTP")
    print(f"\n  ✅ Dry run complete — no email sent, no API calls made.")
    print(f"{_DLINE}\n")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT + COMMAND-LINE FLAGS
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # Parse simple command-line flags (no extra library needed).
    # sys.argv is the list of words typed after "python scheduler.py".
    # e.g. "python scheduler.py --now"  →  sys.argv = ["scheduler.py", "--now"]

    args = sys.argv[1:]   # Everything after "scheduler.py"

    if "--test" in args or "--dry-run" in args:
        # Show schedule info without running anything
        dry_run()

    elif "--now" in args:
        # Run the pipeline immediately, then enter the scheduler loop
        start_scheduler(run_now_first=True)

    else:
        # Default: just start the scheduler and wait for the scheduled time
        start_scheduler(run_now_first=False)


# ═══════════════════════════════════════════════════════════════════════════════
#  KEEPING THE SCHEDULER RUNNING CONTINUOUSLY
#  (How to run it as a background service on Windows)
# ═══════════════════════════════════════════════════════════════════════════════
#
#  PROBLEM:
#    If you just run `python scheduler.py` in a terminal, it stops when:
#    • You close the terminal window
#    • Your computer goes to sleep
#    • You log out
#
#  SOLUTIONS (pick one):
#
#  ────────────────────────────────────────────────────────────────────────────
#  OPTION 1: Windows Task Scheduler (RECOMMENDED for Windows)
#  ────────────────────────────────────────────────────────────────────────────
#    Use Windows Task Scheduler to run app.py directly at 8:00 AM.
#    No need to keep scheduler.py running 24/7.
#
#    Steps:
#    1. Press Win + S → search "Task Scheduler" → open it
#    2. Click "Create Basic Task"
#    3. Name: "AI News Agent"
#    4. Trigger: Daily at 08:00
#    5. Action: Start a program
#       Program:   C:\Users\YourName\AppData\Local\Python\pythoncore-3.14-64\python.exe
#       Arguments: C:\IT\Projects\api-agent\app.py
#       Start in:  C:\IT\Projects\api-agent
#    6. Finish → your email will arrive every morning automatically!
#
#    Advantage: Works even when no terminal is open. Survives reboots.
#    Disadvantage: Requires Windows Task Scheduler setup.
#
#  ────────────────────────────────────────────────────────────────────────────
#  OPTION 2: Keep Terminal Open (Simplest for testing)
#  ────────────────────────────────────────────────────────────────────────────
#    Just leave the terminal running with scheduler.py active.
#    Minimise it and let your PC stay on overnight.
#
#    python scheduler.py
#    → You'll see "⏳ Waiting..." and then "🚀 Running..." at 8:00 AM.
#
#    Advantage: No setup needed, great for testing.
#    Disadvantage: Stops if you close the terminal or the PC sleeps.
#
#  ────────────────────────────────────────────────────────────────────────────
#  OPTION 3: Run in background with pythonw (Windows, no terminal window)
#  ────────────────────────────────────────────────────────────────────────────
#    pythonw.exe runs Python without showing a terminal window.
#    Create run_background.bat in your project:
#
#      @echo off
#      start "" "C:\Python\pythonw.exe" "C:\IT\Projects\api-agent\scheduler.py"
#      echo Scheduler started in background.
#
#    Double-click run_background.bat to start it silently.
#    To stop it: open Task Manager → find pythonw.exe → End Task.
#
#  ────────────────────────────────────────────────────────────────────────────
#  OPTION 4: NSSM (Non-Sucking Service Manager) — Windows Service
#  ────────────────────────────────────────────────────────────────────────────
#    NSSM wraps your Python script as a real Windows Service that
#    starts automatically on boot and restarts if it crashes.
#
#    1. Download NSSM: https://nssm.cc/download
#    2. Run: nssm install "AI News Agent"
#    3. Fill in Python path and scheduler.py path
#    4. Start: nssm start "AI News Agent"
#
#    Advantage: Full service — survives reboots, auto-restart on crash.
#    Disadvantage: Requires NSSM installation.
#
# ═══════════════════════════════════════════════════════════════════════════════
