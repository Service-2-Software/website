/* Mega menu + mobile nav behavior. Binds after partials are injected. */
function initNav() {
  const items = document.querySelectorAll('.nav-item[data-mega]');
  let closeTimer;

  function closeAll() {
    items.forEach((it) => {
      it.classList.remove('open');
      const m = it.querySelector('.mega');
      if (m) m.classList.remove('open');
    });
  }

  items.forEach((item) => {
    const mega = item.querySelector('.mega');
    const open = () => {
      clearTimeout(closeTimer);
      closeAll();
      item.classList.add('open');
      if (mega) mega.classList.add('open');
    };
    const scheduleClose = () => {
      closeTimer = setTimeout(closeAll, 180); // small delay prevents flicker
    };
    item.addEventListener('mouseenter', open);
    item.addEventListener('mouseleave', scheduleClose);
    if (mega) {
      mega.addEventListener('mouseenter', () => clearTimeout(closeTimer));
      mega.addEventListener('mouseleave', scheduleClose);
    }
  });

  // Close on scroll or outside click
  window.addEventListener('scroll', closeAll, { passive: true });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item')) closeAll();
  });

  // Mobile toggle
  const toggle = document.querySelector('.nav-toggle');
  const mobile = document.getElementById('mobileMenu');
  if (toggle && mobile) {
    toggle.addEventListener('click', () => {
      const isOpen = mobile.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
    mobile.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => {
        mobile.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      })
    );
  }

  // Footer year
  const yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
}

document.addEventListener('partials:loaded', initNav);
