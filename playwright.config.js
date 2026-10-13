// Tests run fully offline: every page request is fulfilled from disk or
// aborted inside the specs (see tests/mil-apply-forms.spec.js), so no web
// server and no outbound network access are needed.
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'tests',
  fullyParallel: true,
  reporter: [['list']],
  use: {
    // index.html ships a CSP meta tag; bypass it so test stubs can run.
    bypassCSP: true,
    browserName: 'chromium'
  }
});
