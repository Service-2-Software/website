/*
 * Partner (hiring) forms — home #hf-co and /companies #co-cal.
 *
 * Submit opens a confirmation modal and does not post or book yet.
 * Checking "I am not ... looking for an internship" and clicking Yes posts
 * ActiveCampaign Form 16 and opens Dave's Calendly demo.
 * "I am a service member or spouse" opens the military application instead
 * and does not create a partner lead.
 */
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const INDEX_HTML = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const ORIGIN = 'https://s2s.test';
const NOT_MIL = 'I am not currently an active duty service member or spouse looking for an internship.';

async function openPage(page, urlPath) {
  await page.route('**/*', (route) => {
    const req = route.request();
    if (req.resourceType() === 'document' && req.url().startsWith(ORIGIN)) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: INDEX_HTML });
    }
    return route.abort();
  });
  await page.addInitScript(() => {
    window.__acPosts = [];
    window.__opens = [];
    window.fetch = (url, opts) => {
      const entries = {};
      if (opts && opts.body && typeof opts.body.forEach === 'function') {
        opts.body.forEach((v, k) => { entries[k] = v; });
      }
      window.__acPosts.push({ url: String(url), entries });
      return Promise.resolve({ ok: true });
    };
    window.open = (url) => { window.__opens.push(String(url)); return {}; };
  });
  await page.goto(ORIGIN + urlPath);
}

async function fillPartner(page, formSel) {
  await page.fill(`${formSel} [name=fullname]`, 'Jane Doe');
  await page.fill(`${formSel} [name=email]`, 'jane@company.com');
  await page.fill(`${formSel} [name="field\\[35\\]"]`, 'Acme');
  await page.selectOption(`${formSel} [name="field\\[34\\]"]`, 'SDR / BDR');
  await page.click(`${formSel} button[type=submit]`);
}

test('companies partner form: modal blocks Calendly until the not-military box is checked', async ({ page }) => {
  await openPage(page, '/companies');
  await fillPartner(page, '#co-step1 form');

  await expect(page.locator('#partner-gate')).toBeVisible();
  await expect(page.locator('.pgate-check span')).toHaveText(NOT_MIL);
  await expect(page.locator('#pg-yes')).toBeDisabled();
  expect(await page.evaluate(() => window.__acPosts)).toHaveLength(0);
  expect(await page.evaluate(() => window.__opens)).toHaveLength(0);

  await page.check('#pg-check');
  await expect(page.locator('#pg-yes')).toBeEnabled();
  await page.uncheck('#pg-check');
  await expect(page.locator('#pg-yes')).toBeDisabled();
  await page.check('#pg-check');
  await page.click('#pg-yes');

  await expect(page.locator('#partner-gate')).toBeHidden();
  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expect(posts[0].url).toBe('https://service2software.activehosted.com/proc.php');
  expect(posts[0].entries.f).toBe('16');
  expect(posts[0].entries.u).toBe('6ABECBE6DFD3D');
  expect(posts[0].entries.fullname).toBe('Jane Doe');
  expect(posts[0].entries.email).toBe('jane@company.com');
  expect(posts[0].entries['field[35]']).toBe('Acme');
  expect(posts[0].entries['field[34]']).toBe('Other');

  const opens = await page.evaluate(() => window.__opens);
  expect(opens).toHaveLength(1);
  expect(opens[0]).toContain('calendly.com/davidhester/s2s-hiring');
  expect(opens[0]).toContain('name=Jane%20Doe');
  expect(opens[0]).toContain('email=jane%40company.com');
  await expect(page.locator('#co-book')).toBeVisible();
});

test('companies partner form: service member path opens the military application and does not post', async ({ page }) => {
  await openPage(page, '/companies');
  await fillPartner(page, '#co-step1 form');
  await page.click('.pgate-alt');

  await expect(page.locator('#partner-gate')).toBeHidden();
  expect(await page.evaluate(() => window.__acPosts)).toHaveLength(0);
  expect(await page.evaluate(() => window.__opens)).toHaveLength(0);
  await expect(page.locator('#page-military')).toBeVisible();
  await expect(page.locator('#ac-mil form')).toBeVisible();
  await expect(page.locator('#ac-mil [name=firstname]')).toHaveValue('Jane');
  await expect(page.locator('#ac-mil [name=lastname]')).toHaveValue('Doe');
  await expect(page.locator('#ac-mil [name=email]')).toHaveValue('jane@company.com');
});

test('home partner form: Yes books Dave; military path shows the home application', async ({ page }) => {
  await openPage(page, '/');
  await page.evaluate(() => hfPick('co'));
  await fillPartner(page, '#hf-co form');
  await expect(page.locator('#partner-gate')).toBeVisible();
  expect(await page.evaluate(() => window.__acPosts)).toHaveLength(0);

  await page.keyboard.press('Escape');
  await expect(page.locator('#partner-gate')).toBeHidden();
  expect(await page.evaluate(() => window.__acPosts)).toHaveLength(0);

  await page.click('#hf-co form button[type=submit]');
  await page.click('.pgate-alt');
  await expect(page.locator('#hf-mil')).toBeVisible();
  await expect(page.locator('#hf-co')).toBeHidden();
  await expect(page.locator('#hf-mil [name=firstname]')).toHaveValue('Jane');
  await expect(page.locator('#hf-mil [name=lastname]')).toHaveValue('Doe');
  await expect(page.locator('#hf-mil [name=email]')).toHaveValue('jane@company.com');
  expect(await page.evaluate(() => window.__opens)).toHaveLength(0);

  await page.evaluate(() => hfReset());
  await page.evaluate(() => hfPick('co'));
  await fillPartner(page, '#hf-co form');
  await page.check('#pg-check');
  await page.click('#pg-yes');
  const opens = await page.evaluate(() => window.__opens);
  expect(opens).toHaveLength(1);
  expect(opens[0]).toContain('calendly.com/davidhester/s2s-hiring');
  await expect(page.locator('#hf-book-cal')).toBeVisible();
  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expect(posts[0].entries.f).toBe('16');
});
