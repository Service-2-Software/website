/* S2S ROI Calculator
   -------------------------------------------------------------
   Transparent, illustrative model. Recomputes live on every input.
   NOTE: PROGRAM_COST is a placeholder ($25K/rep) pending the real
   annual partnership number — swap it and the multiples become honest. */
const S2S_ASSUMPTIONS = {
  PROGRAM_COST: 25000,        // TODO: real annual cost per S2S rep
  RECRUITER_FEE: 22000,       // typical agency fee for a comparable hire
  RAMP_BURN: 38000,           // salary paid during a slower traditional ramp
};

function fmt(n) {
  return '$' + Math.round(n).toLocaleString('en-US');
}

function calcROI() {
  const get = (id, d) => {
    const el = document.getElementById(id);
    const v = el ? parseFloat(el.value) : NaN;
    return isNaN(v) ? d : v;
  };
  const reps = Math.max(1, get('roi-reps', 2));
  const acv = Math.max(0, get('roi-acv', 25000));
  const deals = Math.max(0, get('roi-deals', 10));
  const margin = Math.min(100, Math.max(0, get('roi-margin', 60))) / 100;

  const annualRevenue = reps * acv * deals;
  const grossProfit = annualRevenue * margin;
  const s2sCost = reps * S2S_ASSUMPTIONS.PROGRAM_COST;
  const traditionalCost = reps * (S2S_ASSUMPTIONS.RECRUITER_FEE + S2S_ASSUMPTIONS.RAMP_BURN);
  const savings = Math.max(0, traditionalCost - s2sCost);
  const combinedBenefit = grossProfit + savings;
  const roi = s2sCost > 0 ? combinedBenefit / s2sCost : 0;

  const out = {
    'roi-out-revenue': fmt(annualRevenue),
    'roi-out-profit': fmt(grossProfit),
    'roi-out-savings': fmt(savings),
    'roi-out-cost': fmt(s2sCost),
    'roi-out-multiple': roi.toFixed(1) + 'x',
  };
  Object.entries(out).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  });
}

function initROI() {
  if (!document.getElementById('roi-reps')) return;
  ['roi-reps', 'roi-acv', 'roi-deals', 'roi-margin'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', calcROI);
  });
  calcROI();
}

document.addEventListener('DOMContentLoaded', initROI);
