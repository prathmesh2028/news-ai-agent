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
        "urlToImage":      "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&h=340&fit=crop",
        "category":        "AI & ML",
        "summary":         (
            "OpenAI has officially released GPT-5, its most capable language model to date, "
            "showcasing dramatically improved reasoning, coding, and multimodal capabilities. "
            "The model demonstrates near-human-level performance on complex reasoning tasks, "
            "scoring 95% on the MMLU benchmark — a significant leap from GPT-4's 86%. "
            "GPT-5 is now available via API for developers and will roll out to ChatGPT Plus "
            "and Enterprise users over the coming week. OpenAI has maintained pricing parity "
            "with GPT-4 Turbo for the initial launch, though premium tier pricing is expected "
            "to follow for advanced features including autonomous agent capabilities."
        ),
        "bullets": [
            "GPT-5 scores 95% on MMLU benchmark, beating all previous models by a wide margin",
            "Available via API today — ChatGPT rollout begins in 7 days for Plus subscribers",
            "Pricing stays the same as GPT-4 Turbo for standard usage tiers",
            "New autonomous agent mode allows multi-step task completion without human oversight",
            "Multimodal improvements include real-time video understanding and generation",
        ],
        "why_it_matters":  "This is the biggest capability jump in AI since GPT-4 — developers should evaluate migration paths now, as GPT-5's reasoning abilities fundamentally change what's possible with AI applications.",
        "relevance_score": 5,
        "summary_error":   False,
        "read_time_minutes": 4,
    },
    {
        "title":           "Microsoft Integrates Copilot AI into Every Windows 11 Feature",
        "source":          "The Verge",
        "url":             "https://theverge.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "urlToImage":      "https://images.unsplash.com/photo-1633419461186-7d40a38105ec?w=600&h=340&fit=crop",
        "category":        "Big Tech",
        "summary":         (
            "Microsoft's June update embeds Copilot AI deeply into Windows 11, "
            "adding AI-powered search, file summarisation, and natural-language settings control. "
            "Users can now ask Copilot to find files by describing their content, summarise "
            "any open document with a single click, and adjust system settings using plain English. "
            "The update rolls out automatically to all Windows 11 users this week. "
            "Enterprise administrators can configure data privacy boundaries through Intune "
            "to control what information Copilot can access on managed devices."
        ),
        "bullets": [
            "AI now powers Windows Search, File Explorer, and Settings with natural language",
            "Copilot can summarise any open document or email in one click across Office apps",
            "Requires internet connection — offline mode planned for Q3 2026 release",
            "Enterprise IT teams can set privacy boundaries via Microsoft Intune policies",
            "Integration includes real-time translation in Windows apps for 40+ languages",
        ],
        "why_it_matters":  "Enterprise IT teams need to review Copilot data privacy settings before the auto-update reaches corporate fleets. This represents the deepest AI integration in any desktop OS to date.",
        "relevance_score": 4,
        "summary_error":   False,
        "read_time_minutes": 3,
    },
    {
        "title":           "Google DeepMind Achieves Breakthrough in Protein Structure Prediction",
        "source":          "Nature",
        "url":             "https://nature.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "urlToImage":      "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=600&h=340&fit=crop",
        "category":        "AI & ML",
        "summary":         (
            "Google DeepMind's AlphaFold 3 has successfully predicted the structure of "
            "every known protein with near-experimental accuracy, opening new frontiers "
            "in drug discovery and biological research. The model achieves 99.2% accuracy "
            "on protein structure prediction benchmarks, making it practically indistinguishable "
            "from experimental methods that take months or years. The complete database of "
            "200 million predicted protein structures is freely available to researchers worldwide, "
            "and several pharmaceutical companies have already begun integrating it into their "
            "drug discovery pipelines to dramatically accelerate candidate identification."
        ),
        "bullets": [
            "AlphaFold 3 predicts protein structures at 99.2% accuracy, rivaling lab experiments",
            "Free database now covers 200 million proteins across all known forms of life",
            "Pharmaceutical companies are integrating it into drug discovery pipelines immediately",
            "Could reduce drug development timelines from 10+ years to 2-3 years for some targets",
            "Open-source weights released for academic research, commercial API available",
            "WHO endorses the database as a critical resource for neglected disease research",
        ],
        "why_it_matters":  "This could cut drug discovery timelines from decades to years — the single biggest AI impact on human health so far, with immediate implications for pharma, biotech, and academic research.",
        "relevance_score": 5,
        "summary_error":   False,
        "read_time_minutes": 5,
    },
    {
        "title":           "Anthropic's Claude 4 Outperforms GPT-5 on Coding Benchmarks",
        "source":          "Ars Technica",
        "url":             "https://arstechnica.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "urlToImage":      "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=600&h=340&fit=crop",
        "category":        "AI & ML",
        "summary":         (
            "Anthropic released Claude 4 today, which scores higher than GPT-5 on "
            "SWE-Bench and HumanEval coding benchmarks. Claude 4 can autonomously "
            "complete multi-file coding tasks with minimal human oversight, achieving "
            "a 72% success rate on SWE-Bench compared to GPT-5's 68%. The model features "
            "a 200K context window and demonstrates significantly improved instruction "
            "following for complex software engineering tasks. Anthropic is positioning "
            "Claude 4 as the premier choice for developer tooling and enterprise code generation."
        ),
        "bullets": [
            "Claude 4 scores 72% on SWE-Bench vs GPT-5's 68%, establishing a new benchmark leader",
            "Can autonomously fix bugs across entire codebases in one session with high accuracy",
            "Available on Claude.ai and via API — 200K context window for large codebase analysis",
            "New 'extended thinking' mode shows reasoning process for complex debugging tasks",
            "Enterprise tier includes SOC 2 compliance and on-premise deployment options",
        ],
        "why_it_matters":  "Software developers now have two world-class AI coding assistants competing head-to-head — expect both to improve rapidly as the competitive pressure intensifies.",
        "relevance_score": 5,
        "summary_error":   False,
        "read_time_minutes": 3,
    },
    {
        "title":           "Tesla FSD Version 14 Achieves Zero Human Interventions in 10,000-Mile Test",
        "source":          "Electrek",
        "url":             "https://electrek.co",
        "publishedAt":     datetime.date.today().isoformat(),
        "urlToImage":      None,  # No image available — tests placeholder
        "category":        "Technology",
        "summary":         (
            "Tesla's Full Self-Driving version 14, powered by a new end-to-end neural network, "
            "completed a 10,000-mile cross-country test with zero driver interventions. "
            "This marks a major milestone toward Level 4 autonomous driving and represents "
            "a fundamental shift from the company's previous rule-based approach. The new "
            "architecture processes raw camera feeds directly into driving decisions without "
            "intermediate symbolic representations. Regulatory approval for unsupervised driving "
            "remains pending in most states, with California and Texas expected to decide first."
        ),
        "bullets": [
            "10,000 miles with zero human interventions across highway and urban driving scenarios",
            "New end-to-end neural architecture replaces the old rule-based system entirely",
            "Regulatory approval for unsupervised driving still pending in most US states",
            "California and Texas regulatory decisions expected within the next 6 months",
            "Insurance implications could reduce Tesla owner premiums by up to 40%",
        ],
        "why_it_matters":  "If regulators approve, Tesla could begin true robotaxi operations in select cities within 12 months, fundamentally disrupting ride-hailing and delivery industries.",
        "relevance_score": 4,
        "summary_error":   False,
        "read_time_minutes": 4,
    },
    # Breaking/General news (relevance score < 3 → goes in breaking news section)
    {
        "title":           "India Passes Landmark National AI Regulation Framework",
        "source":          "Reuters",
        "url":             "https://reuters.com",
        "publishedAt":     datetime.date.today().isoformat(),
        "urlToImage":      "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&h=340&fit=crop",
        "category":        "Breaking News",
        "summary":         (
            "The Indian government passed a comprehensive AI regulation framework requiring "
            "transparency, bias audits, and human oversight for high-risk AI systems. "
            "Companies deploying AI in healthcare, finance, law enforcement, and education "
            "will need to conduct mandatory algorithmic impact assessments and maintain "
            "detailed audit trails. The framework includes provisions for an AI Safety Board "
            "with enforcement powers and penalty authority up to 4% of global revenue. "
            "Companies have 18 months to comply before penalties apply."
        ),
        "bullets": [
            "Mandatory bias audits and transparency requirements for high-risk AI systems",
            "18-month compliance window before penalties take effect for all companies",
            "AI Safety Board established with enforcement powers and up to 4% revenue fines",
            "Affects healthcare, finance, law enforcement, and education AI deployments",
        ],
        "why_it_matters":  "Every company deploying AI in India must comply within 18 months — this joins the EU AI Act as the second major regulatory framework globally.",
        "relevance_score": 2,
        "summary_error":   False,
        "read_time_minutes": 3,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  EXECUTIVE SUMMARY — Mock Gemini-generated executive brief
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_EXECUTIVE_SUMMARY = [
    "OpenAI released GPT-5 with near-human reasoning, scoring 95% on MMLU and launching autonomous agent capabilities.",
    "Anthropic's Claude 4 immediately challenged GPT-5's dominance, outperforming it on SWE-Bench coding benchmarks at 72% vs 68%.",
    "Google DeepMind's AlphaFold 3 achieved 99.2% accuracy in protein structure prediction, with major pharmaceutical companies already integrating the technology.",
    "Microsoft embedded Copilot AI deeply into Windows 11, making it the most AI-integrated desktop operating system ever released.",
    "Tesla's FSD Version 14 completed 10,000 miles with zero human interventions, bringing autonomous driving closer to regulatory approval.",
    "India passed a landmark AI regulation framework requiring bias audits and transparency, joining the EU as the second major AI regulatory body.",
]


# ─────────────────────────────────────────────────────────────────────────────
#  AI QUOTE — Mock Gemini-generated inspirational quote
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_AI_QUOTE = {
    "text": "Artificial intelligence is not a substitute for human intelligence; it is a tool to amplify human creativity and ingenuity.",
    "author": "Fei-Fei Li",
}


# ─────────────────────────────────────────────────────────────────────────────
#  MARKET MENTIONS — Which companies appeared in today's news
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_MARKET_MENTIONS = {
    "NVIDIA":    False,
    "Microsoft": True,
    "Google":    True,
    "Meta":      False,
    "OpenAI":    True,
    "Anthropic": True,
    "Apple":     False,
    "Amazon":    False,
}

# Post-process mock data to ensure all required template fields are present
for _a in SAMPLE_ARTICLES:
    if "source_logo" not in _a:
        _domain = _a.get("url", "").split("//")[-1].split("/")[0]
        _a["source_logo"] = f"https://www.google.com/s2/favicons?domain={_domain}&sz=64" if _domain else None
    if "read_time_minutes" not in _a:
        # Estimate from summary or description
        _text = _a.get("summary", "") or _a.get("description", "")
        _words = len(_text.split())
        _a["read_time_minutes"] = max(2, round(_words / 200 * 5))

