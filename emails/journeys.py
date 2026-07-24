"""ETS/role × booking journey emails (Brooke layout). Copy for Dave to refine."""

from __future__ import annotations

from layout import BRAND_LIME, render_email

CAL_CANDIDATE = (
    "https://calendly.com/patrick-service2software/"
    "initial-call-with-service-2-software"
)
CAL_PARTNER = "https://calendly.com/davidhester/s2s-hiring"
SITE = "https://d2by6tunn6pa78.cloudfront.net"
SITE_MILITARY = f"{SITE}/?page=military&section=mil-cal"
SITE_COMPANIES = f"{SITE}/?page=companies&section=co-cal"


def link(href: str, label: str) -> str:
    return f'<a href="{href}" style="color:#1a73e8;">{label}</a>'

# Warmed sending addresses (from Dave/Allie go-live prep)
FROM_RECRUITING = {
    "fromname": "Service 2 Software Recruiting",
    "fromemail": "recruiting@service2software.org",
    "reply2": "recruiting@service2software.org",
}
FROM_DAVE = {
    "fromname": "David Hester",
    "fromemail": "dave@service2software.org",
    "reply2": "dave@service2software.org",
}
FROM_DAVID = {
    "fromname": "David Hester",
    "fromemail": "david@service2software.org",
    "reply2": "david@service2software.org",
}


def _cta_btn(href: str, label: str) -> str:
    return (
        f'<a href="{href}" style="display:inline-block;background:{BRAND_LIME};'
        f'color:#111111;font-weight:700;text-decoration:none;padding:12px 18px;'
        f'border-radius:4px;">{label}</a>'
    )


def cand_separated_onedone() -> str:
    return render_email(
        preheader="Thanks for applying — next steps by email (no call needed).",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Thanks for applying to Service 2 Software. Because you marked "
            "<strong>already separated</strong>, we won't send a Calendly link — "
            "this path is email-first."
        ),
        section_title="What happens next",
        section_body_html=(
            "Our recruiting team will review your background and reply with the "
            "right next step for veterans who have already transitioned. "
            "No intro call is required to get started."
        ),
        callout_html=(
            "<strong>One-and-done for now.</strong> Watch your inbox from "
            "recruiting@service2software.org — reply anytime with questions."
        ),
        closing_html=f"Meanwhile you can {link(SITE_MILITARY, 'review the military pathway')}.",
        signoff_name="Service 2 Software Recruiting",
        signoff_title="recruiting@service2software.org",
        signoff_email="recruiting@service2software.org",
    )


def cand_nobook(window_label: str, urgency: str) -> str:
    return render_email(
        preheader=f"You applied ({window_label}) — lock your intro call.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            f"Thanks for applying. You selected <strong>{window_label}</strong> "
            f"until separation. {urgency}"
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Next step</div>"
            f"<div>{_cta_btn(CAL_CANDIDATE, 'Book my intro call →')}</div>"
        ),
        section_title="Why book now",
        section_body_html=(
            "Your intro call with Patrick is a 20-minute two-way fit check — "
            "not an interview. Bring a rough ETS/EAS date and any questions."
        ),
        callout_html=(
            "<strong>This costs you nothing.</strong> SkillBridge keeps you on "
            "military pay and benefits while you train."
        ),
        closing_html="Talk soon.",
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="recruiting@service2software.org",
    )


def cand_booked(window_label: str, prep: str) -> str:
    return render_email(
        preheader=f"You're booked ({window_label}) — here's how to prep.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            f"You're booked. With <strong>{window_label}</strong> on the clock, "
            f"{prep}"
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div><strong>With:</strong> Patrick Gilroy — Recruiting Manager</div>"
        ),
        section_title="Bring this",
        section_body_html=(
            "Rough ETS/EAS date, branch/MOS context, and any questions about "
            "SkillBridge tech-sales internships."
        ),
        closing_html=f"Need to move it? {link(CAL_CANDIDATE, 'Reschedule here')}.",
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="recruiting@service2software.org",
    )


def partner_nobook(role_label: str, angle: str) -> str:
    return render_email(
        preheader=f"Hiring for {role_label}? Let's map SkillBridge seats.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            f"Thanks for reaching out. You noted interest in "
            f"<strong>{role_label}</strong>. {angle}"
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Next step</div>"
            f"<div>{_cta_btn(CAL_PARTNER, 'Schedule hiring call →')}</div>"
        ),
        section_title="What we'll cover",
        section_body_html=(
            "Roles, ramp expectations, SkillBridge hosting basics, and how S2S "
            "trains and matches veteran talent."
        ),
        closing_html=f"Or {link(SITE_COMPANIES, 'see how partner hiring works')} first.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def partner_booked(role_label: str, angle: str) -> str:
    return render_email(
        preheader=f"You're booked — hiring conversation ({role_label}).",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            f"You're booked. We'll focus on <strong>{role_label}</strong> seats. {angle}"
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div><strong>With:</strong> David Hester</div>"
        ),
        closing_html=f"Need a new time? {link(CAL_PARTNER, 'Reschedule here')}.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


# Concrete builders
def cand_612_nobook() -> str:
    return cand_nobook(
        "6–12 months (or more than 12 months)",
        "You have runway — booking now still moves approval fastest.",
    )


def cand_36_nobook() -> str:
    return cand_nobook(
        "3–6 months",
        "Your window is tightening — candidates who book now clear SkillBridge paperwork sooner.",
    )


def cand_lt3_nobook() -> str:
    return cand_nobook(
        "less than 3 months",
        "Timeline is tight. Book your intro call as soon as you can so we can assess fit quickly.",
    )


def cand_612_booked() -> str:
    return cand_booked(
        "6–12 months (or more than 12 months)",
        "we'll map a deliberate SkillBridge timeline on the call.",
    )


def cand_36_booked() -> str:
    return cand_booked(
        "3–6 months",
        "we'll prioritize approval timing and partner match options.",
    )


def cand_lt3_booked() -> str:
    return cand_booked(
        "less than 3 months",
        "we'll move fast on fit and feasibility for your ETS.",
    )


def partner_sdr_nobook() -> str:
    return partner_nobook(
        "SDR / BDR and/or Account Executive",
        "Those are our strongest SkillBridge placement lanes.",
    )


def partner_cs_nobook() -> str:
    return partner_nobook(
        "Customer Success",
        "We can walk through how CS seats work inside a SkillBridge internship.",
    )


def partner_other_nobook() -> str:
    return partner_nobook(
        "Multiple / Other roles",
        "We'll clarify which seats are a fit for S2S interns.",
    )


def partner_sdr_booked() -> str:
    return partner_booked(
        "SDR / BDR / AE",
        "Come with open headcount and target start timing if you have it.",
    )


def partner_cs_booked() -> str:
    return partner_booked(
        "Customer Success",
        "Come with team structure and ramp expectations if you have them.",
    )


def partner_other_booked() -> str:
    return partner_booked(
        "Other / multiple roles",
        "We'll sort which roles are SkillBridge-ready.",
    )


JOURNEY_TEMPLATES = [
    {
        "key": "cand-journey-separated-onedone",
        "name": "S2S · Candidate · Separated one-and-done",
        "subject": "%FIRSTNAME%, thanks for applying — next steps by email",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-separated-onedone",
        "tag": "cand-journey-separated-onedone",
        "build": cand_separated_onedone,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-6-12-nobook",
        "name": "S2S · Candidate · 6-12mo no book",
        "subject": "%FIRSTNAME%, book your intro call (6–12 months out)",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-6-12-nobook",
        "tag": "cand-journey-6-12-nobook",
        "build": cand_612_nobook,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-3-6-nobook",
        "name": "S2S · Candidate · 3-6mo no book",
        "subject": "%FIRSTNAME%, your 3–6 month window — book intro call",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-3-6-nobook",
        "tag": "cand-journey-3-6-nobook",
        "build": cand_36_nobook,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-lt3-nobook",
        "name": "S2S · Candidate · <3mo no book",
        "subject": "%FIRSTNAME%, timeline is tight — book your intro call",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-lt3-nobook",
        "tag": "cand-journey-lt3-nobook",
        "build": cand_lt3_nobook,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-6-12-booked",
        "name": "S2S · Candidate · 6-12mo booked",
        "subject": "%FIRSTNAME%, you're booked — prep for your intro call",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-6-12-booked",
        "tag": "cand-journey-6-12-booked",
        "build": cand_612_booked,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-3-6-booked",
        "name": "S2S · Candidate · 3-6mo booked",
        "subject": "%FIRSTNAME%, you're booked — let's move on timing",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-3-6-booked",
        "tag": "cand-journey-3-6-booked",
        "build": cand_36_booked,
        **FROM_RECRUITING,
    },
    {
        "key": "cand-journey-lt3-booked",
        "name": "S2S · Candidate · <3mo booked",
        "subject": "%FIRSTNAME%, you're booked — fast-track prep",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "tag:cand-journey-lt3-booked",
        "tag": "cand-journey-lt3-booked",
        "build": cand_lt3_booked,
        **FROM_RECRUITING,
    },
    {
        "key": "partner-journey-sdr-ae-nobook",
        "name": "S2S · Partner · SDR/AE no book",
        "subject": "%FIRSTNAME%, schedule a hiring call (SDR/AE)",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-sdr-ae-nobook",
        "tag": "partner-journey-sdr-ae-nobook",
        "build": partner_sdr_nobook,
        **FROM_DAVID,
    },
    {
        "key": "partner-journey-cs-nobook",
        "name": "S2S · Partner · CS no book",
        "subject": "%FIRSTNAME%, schedule a hiring call (Customer Success)",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-cs-nobook",
        "tag": "partner-journey-cs-nobook",
        "build": partner_cs_nobook,
        **FROM_DAVID,
    },
    {
        "key": "partner-journey-other-nobook",
        "name": "S2S · Partner · Other no book",
        "subject": "%FIRSTNAME%, schedule a hiring call",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-other-nobook",
        "tag": "partner-journey-other-nobook",
        "build": partner_other_nobook,
        **FROM_DAVID,
    },
    {
        "key": "partner-journey-sdr-ae-booked",
        "name": "S2S · Partner · SDR/AE booked",
        "subject": "%FIRSTNAME%, you're booked — SDR/AE hiring call",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-sdr-ae-booked",
        "tag": "partner-journey-sdr-ae-booked",
        "build": partner_sdr_booked,
        **FROM_DAVID,
    },
    {
        "key": "partner-journey-cs-booked",
        "name": "S2S · Partner · CS booked",
        "subject": "%FIRSTNAME%, you're booked — CS hiring call",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-cs-booked",
        "tag": "partner-journey-cs-booked",
        "build": partner_cs_booked,
        **FROM_DAVID,
    },
    {
        "key": "partner-journey-other-booked",
        "name": "S2S · Partner · Other booked",
        "subject": "%FIRSTNAME%, you're booked — hiring call",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "tag:partner-journey-other-booked",
        "tag": "partner-journey-other-booked",
        "build": partner_other_booked,
        **FROM_DAVID,
    },
]
