"""
main.py — Main Entry Point for AI News Agent
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  This is the clean, standard entry point for the application.
  It imports the orchestrator pipeline logic from app.py and executes it.

USAGE:
  python main.py
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
from app import run_pipeline

if __name__ == "__main__":
    success = run_pipeline()
    # Exit with code 0 (success) or 1 (failure)
    sys.exit(0 if success else 1)
