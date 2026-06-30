# Changelog

All notable changes to the **AI News Agent** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-30

### Added
* **Interactive Test Menu**: Added `run_tests.py` supporting standalone module audits (Config, NewsAPI, Gemini, Gmail SMTP, and Scheduler).
* **Logging System**: Configured standard Python rotating logging to write application actions, warnings, and errors to `logs/app.log`.
* **Standardized Path Configs**: Centralized Jinja2 template folder and file specifications inside `config.py`.
* **Offline Mock Data**: Extracted static sample articles into `mock_data.py` to support layout design previews without active API tokens.

### Changed
* **SDK Migration**: Migrated from the deprecated `google-generativeai` package to the modern official `google-genai` SDK package.
* **Refactored Type Hints**: Added strict type annotations to all module function signatures (`list[dict[str, any]]`, etc.).
* **Improved Terminal Layout**: Redesigned execution prints into unified step-by-step reporting blocks.

### Removed
* Deleted redundant pre-implementation placeholder files (`fetcher.py` and `test_fetcher.py`).
