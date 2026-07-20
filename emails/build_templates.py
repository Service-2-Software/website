#!/usr/bin/env python3
"""Build Brooke-style HTML email templates for ActiveCampaign campaigns."""

from __future__ import annotations

import json
from pathlib import Path

from layout import BRAND_LIME, render_email

OUT = Path(__file__).resolve().parent / "templates"
CAL_CANDIDATE = (
    "https://calendly.com/patrick-service2software/"
    "initial-call-with-service-2-software"
)
CAL_PARTNER = "https://calendly.com/davidhester/s2s-hiring"
# New marketing site (custom domain still on Kajabi — do not use www.service2software.org yet)
SITE = "https://d2by6tunn6pa78.cloudfront.net"
SITE_MILITARY = f"{SITE}/?page=military&section=mil-cal"
SITE_COMPANIES = f"{SITE}/?page=companies&section=co-cal"
SITE_ROI = f"{SITE}/?page=companies&section=roi-calc"


def link(href: str, label: str) -> str:
    return f'<a href="{href}" style="color:#1a73e8;">{label}</a>'


def candidate_booking_confirmation() -> str:
    return render_email(
        preheader="Your initial call with Patrick is confirmed.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "You're booked. Your <strong>initial call</strong> with Patrick Gilroy, "
            "our Recruiting Manager, is confirmed — this is a two-way fit check, "
            "not an interview. Come as you are."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div style=\"margin-bottom:10px;\"><strong>With:</strong> "
            "Patrick Gilroy — Recruiting Manager</div>"
            "<div><strong>Length:</strong> 20 minutes</div>"
        ),
        section_title="What we'll cover",
        section_body_html=(
            "Your separation timeline, what a fully funded SkillBridge internship "
            "in tech sales actually looks like, and whether S2S is the right path "
            "for you. Bring your rough ETS date and any questions — that's it."
        ),
        callout_html=(
            "<strong>This costs you nothing.</strong> During SkillBridge you stay "
            "on full military pay and benefits while you train with a real tech "
            "company. Our program is a DoW-approved 501(c)(3) — no fees, ever."
        ),
        closing_html=(
            "Can't make the time anymore? No problem — "
            f"{link(CAL_CANDIDATE, 'grab a new slot here')} instead of missing it. "
            "See you soon."
        ),
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="patrick@service2software.org",
    )


def candidate_book_nudge() -> str:
    return render_email(
        preheader="Lock in your 20-minute intro call with Patrick.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Thanks for applying — we received your info. The fastest way through "
            "approval is to lock your <strong>intro call</strong> with Patrick now. "
            "It's a 20-minute two-way fit check, not an interview."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Next step</div>"
            "<div style=\"margin-bottom:12px;\">Book a time that works for you:</div>"
            f'<div><a href="{CAL_CANDIDATE}" style="display:inline-block;background:'
            f'{BRAND_LIME};color:#111111;font-weight:700;text-decoration:none;'
            'padding:12px 18px;border-radius:4px;">Book my intro call →</a></div>'
        ),
        section_title="Why book now",
        section_body_html=(
            "Candidates who schedule immediately move through SkillBridge approval "
            "fastest. Bring a rough ETS/EAS date — that's enough for the first call."
        ),
        callout_html=(
            "<strong>Still on the fence?</strong> This call is low-pressure. "
            "We'll tell you honestly if S2S is the right path."
        ),
        closing_html="Talk soon — Patrick and the recruiting team are ready when you are.",
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="patrick@service2software.org",
    )


def candidate_reminder() -> str:
    return render_email(
        preheader="Reminder: your S2S intro call is coming up.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Quick reminder — your intro call with Patrick is coming up. "
            "No prep deck required. Come with your ETS window and any questions."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div><strong>With:</strong> Patrick Gilroy — Recruiting Manager</div>"
        ),
        closing_html=(
            f"Need to move it? {link(CAL_CANDIDATE, 'Reschedule here')}."
        ),
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="patrick@service2software.org",
    )


def candidate_nurture_skillbridge() -> str:
    return render_email(
        preheader="What a funded SkillBridge tech-sales internship actually looks like.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "SkillBridge isn't a class you sit through — it's a 3–4 month proof of "
            "performance inside a real tech company while you stay on military pay."
        ),
        section_title="What to expect",
        section_body_html=(
            "You'll train with intention (sales craft + AI fluency), get matched to "
            "a hiring partner on purpose, and build real pipeline before ETS. "
            "Most offers land 30+ days before separation."
        ),
        callout_html=(
            f"<strong>Ready to talk it through?</strong> "
            f'{link(CAL_CANDIDATE, "Book your intro call")} if you haven\'t already.'
        ),
        closing_html="We're here when you're ready to take the next step.",
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="patrick@service2software.org",
    )


def partner_booking_confirmation() -> str:
    return render_email(
        preheader="Your S2S hiring call with David is confirmed.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "You're booked. Your <strong>hiring conversation</strong> with "
            "David Hester is confirmed — we'll map your roles, timeline, and "
            "whether SkillBridge interns are the right force-multiplier for your team."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div style=\"margin-bottom:10px;\"><strong>With:</strong> "
            "David Hester — Service 2 Software</div>"
            "<div><strong>Length:</strong> ~30 minutes</div>"
        ),
        section_title="What we'll cover",
        section_body_html=(
            "Open roles, ramp expectations, compliance basics for SkillBridge "
            "hosting, and how S2S sources, trains, and matches veteran talent "
            "to tech sales seats."
        ),
        callout_html=(
            "<strong>No placement fees for candidates — ever.</strong> "
            "Partners invest in a structured internship that produces pipeline "
            "before a full-time offer."
        ),
        closing_html=(
            "Need a different time? "
            f"{link(CAL_PARTNER, 'Grab a new slot here')}. Looking forward to it."
        ),
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def partner_book_nudge() -> str:
    return render_email(
        preheader="Pick a time to map your SkillBridge hiring needs.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Thanks for reaching out about hiring military talent through S2S. "
            "Next step is a short call so we can understand roles, timing, and fit."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Next step</div>"
            f'<div><a href="{CAL_PARTNER}" style="display:inline-block;background:'
            f'{BRAND_LIME};color:#111111;font-weight:700;text-decoration:none;'
            'padding:12px 18px;border-radius:4px;">Schedule hiring call →</a></div>'
        ),
        section_title="Why companies partner with S2S",
        section_body_html=(
            "Pre-trained veteran talent, a 3–4 month proof-of-performance internship, "
            "and a recruiting partner that cares about retention — not just placement."
        ),
        closing_html="Reply to this email if you have questions before we meet.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def partner_reminder() -> str:
    return render_email(
        preheader="Reminder: your S2S hiring call is coming up.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Looking forward to speaking soon about your hiring needs and how "
            "SkillBridge interns can fill seats with purpose."
        ),
        details_box_html=(
            f'<div style="color:{BRAND_LIME};font-size:12px;font-weight:700;'
            'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">'
            "Call Details</div>"
            '<div style="margin-bottom:10px;"><strong>Date &amp; time:</strong> '
            f'<span style="color:{BRAND_LIME};">%INITIAL_CALL_DATETIME%</span></div>'
            "<div><strong>With:</strong> David Hester</div>"
        ),
        closing_html=f"Need to reschedule? {link(CAL_PARTNER, 'Pick a new time')}.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def partner_nurture_roi() -> str:
    return render_email(
        preheader="How S2S SkillBridge hiring actually works for partners.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "A quick look at what partnering with Service 2 Software looks like "
            "when you're hiring for tech sales seats."
        ),
        section_title="The model",
        section_body_html=(
            "We train veterans for modern sales (including AI fluency), match them "
            "to your culture and role, and place them into a structured internship "
            "where they build real pipeline before a full-time decision."
        ),
        callout_html=(
            f"<strong>Want numbers for your team?</strong> "
            f"{link(SITE_ROI, 'Use the ROI calculator on our site')} "
            f"or {link(CAL_PARTNER, 'book a hiring call')}."
        ),
        closing_html="Happy to walk through compliance, timeline, and open roles anytime.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def candidate_what_we_offer() -> str:
    return render_email(
        preheader="A fully funded SkillBridge internship in tech sales.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "If you're separating soon, here's what Service 2 Software offers "
            "service members transitioning into tech sales."
        ),
        section_title="For candidates",
        section_body_html=(
            "A fully funded SkillBridge internship in tech sales while you stay "
            "on military pay and benefits. You'll train with intention, get matched "
            "to a hiring partner on purpose, and build real pipeline before ETS."
        ),
        callout_html=(
            f'<a href="{CAL_CANDIDATE}" style="display:inline-block;background:'
            f'{BRAND_LIME};color:#111111;font-weight:700;text-decoration:none;'
            'padding:12px 18px;border-radius:4px;">Apply / book intro call →</a>'
        ),
        closing_html=(
            f"Prefer to browse first? {link(SITE_MILITARY, 'See the military pathway')}."
        ),
        signoff_name="Patrick Gilroy",
        signoff_title="Recruiting Manager, Service2Software",
        signoff_email="patrick@service2software.org",
    )


def partner_what_we_offer() -> str:
    return render_email(
        preheader="Pre-trained veteran talent for your sales team.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "If you're hiring SDRs or building a sales team, here's what "
            "partnering with Service 2 Software looks like."
        ),
        section_title="For hiring partners",
        section_body_html=(
            "Pre-trained veteran talent, a structured SkillBridge internship, "
            "and a recruiting process built for retention — not just placement. "
            "Interns build real pipeline before you make a full-time offer."
        ),
        callout_html=(
            f'<a href="{CAL_PARTNER}" style="display:inline-block;background:'
            f'{BRAND_LIME};color:#111111;font-weight:700;text-decoration:none;'
            'padding:12px 18px;border-radius:4px;">Talk to us about hiring →</a>'
        ),
        closing_html=(
            f"Want the numbers first? {link(SITE_ROI, 'Open the ROI calculator')} "
            f"or {link(SITE_COMPANIES, 'see how partner hiring works')}."
        ),
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


def newsletter_welcome() -> str:
    """Brand-only welcome for the undifferentiated newsletter list (no dual CTAs)."""
    return render_email(
        preheader="Welcome to Service 2 Software — Hire With Purpose.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Welcome. You're on the list for updates on SkillBridge pathways "
            "into tech sales — from Service 2 Software, a DoW-approved 501(c)(3)."
        ),
        section_title="Hire With Purpose",
        section_body_html=(
            "We train veterans for modern tech sales and match them with companies "
            "ready to hire with purpose. No fees to candidates — ever."
        ),
        callout_html=(
            f"Explore the site: {link(SITE, 'Service 2 Software')}."
        ),
        closing_html="Glad you're here — more from us soon.",
        signoff_name="Allie Medawar",
        signoff_title="Service 2 Software",
        signoff_email="allie@service2software.org",
    )


def newsletter_story() -> str:
    return render_email(
        preheader="Why Service 2 Software exists.",
        greeting_html="Hi %FIRSTNAME%,",
        body_html=(
            "Military talent shouldn't have to guess their way into tech. "
            "We built S2S so transitions into sales careers are structured, funded, "
            "and matched on purpose."
        ),
        section_title="Our mission",
        section_body_html=(
            "Train with intention. Match with purpose. Focus on results — "
            "so veterans earn full-time offers before ETS, and companies hire people "
            "who've already proven they can sell."
        ),
        closing_html=f"Explore more at {link(SITE, 'our website')}.",
        signoff_name="David Hester",
        signoff_title="Service 2 Software",
        signoff_email="david@service2software.org",
    )


TEMPLATES = [
    {
        "key": "candidate-booking-confirmation",
        "name": "S2S · Candidate · Booking confirmation",
        "subject": "%FIRSTNAME%, you're booked — intro call with Patrick",
        "fromname": "Patrick Gilroy",
        "fromemail": "patrick@service2software.org",
        "reply2": "patrick@service2software.org",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "calendly-candidate-booked",
        "build": candidate_booking_confirmation,
    },
    {
        "key": "candidate-book-nudge",
        "name": "S2S · Candidate · Book your intro call",
        "subject": "%FIRSTNAME%, next step: book your 20-minute intro call",
        "fromname": "Patrick Gilroy",
        "fromemail": "patrick@service2software.org",
        "reply2": "patrick@service2software.org",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "form-candidate",
        "build": candidate_book_nudge,
    },
    {
        "key": "candidate-reminder",
        "name": "S2S · Candidate · Call reminder",
        "subject": "Reminder: your S2S intro call is coming up",
        "fromname": "Patrick Gilroy",
        "fromemail": "patrick@service2software.org",
        "reply2": "patrick@service2software.org",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "calendly-candidate-reminder",
        "build": candidate_reminder,
    },
    {
        "key": "candidate-nurture-skillbridge",
        "name": "S2S · Candidate · What SkillBridge looks like",
        "subject": "What a funded SkillBridge internship actually looks like",
        "fromname": "Patrick Gilroy",
        "fromemail": "patrick@service2software.org",
        "reply2": "patrick@service2software.org",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "candidate-nurture-d2",
        "build": candidate_nurture_skillbridge,
    },
    {
        "key": "candidate-what-we-offer",
        "name": "S2S · Candidate · What we offer",
        "subject": "%FIRSTNAME%, here's what S2S offers transitioning service members",
        "fromname": "Patrick Gilroy",
        "fromemail": "patrick@service2software.org",
        "reply2": "patrick@service2software.org",
        "list": "website-candidates",
        "journey": "candidate",
        "trigger": "candidate-nurture-offer",
        "build": candidate_what_we_offer,
    },
    {
        "key": "partner-booking-confirmation",
        "name": "S2S · Partner · Booking confirmation",
        "subject": "%FIRSTNAME%, you're booked — hiring call with David",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "calendly-partner-booked",
        "build": partner_booking_confirmation,
    },
    {
        "key": "partner-book-nudge",
        "name": "S2S · Partner · Schedule hiring call",
        "subject": "%FIRSTNAME%, let's map your SkillBridge hiring needs",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "form-partner",
        "build": partner_book_nudge,
    },
    {
        "key": "partner-reminder",
        "name": "S2S · Partner · Call reminder",
        "subject": "Reminder: your S2S hiring call is coming up",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "calendly-partner-reminder",
        "build": partner_reminder,
    },
    {
        "key": "partner-nurture-roi",
        "name": "S2S · Partner · How hiring works",
        "subject": "How S2S SkillBridge hiring works for partners",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "partner-nurture-d2",
        "build": partner_nurture_roi,
    },
    {
        "key": "partner-what-we-offer",
        "name": "S2S · Partner · What we offer",
        "subject": "%FIRSTNAME%, here's what S2S offers hiring partners",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "website-partners",
        "journey": "partner",
        "trigger": "partner-nurture-offer",
        "build": partner_what_we_offer,
    },
    {
        "key": "newsletter-welcome",
        "name": "S2S · Newsletter · Welcome",
        "subject": "Welcome to Service 2 Software",
        "fromname": "Allie Medawar",
        "fromemail": "allie@service2software.org",
        "reply2": "allie@service2software.org",
        "list": "home-page-group",
        "journey": "newsletter",
        "trigger": "form-newsletter",
        "build": newsletter_welcome,
    },
    {
        "key": "newsletter-story",
        "name": "S2S · Newsletter · Story & mission",
        "subject": "Why Service 2 Software exists",
        "fromname": "David Hester",
        "fromemail": "david@service2software.org",
        "reply2": "david@service2software.org",
        "list": "home-page-group",
        "journey": "newsletter",
        "trigger": "newsletter-d3",
        "build": newsletter_story,
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in TEMPLATES:
        html = item["build"]()
        path = OUT / f"{item['key']}.html"
        path.write_text(html, encoding="utf-8")
        meta = {k: v for k, v in item.items() if k != "build"}
        meta["file"] = path.name
        manifest.append(meta)
        print("wrote", path.name, "bytes", len(html))
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("manifest:", OUT / "manifest.json")


if __name__ == "__main__":
    main()
