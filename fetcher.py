"""
fetcher.py — News Fetcher
──────────────────────────
Responsibility: Talk to the NewsAPI and return a list of articles.

What it does (when logic is added):
  1. Reads NEWS_API_KEY and NEWS_QUERY from config.
  2. Sends an HTTP GET request to NewsAPI.
  3. Parses the JSON response.
  4. Returns a clean Python list of article dictionaries like:
       [
         {
           "title": "...",
           "description": "...",
           "url": "...",
           "source": "...",
           "published_at": "..."
         },
         ...
       ]

This module knows NOTHING about emails or AI — it only fetches news.
That separation keeps the code easy to swap (e.g., use a different
news source later) without touching anything else.
"""
