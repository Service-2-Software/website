"""Shared Brooke-style S2S email layout (#CEFF00 accent, black header).

The wordmark uses a fixed 480px width (not width:100%) inside the same
32px gutters as the body. Gmail expands width:100% images to the message
pane, which made the header wider than the 600px content column. The PNG
is 639×46, so 480px keeps it readable while lining up with the CTA.
"""

BRAND_LIME = "#CEFF00"
BRAND_BLACK = "#111111"
BRAND_MUTED = "#666666"
BRAND_SOFT = "#F4FBE3"
BRAND_WORDMARK = (
    "https://service2software.activehosted.com/content/pkjoam/2026/07/27/"
    "94ef5e12-7838-4f52-9808-7f50811e72eb.png"
)


def render_email(
    *,
    preheader: str,
    greeting_html: str,
    body_html: str,
    details_box_html: str | None = None,
    section_title: str | None = None,
    section_body_html: str | None = None,
    extra_sections: list[tuple[str, str]] | None = None,
    callout_html: str | None = None,
    closing_html: str,
    signoff_name: str,
    signoff_title: str,
    signoff_email: str,
) -> str:
    details = ""
    if details_box_html:
        details = f"""
              <tr>
                <td style="padding:0 0 24px 0;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BRAND_BLACK};border-radius:8px;">
                    <tr>
                      <td style="padding:22px 24px;font-family:Arial,Helvetica,sans-serif;color:#ffffff;font-size:15px;line-height:1.6;">
                        {details_box_html}
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>"""

    def _section_row(title: str, body: str) -> str:
        return f"""
              <tr>
                <td style="padding:18px 0 8px 0;font-family:Arial,Helvetica,sans-serif;">
                  <div style="font-size:20px;font-weight:700;color:{BRAND_BLACK};margin:0 0 6px 0;">{title}</div>
                  <div style="width:48px;height:3px;background:{BRAND_LIME};margin:0 0 14px 0;"></div>
                  <div style="font-size:15px;line-height:1.7;color:{BRAND_BLACK};">{body}</div>
                </td>
              </tr>"""

    section = ""
    if section_title and section_body_html:
        section = _section_row(section_title, section_body_html)

    extras = ""
    if extra_sections:
        extras = "".join(_section_row(t, b) for t, b in extra_sections)

    callout = ""
    if callout_html:
        callout = f"""
              <tr>
                <td style="padding:20px 0 8px 0;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BRAND_SOFT};border-left:4px solid {BRAND_LIME};">
                    <tr>
                      <td style="padding:16px 18px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.65;color:{BRAND_BLACK};">
                        {callout_html}
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>"""

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Service 2 Software</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">
          <tr>
            <td style="padding:0 32px;background:#ffffff;font-family:Arial,Helvetica,sans-serif;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;background:{BRAND_BLACK};">
                <tr>
                  <td style="padding:20px 24px 16px 24px;">
                    <img src="{BRAND_WORDMARK}" width="480" alt="SERVICE 2 SOFTWARE" style="display:block;width:480px;max-width:480px;height:auto;border:0;outline:none;text-decoration:none;" />
                    <div style="margin-top:8px;font-size:11px;letter-spacing:0.18em;color:rgba(255,255,255,0.75);text-transform:uppercase;">Veteran Talent · SkillBridge Careers</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:0 32px;background:#ffffff;font-size:0;line-height:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;">
                <tr>
                  <td style="height:4px;background:{BRAND_LIME};font-size:0;line-height:0;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 32px 40px 32px;font-family:Arial,Helvetica,sans-serif;color:{BRAND_BLACK};">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:0 0 18px 0;font-size:16px;line-height:1.7;">
                    {greeting_html}
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 0 22px 0;font-size:16px;line-height:1.7;">
                    {body_html}
                  </td>
                </tr>
                {details}
                {section}
                {extras}
                {callout}
                <tr>
                  <td style="padding:22px 0 0 0;font-size:15px;line-height:1.7;color:{BRAND_BLACK};">
                    {closing_html}
                  </td>
                </tr>
                <tr>
                  <td style="padding:28px 0 0 0;font-family:Arial,Helvetica,sans-serif;">
                    <div style="font-size:16px;font-weight:700;color:{BRAND_BLACK};">{signoff_name}</div>
                    <div style="font-size:14px;color:{BRAND_MUTED};margin-top:4px;">{signoff_title}</div>
                    <div style="margin-top:8px;"><a href="mailto:{signoff_email}" style="color:#1a73e8;font-size:14px;">{signoff_email}</a></div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:18px 32px 28px 32px;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:{BRAND_MUTED};border-top:1px solid #eeeeee;">
              Service 2 Software · DoW-approved SkillBridge · <a href="%UNSUBSCRIBELINK%" style="color:{BRAND_MUTED};">Unsubscribe</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
