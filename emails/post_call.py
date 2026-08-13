"""Post–initial-call candidate emails (after Patrick call is completed)."""

from __future__ import annotations

from layout import BRAND_LIME, render_email

PORTAL_LOGIN = "https://s2score.service2software.org/candidatelogin"
PORTAL_HOME = "https://s2score.service2software.org/candidates/leads"
PORTAL_RESET = "https://s2score.service2software.org/candidatelogin/reset"
CORE_LOGIN = "https://s2score.service2software.org/login"

FROM_RECRUITING = {
    "fromname": "Service 2 Software Recruiting",
    "fromemail": "recruiting@service2software.org",
    "reply2": "recruiting@service2software.org",
}


def _a(href: str, label: str) -> str:
    return f'<a href="{href}" style="color:#1a73e8;">{label}</a>'


def _btn(href: str, label: str) -> str:
    return (
        f'<a href="{href}" style="display:inline-block;background:{BRAND_LIME};'
        f'color:#111111;font-weight:700;text-decoration:none;padding:12px 18px;'
        f'border-radius:4px;">{label}</a>'
    )


def candidate_post_call_precore_portal() -> str:
    """Send after the candidate completes their initial call with Patrick."""
    fail_table = f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;line-height:1.5;">
  <tr>
    <td style="padding:10px 12px;background:#111111;color:{BRAND_LIME};font-weight:700;width:48%;">Message you may see</td>
    <td style="padding:10px 12px;background:#111111;color:{BRAND_LIME};font-weight:700;">What to do</td>
  </tr>
  <tr>
    <td style="padding:10px 12px;border-bottom:1px solid #eeeeee;vertical-align:top;"><em>We couldn't find your application</em></td>
    <td style="padding:10px 12px;border-bottom:1px solid #eeeeee;vertical-align:top;">Confirm you used the email from your initial call, or contact your recruiter.</td>
  </tr>
  <tr>
    <td style="padding:10px 12px;border-bottom:1px solid #eeeeee;vertical-align:top;"><em>Self-registration is only available right after your initial call</em></td>
    <td style="padding:10px 12px;border-bottom:1px solid #eeeeee;vertical-align:top;">Your Lead status may have already moved forward — ask your recruiter to help you get access.</td>
  </tr>
  <tr>
    <td style="padding:10px 12px;vertical-align:top;"><em>An account already exists</em></td>
    <td style="padding:10px 12px;vertical-align:top;">Go to Sign in or reset your password.</td>
  </tr>
</table>
"""
    return render_email(
        preheader="Create your Pre-Core portal account — next step after your intro call.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Great speaking with you. Your next step is to create your "
            "<strong>Pre-Core Candidate Portal</strong> account so you can track "
            "stages and to-dos through assessment and interviews."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Pre-Core Portal</div>"
            f"<div style=\"margin-bottom:14px;\">{_a(PORTAL_LOGIN, PORTAL_LOGIN)}</div>"
            f"<div>{_btn(PORTAL_LOGIN, 'Create account / log in →')}</div>"
        ),
        section_title="Create your account",
        section_body_html=(
            "1. Open <strong>Create account</strong>.<br/>"
            "2. Enter the <strong>same email address</strong> used for your initial call with S2S.<br/>"
            "3. Choose a password (at least 8 characters).<br/>"
            "4. Click <strong>Create Account</strong>.<br/><br/>"
            "You will land on your Pre-Core dashboard, where you can track stages and to-dos."
        ),
        extra_sections=[
            ("If registration fails", fail_table),
            (
                "Log in",
                "1. Open "
                + _a(PORTAL_LOGIN, PORTAL_LOGIN)
                + ".<br/>"
                "2. Enter your email and password.<br/>"
                "3. Click <strong>Sign In</strong>.<br/><br/>"
                "You will go to your Pre-Core home: "
                + _a(PORTAL_HOME, PORTAL_HOME)
                + ".",
            ),
            (
                "Forgot password",
                "On the login page, click <strong>Forgot password?</strong><br/>"
                "Or go directly to "
                + _a(PORTAL_RESET, PORTAL_RESET)
                + ".<br/><br/>"
                "Follow the steps to reset your password with the email for your account.",
            ),
            (
                "After you’re accepted",
                "Once you are accepted into the program (acceptance letter / Salesforce conversion), "
                "you will use the <strong>S2S Core</strong> portal instead:<br/><br/>"
                "Login: "
                + _a(CORE_LOGIN, CORE_LOGIN)
                + "<br/><br/>"
                "See the separate S2S Core candidate guide for register and login steps.",
            ),
        ],
        callout_html=(
            "<strong>Need help?</strong> Contact your S2S recruiter or program contact "
            "if you cannot register or sign in with the email from your initial call."
        ),
        closing_html="Looking forward to seeing you in the portal.",
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="recruiting@service2software.org",
    )


POST_CALL_TEMPLATES = [
    {
        "key": "candidate-post-call-precore-portal",
        "name": "S2S · Candidate · Post-call Pre-Core portal",
        "subject": "%FIRSTNAME%, create your Pre-Core portal account",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-initial-call-completed",
        "tag": "cand-initial-call-completed",
        "build": candidate_post_call_precore_portal,
        **FROM_RECRUITING,
    },
]
