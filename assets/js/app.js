/* ============================================================
   Service 2 Software — Application Logic
   ============================================================ */

(function () {
  'use strict';

  /* ─── Logo Ticker ──────────────────────────────────────── */
  function initTicker() {
    const track = document.querySelector('.ticker-track');
    if (!track) return;

    // Duplicate items for seamless loop
    const clone = track.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    track.parentNode.appendChild(clone);
  }

  /* ─── Audience Card Hover ──────────────────────────────── */
  function initAudienceCards() {
    // Handled purely by CSS, but make sure images load
    document.querySelectorAll('.audience-card img').forEach(img => {
      img.addEventListener('error', function () {
        this.style.display = 'none';
      });
    });
  }

  /* ─── ROI Calculator ───────────────────────────────────── */
  function initCalculator() {
    const calc = document.getElementById('roi-calculator');
    if (!calc) return;

    // S2S program assumptions
    const ASSUMPTIONS = {
      programCost:       25000,  // TODO: update with real partnership cost
      rampReduction:     1.0,    // fraction of ramp cost eliminated
      retentionBonus:    0.15,   // extra 15% retention vs avg hire
      productivityGain:  0.30    // 30% better year-1 pipeline than avg new hire
    };

    const inputs = {
      reps:          calc.querySelector('#calc-reps'),
      acv:           calc.querySelector('#calc-acv'),
      rampMonths:    calc.querySelector('#calc-ramp'),
      trainingCost:  calc.querySelector('#calc-training')
    };

    const outputs = {
      traditionalCost: calc.querySelector('#out-traditional-cost'),
      s2sCost:         calc.querySelector('#out-s2s-cost'),
      pipelineGain:    calc.querySelector('#out-pipeline'),
      roiMultiple:     calc.querySelector('#out-roi'),
      annualSavings:   calc.querySelector('#out-savings')
    };

    function fmt(n) {
      if (n >= 1000000) return '$' + (n / 1000000).toFixed(1) + 'M';
      if (n >= 1000)    return '$' + Math.round(n / 1000) + 'K';
      return '$' + Math.round(n);
    }

    function calculate() {
      const reps         = parseInt(inputs.reps.value)        || 1;
      const acv          = parseInt(inputs.acv.value)         || 60000;
      const rampMonths   = parseInt(inputs.rampMonths.value)  || 6;
      const trainingCost = parseInt(inputs.trainingCost.value)|| 8000;

      // Traditional hire costs per rep
      const rampCostPerRep     = (rampMonths / 12) * acv * 1.2; // lost pipeline during ramp
      const traditionalPerRep  = rampCostPerRep + trainingCost;
      const totalTraditional   = traditionalPerRep * reps;

      // S2S costs
      const s2sCostTotal = ASSUMPTIONS.programCost * reps;

      // Pipeline gain: S2S reps start producing immediately + retention bonus
      const baseYearPipeline   = acv * 4 * reps; // avg 4 deals/yr
      const pipelineBonus      = baseYearPipeline * ASSUMPTIONS.productivityGain;
      const totalPipelineGain  = pipelineBonus + (rampCostPerRep * reps); // saved ramp cost = recaptured pipeline

      // ROI
      const netBenefit   = totalTraditional - s2sCostTotal + pipelineBonus;
      const roi          = netBenefit / s2sCostTotal;
      const annualSaving = totalTraditional - s2sCostTotal;

      if (outputs.traditionalCost) outputs.traditionalCost.textContent = fmt(totalTraditional);
      if (outputs.s2sCost)         outputs.s2sCost.textContent         = fmt(s2sCostTotal);
      if (outputs.pipelineGain)    outputs.pipelineGain.textContent    = fmt(totalPipelineGain);
      if (outputs.roiMultiple)     outputs.roiMultiple.textContent     = roi.toFixed(1) + 'x';
      if (outputs.annualSavings)   outputs.annualSavings.textContent   = fmt(annualSaving > 0 ? annualSaving : 0);
    }

    Object.values(inputs).forEach(input => {
      if (input) input.addEventListener('input', calculate);
    });

    calculate(); // initial run
  }

  /* ─── Lead Forms ───────────────────────────────────────── */
  function initForms() {
    document.querySelectorAll('.s2s-form').forEach(form => {
      form.addEventListener('submit', function (e) {
        e.preventDefault();

        const data      = Object.fromEntries(new FormData(this));
        const formType  = this.dataset.form;
        const submitBtn = this.querySelector('[type="submit"]');

        // Disable button during submission
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Submitting…';
        }

        // TODO: Replace with real ActiveCampaign form endpoint
        const endpoint = this.dataset.action || '#';

        if (endpoint === '#') {
          // Demo: show thank-you state
          showThankYou(form, formType);
          return;
        }

        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
          .then(r => r.ok ? r.json() : Promise.reject(r))
          .then(() => showThankYou(form, formType))
          .catch(() => {
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.textContent = 'Try Again';
            }
          });
      });
    });
  }

  function showThankYou(form, formType) {
    const thankYou = form.nextElementSibling;
    if (thankYou && thankYou.classList.contains('form-thankyou')) {
      form.style.display = 'none';
      thankYou.style.display = 'block';
    }
  }

  /* ─── Animate on scroll (simple fade-in) ──────────────── */
  function initAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.animate-in').forEach(el => observer.observe(el));
  }

  /* ─── Testimonial.to resize ────────────────────────────── */
  function initTestimonial() {
    window.addEventListener('message', function (e) {
      if (e.data && e.data.type === 'testimonialto-resize') {
        const iframe = document.querySelector('#testimonialto-0f9fe1c1-b3b4-4f10-9ce5-8b3b07b8994a');
        if (iframe) iframe.height = e.data.height + 'px';
      }
    });
  }

  /* ─── Init ─────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initTicker();
    initAudienceCards();
    initCalculator();
    initForms();
    initAnimations();
    initTestimonial();
  });

})();
