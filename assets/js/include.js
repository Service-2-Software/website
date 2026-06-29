/* Lightweight HTML partial includes so nav + footer have one source of truth.
   Usage: <div data-include="/partials/nav.html"></div>
   After injection we dispatch "partials:loaded" so nav.js can bind. */
(async function () {
  const slots = document.querySelectorAll('[data-include]');
  await Promise.all([...slots].map(async (el) => {
    const url = el.getAttribute('data-include');
    try {
      const res = await fetch(url);
      el.innerHTML = await res.text();
    } catch (e) {
      el.innerHTML = '<!-- failed to load ' + url + ' -->';
      console.error('Include failed:', url, e);
    }
  }));
  document.dispatchEvent(new CustomEvent('partials:loaded'));
})();
