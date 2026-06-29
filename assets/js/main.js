/* =====================================================================
   Service 2 Software — shared site chrome + interactions
   Nav + footer are injected here so there's a single source of truth
   across every page in the repo.
   ===================================================================== */
(function () {
  "use strict";

  /* ---- custom icon set (hand-drawn glyphs, S2S personality) ---------- */
  var ICONS = {
    program: '<svg viewBox="0 0 24 24"><path d="M4 9l8-4 8 4-8 4-8-4z"/><path d="M4 13l8 4 8-4"/><path d="M4 17l8 4 8-4"/></svg>',         // rank chevrons
    impact:  '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 12l6-3"/><circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/></svg>', // radar
    why:     '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 1v4M12 19v4M1 12h4M19 12h4"/><circle cx="12" cy="12" r="2.4"/></svg>', // crosshair
    founder: '<svg viewBox="0 0 24 24"><path d="M12 2l2.3 6.8H21l-5.4 4 2 6.8L12 15.6 6.4 19.6l2-6.8L3 8.8h6.7z"/></svg>', // north star
    story:   '<svg viewBox="0 0 24 24"><path d="M6 21V4M6 4h11l-2 3 2 3H6"/></svg>', // flag
    results: '<svg viewBox="0 0 24 24"><path d="M4 20V12M10 20V7M16 20V14M22 20V4"/></svg>', // rising bars
    how:     '<svg viewBox="0 0 24 24"><circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M7.3 7.2L10.7 16M16.7 7.2L13.3 16"/></svg>', // flow nodes
    roi:     '<svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="1"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2"/></svg>', // calculator
    book:    '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="16" rx="1"/><path d="M4 9h16M8 3v4M16 3v4M9 15l2 2 4-4"/></svg>', // calendar check
    apply:   '<svg viewBox="0 0 24 24"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 14h6M13 11v6"/></svg>', // doc submit
    stories: '<svg viewBox="0 0 24 24"><path d="M12 3l2.5 5.5L20 9l-4 4 1 6-5-3-5 3 1-6L4 9l5.5-.5z"/></svg>', // star
    login:   '<svg viewBox="0 0 24 24"><path d="M14 3h5v18h-5"/><path d="M3 12h11M10 8l4 4-4 4"/></svg>', // door arrow
    pen:     '<svg viewBox="0 0 24 24"><path d="M4 20l4-1L20 7l-3-3L5 16z"/><path d="M15 6l3 3"/></svg>', // pen
    casestudy:'<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="1"/><path d="M8 15l3-3 2 2 3-4"/></svg>', // doc chart
    guide:   '<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 012-2h6v18H6a2 2 0 01-2-2z"/><path d="M20 5a2 2 0 00-2-2h-6v18h6a2 2 0 002-2z"/></svg>', // open book
    faq:     '<svg viewBox="0 0 24 24"><path d="M5 4h14v11H9l-4 4z"/><path d="M9.5 8.5a2.5 2.5 0 113.5 2.3c-.6.3-1 .8-1 1.5M12 14.5h0"/></svg>' // question bubble
  };

  /* ---- nav model ----------------------------------------------------- */
  var MENU = [
    { label: "For Military", href: "military.html", feat: {
        kicker: "For Transitioning Service Members",
        title: "Get Hired Before Your Last Day in Uniform",
        cta: "Apply Now", href: "military.html#apply",
        bg: "linear-gradient(135deg,#13241a,#0b0b0d)" },
      items: [
        { i: "program", t: "The Program", d: "How the S2S SkillBridge fellowship works", h: "military.html#program" },
        { i: "apply",   t: "How to Apply", d: "Eligibility and the path to approval", h: "military.html#apply" },
        { i: "stories", t: "Graduate Stories", d: "Where our fellows landed", h: "military.html#stories" },
        { i: "login",   t: "Candidate Login", d: "S2S Core for candidates", h: "#", todo: true }
      ] },
    { label: "For Companies", href: "companies.html", feat: {
        kicker: "For Sales Leaders",
        title: "Your Competitors Are Still Guessing on Hires",
        cta: "Partner With S2S", href: "companies.html#book",
        bg: "linear-gradient(135deg,#1a1d12,#0b0b0d)" },
      items: [
        { i: "why",     t: "Why S2S", d: "Mission-ready sales talent, ramp-ready", h: "companies.html#why" },
        { i: "results", t: "Partner Results", d: "ROI our partners actually see", h: "companies.html#results" },
        { i: "roi",     t: "ROI Calculator", d: "Run your own numbers", h: "companies.html#roi" },
        { i: "how",     t: "How It Works", d: "From intro call to placement", h: "companies.html#how" },
        { i: "book",    t: "Schedule a Call", d: "Talk to our team", h: "companies.html#book" }
      ] },
    { label: "About", href: "about.html", feat: {
        kicker: "Service 2 Software", brand: true,
        title: "HIRE WITH PURPOSE.",
        cta: "Our Story", href: "about.html#story", bg: "#0b0b0d" },
      items: [
        { i: "story",   t: "Our Story", d: "Why we built S2S", h: "about.html#story" },
        { i: "founder", t: "Meet the Founder", d: "The person behind the mission", h: "about.html#founder" },
        { i: "stories", t: "Meet the Team", d: "Who you will work with", h: "about.html#team" },
        { i: "why",     t: "Guiding Principles", d: "What we stand on", h: "about.html#principles" },
        { i: "impact",  t: "Mission Impact", d: "600+ transitions, 96% employment rate", h: "about.html#impact" }
      ] },
    { label: "Resources", href: "blog.html", feat: {
        kicker: "From the Field",
        title: "Insights for Veterans and Sales Leaders",
        cta: "Read the Blog", href: "blog.html", bg: "linear-gradient(135deg,#14171c,#0b0b0d)" },
      items: [
        { i: "pen",       t: "Blog", d: "Transition and sales playbooks", h: "blog.html" },
        { i: "casestudy", t: "Case Studies", d: "Partner outcomes in detail", h: "companies.html#results" },
        { i: "guide",     t: "SkillBridge Guide", d: "Everything on DoD SkillBridge", h: "blog.html" },
        { i: "faq",       t: "FAQ", d: "Common questions answered", h: "blog.html" }
      ] }
  ];

  var CALENDLY = "https://calendly.com/davidhester/s2s-hiring"; // company / partner intro call

  /* ---- build mega panel --------------------------------------------- */
  function megaHTML(m) {
    var links = m.items.map(function (it) {
      return '<a class="mega-item" href="' + it.h + '"' + (it.todo ? ' data-todo="portal"' : '') +
        '><span class="tile">' + (ICONS[it.i] || ICONS.pen) + '</span>' +
        '<span><span class="mt">' + it.t + '</span><span class="md">' + it.d + '</span></span></a>';
    }).join("");
    var feat = m.feat.brand
      ? '<a class="mega-feat brandcard" style="background:' + m.feat.bg + '" href="' + m.feat.href + '">' +
          '<span class="fk">' + m.feat.kicker + '</span>' +
          '<span class="ff">HIRE <span class="hollow">WITH</span> PURPOSE.</span></a>'
      : '<a class="mega-feat" style="background:' + m.feat.bg + '" href="' + m.feat.href + '">' +
          '<span class="fk">' + m.feat.kicker + '</span>' +
          '<span class="ff">' + m.feat.title + '</span>' +
          '<span class="arrow-link" style="margin-top:14px;color:var(--lime)">' + m.feat.cta + ' <span class="ar">&rarr;</span></span></a>';
    return '<div class="mega-links">' + links + '</div>' + feat;
  }

  function navHTML() {
    var mid = MENU.map(function (m, idx) {
      return '<div class="nav-item" data-idx="' + idx + '">' +
        '<a class="nav-link" href="' + m.href + '">' + m.label + ' <span class="caret"></span></a>' +
        '<div class="mega">' + megaHTML(m) + '</div></div>';
    }).join("");
    return '<nav class="nav"><div class="wrap">' +
      '<a class="brand" href="index.html">Service<span class="num">&nbsp;2&nbsp;</span>Software</a>' +
      '<div class="nav-mid">' + mid + '</div>' +
      '<div class="nav-right">' +
        '<a class="nav-link" href="#" data-todo="portal">S2S Core Login</a>' +
        '<a class="btn primary sm" href="military.html#apply"><span>Apply Now</span></a>' +
        '<button class="nav-burger" aria-label="Menu"><span></span></button>' +
      '</div></div></nav>' +
      mobileHTML();
  }

  function mobileHTML() {
    var groups = MENU.map(function (m) {
      var sub = m.items.map(function (it) { return '<a class="m-link" href="' + it.h + '">' + it.t + '</a>'; }).join("");
      return '<div class="m-head">' + m.label + '</div>' + sub;
    }).join("");
    return '<div class="mobile">' + groups +
      '<div class="m-cta">' +
        '<a class="btn primary lg" href="military.html#apply"><span>Apply Now</span></a>' +
        '<a class="btn ghost" href="companies.html#book"><span>Schedule a Call</span></a>' +
        '<a class="btn ghost" href="#" data-todo="portal"><span>S2S Core Login</span></a>' +
      '</div></div>';
  }

  function footerHTML() {
    var ICN = {
      li: '<svg viewBox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 11-.02 5 2.5 2.5 0 01.02-5zM3 9h4v12H3zM10 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21H18.6v-5.3c0-1.27-.02-2.9-1.77-2.9-1.77 0-2.04 1.38-2.04 2.8V21H10z"/></svg>',
      x:  '<svg viewBox="0 0 24 24"><path d="M17.5 3h3l-7 8 8.2 10h-6.4l-5-6.1L7 21H4l7.5-8.6L3.6 3h6.5l4.5 5.6zm-1.1 16h1.7L8.4 4.8H6.6z"/></svg>',
      yt: '<svg viewBox="0 0 24 24"><path d="M23 12s0-3.2-.4-4.7a2.5 2.5 0 00-1.8-1.8C19.2 5 12 5 12 5s-7.2 0-8.8.5A2.5 2.5 0 001.4 7.3C1 8.8 1 12 1 12s0 3.2.4 4.7a2.5 2.5 0 001.8 1.8C4.8 19 12 19 12 19s7.2 0 8.8-.5a2.5 2.5 0 001.8-1.8C23 15.2 23 12 23 12zM10 15V9l5 3z"/></svg>'
    };
    return '<footer class="footer"><div class="wrap">' +
      '<div class="footer-top">' +
        '<div class="fcol">' +
          '<div class="brand">Service<span class="num">&nbsp;2&nbsp;</span>Software</div>' +
          '<p>We turn proven military leaders into high-performing sales professionals, and connect them with companies that need ramp-ready talent.</p>' +
          '<div class="socials">' +
            '<a href="https://www.linkedin.com/company/service-2-software" aria-label="LinkedIn">' + ICN.li + '</a>' +
            '<a href="#" aria-label="X">' + ICN.x + '</a>' +
            '<a href="#" aria-label="YouTube">' + ICN.yt + '</a>' +
          '</div>' +
        '</div>' +
        '<div class="fcol"><h4>For Military</h4>' +
          '<a href="military.html#program">The Program</a><a href="military.html#apply">How to Apply</a>' +
          '<a href="military.html#stories">Graduate Stories</a>' +
          '<a href="https://ratemyskb.com/company/service-2-software">RateMySkillBridge</a></div>' +
        '<div class="fcol"><h4>For Companies</h4>' +
          '<a href="companies.html#why">Why S2S</a><a href="companies.html#results">Partner Results</a>' +
          '<a href="companies.html#roi">ROI Calculator</a><a href="companies.html#book">Schedule a Call</a></div>' +
        '<div class="fcol"><h4>Company</h4>' +
          '<a href="about.html#story">Our Story</a><a href="about.html#team">Meet the Team</a>' +
          '<a href="blog.html">Blog</a><a href="companies.html#book">Contact</a></div>' +
      '</div>' +
      '<div class="footer-bottom">' +
        '<p>&copy; ' + new Date().getFullYear() + ' Service 2 Software. DoD SkillBridge Approved &middot; 501(c)(3).</p>' +
        '<p>Hire With Purpose.</p>' +
      '</div>' +
    '</div></footer>';
  }

  /* ---- wire interactions -------------------------------------------- */
  function init() {
    var navMount = document.getElementById("site-nav");
    var footMount = document.getElementById("site-footer");
    if (navMount) navMount.innerHTML = navHTML();
    if (footMount) footMount.innerHTML = footerHTML();

    var items = Array.prototype.slice.call(document.querySelectorAll(".nav-item"));
    var closeTimer;
    items.forEach(function (item) {
      item.addEventListener("mouseenter", function () {
        clearTimeout(closeTimer);
        items.forEach(function (i) { i.classList.remove("open"); });
        item.classList.add("open");
      });
      item.addEventListener("mouseleave", function () {
        closeTimer = setTimeout(function () { item.classList.remove("open"); }, 160);
      });
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".nav-item")) items.forEach(function (i) { i.classList.remove("open"); });
    });
    window.addEventListener("scroll", function () { items.forEach(function (i) { i.classList.remove("open"); }); }, { passive: true });

    // mobile
    var burger = document.querySelector(".nav-burger");
    var mobile = document.querySelector(".mobile");
    if (burger && mobile) {
      burger.addEventListener("click", function () { mobile.classList.toggle("open"); });
      mobile.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () { mobile.classList.remove("open"); });
      });
    }

    // portal TODO links
    document.querySelectorAll('[data-todo="portal"]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        alert("The S2S Core portal is coming soon. Hang tight!");
      });
    });

    initROI();
    initForms();
  }

  /* ---- ROI calculator ------------------------------------------------ */
  var ROI = { programCost: 25000, repsTradCost: 120000, rampMonthsTrad: 9, rampMonthsS2S: 3 };
  function fmt(n) { return "$" + Math.round(n).toLocaleString(); }
  function initROI() {
    var root = document.getElementById("roi");
    if (!root) return;
    var get = function (id) { return parseFloat((document.getElementById(id) || {}).value) || 0; };
    function calc() {
      var reps = get("roi-reps");
      var acv = get("roi-acv");
      var quota = get("roi-quota");
      // pipeline value generated earlier by compressing ramp (months saved * monthly quota attainment)
      var monthsSaved = (ROI.rampMonthsTrad - ROI.rampMonthsS2S);
      var monthlyProd = (quota * acv) / 12;
      var earlyValue = reps * monthsSaved * monthlyProd;
      var savings = reps * (ROI.repsTradCost - ROI.programCost);
      var invest = reps * ROI.programCost;
      var totalGain = earlyValue + savings;
      var multiple = invest > 0 ? (totalGain / invest) : 0;

      set("out-early", fmt(earlyValue));
      set("out-savings", fmt(savings));
      set("out-invest", fmt(invest));
      set("out-mult", (multiple).toFixed(1) + "x");
    }
    function set(id, v) { var el = document.getElementById(id); if (el) el.textContent = v; }
    root.querySelectorAll("input").forEach(function (i) { i.addEventListener("input", calc); });
    calc();
  }

  /* ---- lead forms ---------------------------------------------------- */
  function initForms() {
    document.querySelectorAll("form[data-lead]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        /* TODO: POST to ActiveCampaign (proc.php) once form IDs exist.
           AC then handles the 2-hour follow-up email + Salesforce + Slack. */
        var thanks = form.parentNode.querySelector(".thanks");
        form.style.display = "none";
        if (thanks) thanks.classList.add("show");
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
