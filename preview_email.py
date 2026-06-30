"""
preview_email.py — Generate a local HTML preview of the email
─────────────────────────────────────────────────────────────
Renders the HTML email template with sample data and saves it as
email_preview.html — open that file in your browser to see
exactly how the email will look, without sending anything.

Usage:
    python preview_email.py
    Then open email_preview.html in Chrome/Edge/Firefox.
"""

import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

import config
from mock_data import SAMPLE_ARTICLES   # Shared mock data module


def generate_preview():
    """Render the email template with sample data and save as HTML file."""

    # Load templates from standardized config paths
    template_dir  = config.TEMPLATE_DIR
    template_file = config.TEMPLATE_FILE
    output_file   = Path(__file__).parent / "email_preview.html"

    # Set up Jinja2 environment pointing at the templates folder
    env      = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
    template = env.get_template(template_file)

    today_str = datetime.date.today().strftime("%A, %B %d, %Y")

    # Split articles into tech (score >= 3) vs breaking (score < 3)
    tech_articles     = [a for a in SAMPLE_ARTICLES if a.get("relevance_score", 3) >= 3]
    breaking_articles = [a for a in SAMPLE_ARTICLES if a.get("relevance_score", 3) < 3]

    # Render the template — this fills all {{ placeholders }}
    html = template.render(
        subject          = f"🤖 Your AI & Tech News Digest — {today_str}",
        date             = today_str,
        send_time        = datetime.datetime.now().strftime("%H:%M"),
        model            = config.GEMINI_MODEL,
        tech_articles    = tech_articles,
        breaking_articles= breaking_articles,
        total_articles   = len(SAMPLE_ARTICLES),
        tech_count       = len(tech_articles),
        breaking_count   = len(breaking_articles),
    )

    # Save to file
    output_file.write_text(html, encoding="utf-8")

    print(f"\n✅ Email preview generated!")
    print(f"   📄 File : {output_file}")
    print(f"   🌐 Open : Right-click → Open with Browser in VS Code")
    print(f"             Or drag the file into Chrome/Edge\n")


if __name__ == "__main__":
    generate_preview()
