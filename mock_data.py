"""
mock_data.py — Shared Test Data for Verification
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Contains structured mock news articles and summaries. This allows us to test
  the email template rendering, email dispatching, and run diagnostic test suites
  without making active requests to NewsAPI or Google Gemini APIs.

  Having a single file prevents code duplication across test runners.
═══════════════════════════════════════════════════════════════════════════════
"""

import datetime

# Realistic sample articles with simulated Gemini summary outputs.
# Used by: preview_email.py, email_sender.py, run_tests.py
SAMPLE_ARTICLES = [
    {
        "title":           "OpenAI Releases GPT-5 with Unprecedented Reasoning Abilities",
        "source":          "TechCrunch",
        "url":             "https://techcrunch.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "OpenAI has released GPT-5, its most capable language model to date, "
            "showcasing dramatically improved reasoning, coding, and multimodal capabilities. "
            "The model is now available via API and will roll out to ChatGPT users next week."
        ),
        "bullets": [
            "GPT-5 scores 95% on MMLU benchmark, beating all previous models",
            "Available via API today — ChatGPT rollout begins in 7 days",
            "Pricing stays the same as GPT-4 Turbo for now",
        ],
        "why_it_matters":  "This is the biggest capability jump in AI since GPT-4 — developers should evaluate migration paths now.",
        "relevance_score": 5,
        "summary_error":   False,
    },
    {
        "title":           "Microsoft Integrates Copilot AI into Every Windows 11 Feature",
        "source":          "The Verge",
        "url":             "https://theverge.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "Microsoft's June update embeds Copilot AI deeply into Windows 11, "
            "adding AI-powered search, file summarisation, and natural-language settings control. "
            "The update rolls out automatically to all Windows 11 users this week."
        ),
        "bullets": [
            "AI now powers Windows Search, File Explorer, and Settings",
            "Copilot can summarise any open document or email in one click",
            "Requires internet connection — offline mode planned for Q3",
        ],
        "why_it_matters":  "Enterprise IT teams need to review Copilot data privacy settings before the auto-update reaches corporate fleets.",
        "relevance_score": 4,
        "summary_error":   False,
    },
    {
        "title":           "Google DeepMind Achieves Breakthrough in Protein Structure Prediction",
        "source":          "Nature",
        "url":             "https://nature.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "Google DeepMind's AlphaFold 3 has successfully predicted the structure of "
            "every known protein with near-experimental accuracy, opening new frontiers "
            "in drug discovery and biological research."
        ),
        "bullets": [
            "AlphaFold 3 predicts protein structures at 99.2% accuracy",
            "Free database now covers 200 million proteins across all known life",
            "Pharmaceutical companies are integrating it into drug discovery pipelines",
        ],
        "why_it_matters":  "This could cut drug discovery timelines from decades to years — the single biggest AI impact on human health so far.",
        "relevance_score": 5,
        "summary_error":   False,
    },
    {
        "title":           "Anthropic's Claude 4 Outperforms GPT-5 on Coding Benchmarks",
        "source":          "Ars Technica",
        "url":             "https://arstechnica.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "Anthropic released Claude 4 today, which scores higher than GPT-5 on "
            "SWE-Bench and HumanEval coding benchmarks. Claude 4 can autonomously "
            "complete multi-file coding tasks with minimal human oversight."
        ),
        "bullets": [
            "Claude 4 scores 72% on SWE-Bench vs GPT-5's 68%",
            "Can autonomously fix bugs across entire codebases in one session",
            "Available on Claude.ai and via API — 200K context window",
        ],
        "why_it_matters":  "Software developers now have two world-class AI coding assistants competing — expect both to improve rapidly.",
        "relevance_score": 5,
        "summary_error":   False,
    },
    {
        "title":           "Tesla FSD Version 14 Achieves Zero Human Interventions in 10,000-Mile Test",
        "source":          "Electrek",
        "url":             "https://electrek.co",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "Tesla's Full Self-Driving version 14, powered by a new end-to-end neural network, "
            "completed a 10,000-mile cross-country test with zero driver interventions. "
            "This marks a major milestone toward Level 4 autonomous driving."
        ),
        "bullets": [
            "10,000 miles with zero human interventions across highway and urban driving",
            "New end-to-end neural architecture replaces the old rule-based system",
            "Regulatory approval for unsupervised driving still pending in most states",
        ],
        "why_it_matters":  "If regulators approve, Tesla could begin true robotaxi operations in select cities within 12 months.",
        "relevance_score": 4,
        "summary_error":   False,
    },
    # Breaking/General news (relevance score < 3 → goes in breaking news section)
    {
        "title":           "India Passes Landmark National AI Regulation Framework",
        "source":          "Reuters",
        "url":             "https://reuters.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "summary":         (
            "The Indian government passed a comprehensive AI regulation framework requiring "
            "transparency, bias audits, and human oversight for high-risk AI systems. "
            "Companies have 18 months to comply before penalties apply."
        ),
        "bullets":         [],
        "why_it_matters":  "Every company deploying AI in India must comply within 18 months.",
        "relevance_score": 2,
        "summary_error":   False,
    },
]
