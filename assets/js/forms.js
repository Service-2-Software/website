/* Lead form flow: short native form -> on-submit reveal a "thank you"
   step with the Calendly embed, mirroring B2B SaaS speed-to-lead patterns.
   The data POST to ActiveCampaign is stubbed until AC form IDs are provided. */
const CALENDLY = {
  // TODO: replace military with Patrick's intro-call Calendly URL when provided
  military: 'https://calendly.com/davidhester/s2s-hiring',
  companies: 'https://calendly.com/davidhester/s2s-hiring',
};

function submitLead(form) {
  const audience = form.dataset.audience || 'companies';
  const thankyou = form.parentElement.querySelector('.form-thankyou');

  // TODO: POST to ActiveCampaign once "Military Application" / "Partner Inquiry"
  // form IDs exist. AC then handles the 2-hour email + Salesforce + Slack.
  const payload = Object.fromEntries(new FormData(form).entries());
  console.log('[lead captured]', audience, payload);

  if (thankyou) {
    form.style.display = 'none';
    const slot = thankyou.querySelector('.calendly-slot');
    if (slot && !slot.dataset.loaded) {
      slot.innerHTML =
        '<iframe src="' + CALENDLY[audience] + '" title="Book a call" ' +
        'style="width:100%;min-height:640px;border:0"></iframe>';
      slot.dataset.loaded = '1';
    }
    thankyou.hidden = false;
    thankyou.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form.lead-form').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitLead(form);
    });
  });
  // Newsletter (placeholder until AC list is wired)
  document.querySelectorAll('form.newsletter-form').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const msg = form.querySelector('.nl-msg');
      if (msg) { msg.hidden = false; }
      form.querySelector('input[type=email]').value = '';
    });
  });
});
