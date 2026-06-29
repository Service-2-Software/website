/* ============================================================
   Service 2 Software — Navigation Logic
   ============================================================ */

(function () {
  'use strict';

  const nav     = document.getElementById('site-nav');
  const items   = document.querySelectorAll('.nav-item[data-panel]');
  const panels  = document.querySelectorAll('.mega-panel');
  const burger  = document.querySelector('.nav-hamburger');
  const drawer  = document.querySelector('.mobile-drawer');

  let closeTimer = null;
  let activePanel = null;

  /* ─── Mega Panel Logic ─────────────────────────────────── */
  function openPanel(name) {
    clearTimeout(closeTimer);

    if (activePanel === name) return;

    // Close any open panel first
    closeAllPanels(false);

    const panel = document.getElementById('panel-' + name);
    const item  = document.querySelector('.nav-item[data-panel="' + name + '"]');

    if (!panel || !item) return;

    panel.classList.add('open');
    item.classList.add('mega-open');
    activePanel = name;
  }

  function closeAllPanels(immediate) {
    if (immediate) {
      _doClose();
    } else {
      closeTimer = setTimeout(_doClose, 200);
    }
  }

  function _doClose() {
    panels.forEach(p  => p.classList.remove('open'));
    items.forEach(i   => i.classList.remove('mega-open'));
    activePanel = null;
  }

  /* Attach hover events to nav items */
  items.forEach(item => {
    const name = item.dataset.panel;

    item.addEventListener('mouseenter', () => openPanel(name));
    item.addEventListener('mouseleave', () => closeAllPanels(false));
  });

  /* Keep panel open while hovering it */
  panels.forEach(panel => {
    panel.addEventListener('mouseenter', () => clearTimeout(closeTimer));
    panel.addEventListener('mouseleave', () => closeAllPanels(false));
  });

  /* Close on outside click */
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !e.target.closest('.mega-panels')) {
      closeAllPanels(true);
    }
  });

  /* Close on scroll */
  window.addEventListener('scroll', () => {
    closeAllPanels(true);
    if (window.scrollY > 20) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }, { passive: true });

  /* ─── Mobile Hamburger ─────────────────────────────────── */
  if (burger && drawer) {
    burger.addEventListener('click', () => {
      const isOpen = drawer.classList.contains('open');
      drawer.classList.toggle('open');
      burger.classList.toggle('open');
      document.body.style.overflow = isOpen ? '' : 'hidden';
    });

    /* Close mobile drawer on link click */
    drawer.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        drawer.classList.remove('open');
        burger.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ─── Deep Link Handler ────────────────────────────────── */
  document.querySelectorAll('a[href*="#"]').forEach(link => {
    link.addEventListener('click', function (e) {
      const href  = this.getAttribute('href');
      const parts = href.split('#');
      const page  = parts[0];
      const hash  = parts[1];

      if (!hash) return;

      const currentPage = window.location.pathname.split('/').pop() || 'index.html';
      const isSamePage  = !page || page === currentPage || page === '' || page === '/';

      if (isSamePage) {
        e.preventDefault();
        closeAllPanels(true);
        const target = document.getElementById(hash);
        if (target) {
          const offset = target.getBoundingClientRect().top + window.scrollY - 80;
          window.scrollTo({ top: offset, behavior: 'smooth' });
        }
      }
      // Cross-page links let the browser navigate naturally
    });
  });

})();
