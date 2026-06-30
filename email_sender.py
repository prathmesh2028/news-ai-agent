"""
email_sender.py — Gmail SMTP Email Dispatcher
═══════════════════════════════════════════════════════════════════════════════
PURPOSE:
  Sends a beautiful HTML email via Gmail's SMTP server.
  Reads credentials (Gmail address + App Password) from the .env file.

  This module's job is ONLY sending — it doesn't fetch news or summarise.
  It takes ready-made content and delivers it.

─────────────────────────────────────────────────────────────────────────────
HOW EMAIL SENDING WORKS (SMTP — for beginners):
─────────────────────────────────────────────────────────────────────────────

  SMTP stands for "Simple Mail Transfer Protocol."
  It's the universal standard for SENDING email, like a digital postal service.

  The journey of your email, step by step:

  YOUR PYTHON SCRIPT
      │
      │  1. Opens a TCP connection to Gmail's mail server
      │     (smtp.gmail.com on port 587)
      │
      ▼
  GMAIL SMTP SERVER (smtp.gmail.com:587)
      │
      │  2. Negotiates STARTTLS — upgrades the connection to encrypted TLS.
      │     Without this, your password would travel in plain text. ❌
      │     With TLS, everything is encrypted. ✅
      │
      │  3. Login: we send our Gmail address + App Password.
      │     Gmail verifies our identity before allowing any sending.
      │
      │  4. We hand off the email: FROM, TO, SUBJECT, HTML BODY.
      │     Gmail accepts it and queues it for delivery.
      │
      ▼
  RECIPIENT'S MAIL SERVER (e.g., Gmail, Outlook, Yahoo)
      │
      │  5. Gmail delivers the email to the recipient's inbox.
      │     This happens within seconds.
      │
      ▼
  RECIPIENT'S INBOX ✉️

  KEY TERMS:
    SMTP Port 587  = standard port for "submission" (sending mail with auth)
    STARTTLS       = command that upgrades plain connection → encrypted TLS
    App Password   = a 16-character Google-generated password for apps
                     (required when Gmail 2FA is enabled — safer than your
                     real password because it can be revoked independently)
    MIMEMultipart  = email format that bundles plain text + HTML together
    MIMEText       = a single content part (either plain text or HTML)

─────────────────────────────────────────────────────────────────────────────
GMAIL SETUP (one-time — REQUIRED before this works):
─────────────────────────────────────────────────────────────────────────────

  1. Enable 2-Factor Authentication on your Google account:
     https://myaccount.google.com/security

  2. Generate a Gmail App Password:
     https://myaccount.google.com/apppasswords
     → Select "Mail" + "Windows Computer" → Generate
     → Copy the 16-character password (e.g., "abcd efgh ijkl mnop")

  3. Add to your .env file:
     EMAIL_ADDRESS  = your.email@gmail.com
     EMAIL_PASSWORD = abcdefghijklmnop   ← the 16-char App Password, no spaces
     EMAIL_RECIPIENT= recipient@gmail.com
     SMTP_SERVER    = smtp.gmail.com
     SMTP_PORT      = 587

HOW TO USE FROM OTHER MODULES:
  from email_sender import send_email
  success = send_email(
      recipient="someone@gmail.com",
      subject="My Subject",
      html_body="<h1>Hello!</h1>"
  )

HOW TO TEST IN ISOLATION:
  python email_sender.py
═══════════════════════════════════════════════════════════════════════════════
"""

import smtplib                               # Python's built-in SMTP library
from email.mime.multipart import MIMEMultipart  # Builds a multi-part email container
from email.mime.text import MIMEText         # Wraps text/HTML content into MIME format

import config                                # Loads EMAIL_ADDRESS, EMAIL_PASSWORD, etc.
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PUBLIC FUNCTION: send_email()
# ─────────────────────────────────────────────────────────────────────────────

def send_email(recipient: str, subject: str, html_body: str) -> bool:
    """
    Send an HTML email via Gmail SMTP.

    This function handles the ENTIRE email sending process:
      1. Builds the MIME email object (the email "envelope + letter")
      2. Connects to Gmail's SMTP server (smtp.gmail.com:587)
      3. Upgrades the connection to TLS (encryption)
      4. Logs in with your Gmail App Password
      5. Sends the email
      6. Closes the connection cleanly

    Args:
        recipient (str) : Email address to send to. Example: "you@gmail.com"
        subject   (str) : Email subject line. Example: "🤖 Your Daily AI News"
        html_body (str) : Full HTML string for the email body.

    Returns:
        True  — email was accepted by Gmail and is on its way.
        False — something went wrong (error is printed, no crash).
    """

    # ── STEP 1: Validate inputs before even trying to connect ──────────────
    # Catch obvious mistakes early with a helpful message.
    if not recipient or "@" not in recipient:
        print(f"❌ [Email] Invalid recipient address: '{recipient}'")
        return False

    if not html_body or len(html_body.strip()) < 10:
        print("❌ [Email] HTML body is empty — nothing to send.")
        return False

    if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
        print(
            "❌ [Email] Missing credentials in .env\n"
            "   Make sure EMAIL_ADDRESS and EMAIL_PASSWORD are set."
        )
        return False

    print(f"\n📧 Sending email...")
    print(f"   From    : {config.EMAIL_ADDRESS}")
    print(f"   To      : {recipient}")
    print(f"   Subject : {subject}")
    logger.info(f"Initiating email send sequence to recipient: {recipient}")

    # ── STEP 2: Build the MIME email object ────────────────────────────────
    #
    # MIME = Multipurpose Internet Mail Extensions.
    # It's the format standard that lets emails carry both text and HTML.
    #
    # MIMEMultipart("alternative") = an email with TWO versions:
    #   - plain text (fallback for very old clients)
    #   - HTML       (shown by Gmail, Outlook, Apple Mail, etc.)
    # Email clients automatically show the version they support best.
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = config.EMAIL_ADDRESS   # The "From:" header visible to recipient
    msg["To"]      = recipient              # The "To:" header visible to recipient

    # ── STEP 2a: Plain-text fallback ────────────────────────────────────
    # A simple text version shown if the email client can't render HTML.
    # Very few modern clients need this, but it's professional to include.
    plain_text = (
        f"Subject: {subject}\n\n"
        "This email contains an HTML digest. "
        "Please view it in an HTML-capable email client (e.g., Gmail, Outlook).\n\n"
        "Powered by AI News Agent + Google Gemini."
    )

    # ── STEP 2b: HTML version ────────────────────────────────────────────
    # This is what almost all recipients will see — the beautiful digest.
    # IMPORTANT: The HTML version MUST be attached last.
    # The MIME standard says: email clients prefer the LAST part they understand.
    # So we attach plain first, HTML second.
    part_plain = MIMEText(plain_text, "plain", "utf-8")
    part_html  = MIMEText(html_body,  "html",  "utf-8")
    msg.attach(part_plain)
    msg.attach(part_html)   # ← attached last = preferred by email clients

    print(f"   ✅ Email object built ({len(html_body):,} bytes HTML body)")

    # ── STEP 3: Connect to Gmail SMTP and send ────────────────────────────
    #
    # smtplib.SMTP(server, port) opens a network connection to the mail server.
    # We use a `with` block — this ensures the connection is ALWAYS closed
    # cleanly when we're done, even if an error occurs.
    #
    # Think of it like opening and closing a phone call.
    try:
        print(f"   🌐 Connecting to {config.SMTP_SERVER}:{config.SMTP_PORT}...")

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp_connection:

            # ── STEP 3a: EHLO — "Hello, I'm a mail client" ──────────────
            # EHLO is the opening greeting in the SMTP protocol.
            # It tells the server what capabilities our client supports.
            # smtplib does this automatically inside SMTP(), but it's
            # good to know this is happening under the hood.

            # ── STEP 3b: STARTTLS — upgrade to encrypted connection ──────
            # Before sending any credentials, we MUST encrypt the connection.
            # starttls() sends the STARTTLS command to the server,
            # which upgrades our plain TCP connection to encrypted TLS.
            # Without this, your password travels in plain text — never skip it.
            smtp_connection.starttls()
            print("   🔒 TLS encryption enabled (connection is secure)")

            # ── STEP 3c: Login — authenticate with Gmail ─────────────────
            # Gmail requires authentication before accepting any emails.
            # EMAIL_PASSWORD must be a Gmail App Password (16 chars), NOT
            # your normal Gmail password.
            smtp_connection.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            print(f"   🔑 Authenticated as {config.EMAIL_ADDRESS}")

            # ── STEP 3d: sendmail() — hand off the email to Gmail ─────────
            # This sends the assembled MIME message to Gmail's servers.
            # Gmail then routes it to the recipient's mail server.
            # Arguments: from_addr, [list_of_recipients], raw_message_string
            smtp_connection.sendmail(
                from_addr = config.EMAIL_ADDRESS,
                to_addrs  = [recipient],
                msg       = msg.as_string(),   # Convert MIMEMultipart → raw string
            )

        # ── If we reach this line, the email was successfully accepted ──
        print(
            f"\n{'─'*60}\n"
            f"  ✅ Email sent successfully!\n"
            f"     To      : {recipient}\n"
            f"     Subject : {subject}\n"
            f"     Check your inbox in 5-10 seconds.\n"
            f"{'─'*60}\n"
        )
        logger.info(f"Email sent successfully to recipient: {recipient} (subject: {subject})")
        return True

    # ── ERROR HANDLING — each error has its own friendly explanation ────────

    except smtplib.SMTPAuthenticationError as error:
        # Gmail rejected our username/password.
        # Most common cause: using your real Gmail password instead of App Password.
        print(
            "\n❌ Authentication failed — Gmail rejected the login credentials.\n"
            "\n   LIKELY CAUSE:\n"
            "   You're using your real Gmail password. Gmail BLOCKS this.\n"
            "   You MUST use a Gmail App Password instead.\n"
            "\n   HOW TO FIX:\n"
            "   1. Go to: https://myaccount.google.com/apppasswords\n"
            "   2. Create an App Password for 'Mail'\n"
            "   3. Copy the 16-character password (e.g. abcdefghijklmnop)\n"
            "   4. Update EMAIL_PASSWORD in your .env file\n"
            "      (no spaces in the password)\n"
        )
        logger.error(f"SMTP Authentication failed for {config.EMAIL_ADDRESS}: {error}")
        return False

    except smtplib.SMTPConnectError as error:
        # Could not even establish a connection to Gmail's server.
        # Usually a firewall, wrong port, or server outage.
        print(
            f"\n❌ Could not connect to the SMTP server.\n"
            f"   Server : {config.SMTP_SERVER}\n"
            f"   Port   : {config.SMTP_PORT}\n"
            f"   Error  : {error}\n"
            "\n   POSSIBLE CAUSES:\n"
            "   • Your firewall is blocking outgoing port 587\n"
            "   • SMTP_SERVER or SMTP_PORT is wrong in .env\n"
            "   • Gmail SMTP is temporarily down\n"
        )
        logger.error(f"SMTP connection error to {config.SMTP_SERVER}:{config.SMTP_PORT}: {error}")
        return False

    except smtplib.SMTPRecipientsRefused as error:
        # Gmail accepted the connection but refused to send to this recipient.
        # Usually a typo in the email address.
        print(
            f"\n❌ Recipient address was refused by Gmail.\n"
            f"   Recipient : {recipient}\n"
            f"   Error     : {error}\n"
            "\n   FIX: Double-check the recipient email address.\n"
        )
        logger.error(f"SMTP recipient refused for {recipient}: {error}")
        return False

    except smtplib.SMTPSenderRefused as error:
        # Gmail refused to accept the FROM address.
        # Usually EMAIL_ADDRESS doesn't match the authenticated account.
        print(
            f"\n❌ Sender address was refused.\n"
            f"   Sender : {config.EMAIL_ADDRESS}\n"
            f"   Error  : {error}\n"
            "\n   FIX: Make sure EMAIL_ADDRESS matches the Gmail account\n"
            "        you used to generate the App Password.\n"
        )
        logger.error(f"SMTP sender refused for {config.EMAIL_ADDRESS}: {error}")
        return False

    except smtplib.SMTPException as error:
        # Generic SMTP error — catch-all for any other SMTP-level failure.
        print(
            f"\n❌ An SMTP error occurred while sending.\n"
            f"   Error : {error}\n"
        )
        logger.error(f"SMTP error during send: {error}")
        return False

    except OSError as error:
        # OSError (or ConnectionError / TimeoutError) = network-level failure.
        # This means Python couldn't even reach smtp.gmail.com.
        print(
            f"\n❌ Network error — could not reach {config.SMTP_SERVER}.\n"
            f"   Error : {error}\n"
            "\n   POSSIBLE CAUSES:\n"
            "   • No internet connection\n"
            "   • DNS resolution failed\n"
            "   • Network timeout (server took too long to respond)\n"
            "\n   FIX: Check your internet connection and try again.\n"
        )
        logger.error(f"Network error (SMTP server unreachable): {error}")
        return False

    except Exception as error:
        # Final safety net — catches anything we didn't anticipate.
        print(f"\n❌ Unexpected error while sending email: {error}\n")
        logger.error(f"Unexpected exception in send_email: {error}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  QUICK TEST — run directly: python email_sender.py
# ─────────────────────────────────────────────────────────────────────────────
# Sends a simple real HTML email to test your Gmail credentials.
# Does NOT use NewsAPI or Gemini — just tests the SMTP connection.

if __name__ == "__main__":

    # Show current config so we can verify credentials at a glance.
    config.print_config_summary()

    # Minimal HTML email for testing SMTP — no Jinja2 template needed here.
    test_html = """
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:24px; background-color:#0f0f1a;
                 font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center">
            <table role="presentation" width="560" cellpadding="0" cellspacing="0"
              style="background-color:#111132; border:1px solid rgba(99,179,237,0.2);
                     border-radius:14px; padding:36px 32px; text-align:center;">
              <tr>
                <td style="font-size:40px; padding-bottom:16px;">🤖</td>
              </tr>
              <tr>
                <td style="font-size:24px; font-weight:800; color:#ffffff;
                            padding-bottom:12px;">
                  SMTP Connection Test
                </td>
              </tr>
              <tr>
                <td style="font-size:15px; color:#68d391; font-weight:600;
                            padding-bottom:20px;">
                  ✅ Gmail SMTP is working correctly!
                </td>
              </tr>
              <tr>
                <td style="font-size:14px; color:#a0aec0; line-height:1.7;
                            padding-bottom:24px;">
                  If you can read this, your <strong style="color:#63b3ed;">email_sender.py</strong>
                  is correctly connected to Gmail SMTP.<br/>
                  Your credentials are valid and email delivery is working.
                </td>
              </tr>
              <tr>
                <td style="font-size:12px; color:#4a5568; border-top:1px solid rgba(255,255,255,0.07);
                            padding-top:20px;">
                  AI News Agent &nbsp;·&nbsp; email_sender.py test &nbsp;·&nbsp;
                  Powered by Google Gemini
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    print("\n📤 Sending SMTP test email...")
    print("   (This tests your Gmail credentials — no NewsAPI or Gemini needed)\n")

    success = send_email(
        recipient = config.EMAIL_RECIPIENT,
        subject   = "✅ AI News Agent — SMTP Test",
        html_body = test_html,
    )

    if success:
        print(f"🎉 Check your inbox: {config.EMAIL_RECIPIENT}")
        print("   If the email arrived, SMTP is fully working. ✅")
        print("   You're ready to run main.py!\n")
    else:
        print("💥 Test failed — see the error above for the fix.\n")
