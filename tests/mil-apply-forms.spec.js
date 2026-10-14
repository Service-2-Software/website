/*
 * Military application forms (home #hf-mil and /military #ac-mil) — AC Form 11.
 *
 * All outbound network is blocked: the document is served from disk via
 * route interception, every other request is aborted, and window.fetch /
 * window.open are stubbed in-page so nothing ever leaves the browser.
 *
 * Asserts:
 *  - field[8] (Separation date) posts in YYYY-MM-DD format,
 *  - field[32] derives the exact legacy dropdown strings for sample dates in
 *    every window (incl. boundaries and month-end clamping),
 *  - Calendly popup/skip behavior follows the derived field[32] value,
 *  - fullname join, phone E.164, field[5] Branch, and the AC Form 11
 *    identifiers (u/f/or) are unchanged.
 */
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const INDEX_HTML = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const ORIGIN = 'https://s2s.test';
// Every date-window assertion is relative to this frozen "today".
const FIXED_TODAY = '2026-06-15T12:00:00';

async function openPage(page, urlPath) {
  // Freeze Date (timers keep running) so window mapping is deterministic.
  await page.clock.setFixedTime(new Date(FIXED_TODAY));

  // Block ALL outbound requests; only the document itself is served from disk.
  await page.route('**/*', (route) => {
    const req = route.request();
    if (req.resourceType() === 'document' && req.url().startsWith(ORIGIN)) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: INDEX_HTML });
    }
    return route.abort();
  });

  // Record AC posts and Calendly window.open calls instead of performing them.
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

/* ─── field[32] derivation: sample dates in every window ─── */

const WINDOW_CASES = [
  // [field[8] value, expected field[32]] with today frozen at 2026-06-15
  ['2025-01-01', 'Already separated'],       // far past
  ['2026-06-14', 'Already separated'],       // yesterday
  ['2026-06-15', 'Less than 3 months'],      // today → separating today, not separated
  ['2026-07-20', 'Less than 3 months'],      // mid-window
  ['2026-09-14', 'Less than 3 months'],      // last day under 3 months
  ['2026-09-15', '3-6 months'],              // exactly 3 months → higher window
  ['2026-11-01', '3-6 months'],              // mid-window
  ['2026-12-14', '3-6 months'],              // last day under 6 months
  ['2026-12-15', '6-12 months'],             // exactly 6 months → higher window
  ['2027-03-01', '6-12 months'],             // mid-window
  ['2027-06-15', '6-12 months'],             // exactly 12 months stays 6-12 ("More than 12" is strict)
  ['2027-06-16', 'More than 12 months'],     // first day past 12 months
  ['2030-01-01', 'More than 12 months']      // far future
];

test('milEtsWindow maps dates to the exact legacy field[32] strings', async ({ page }) => {
  await openPage(page, '/');
  for (const [date, expected] of WINDOW_CASES) {
    const got = await page.evaluate((d) => milEtsWindow(d), date);
    expect(got, `field[8]=${date}`).toBe(expected);
  }
  // Invalid / empty input derives nothing (date input is required anyway).
  expect(await page.evaluate(() => milEtsWindow(''))).toBe('');
  expect(await page.evaluate(() => milEtsWindow('not-a-date'))).toBe('');
});

test('milEtsWindow clamps month-end overflow (Nov 30 + 3mo -> Feb 28)', async ({ page }) => {
  await openPage(page, '/');
  await page.clock.setFixedTime(new Date('2026-11-30T12:00:00'));
  expect(await page.evaluate(() => milEtsWindow('2027-02-27'))).toBe('Less than 3 months');
  expect(await page.evaluate(() => milEtsWindow('2027-02-28'))).toBe('3-6 months');
});

/* ─── end-to-end submits ─── */

async function fillMilForm(page, formSel, { date, phone, branch, leadSource, smsConsent }) {
  await page.fill(`${formSel} [name=firstname]`, 'Jane');
  await page.fill(`${formSel} [name=lastname]`, 'Doe');
  await page.fill(`${formSel} [name=email]`, 'jane@example.com');
  if (phone) await page.fill(`${formSel} [name=phone]`, phone);
  await page.selectOption(`${formSel} [name="field\\[5\\]"]`, branch || 'US Army');
  if (date) await page.fill(`${formSel} [name="field\\[8\\]"]`, date);
  if (leadSource) await page.selectOption(`${formSel} [name="field\\[47\\]"]`, leadSource);
  if (smsConsent) await page.check(`${formSel} [name=sms_consent]`);
  await page.click(`${formSel} button[type=submit]`);
}

function expectForm11Basics(post, branch = 'US Army') {
  expect(post.url).toBe('https://service2software.activehosted.com/proc.php');
  expect(post.entries.u).toBe('11');
  expect(post.entries.f).toBe('11');
  expect(post.entries.or).toBe('a0d5e878-42eb-41ee-9e19-4dd997d107e2');
  expect(post.entries.fullname).toBe('Jane Doe');
  expect(post.entries.firstname).toBeUndefined();
  expect(post.entries.lastname).toBeUndefined();
  expect(post.entries['field[5]']).toBe(branch);
  if (branch !== 'Military Spouse') {
    expect(post.entries['field[8]']).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  }
}

test('home #hf-mil: 6-12 months window posts field[8]+field[32] and opens Calendly', async ({ page }) => {
  await openPage(page, '/');
  await page.evaluate(() => hfPick('mil'));
  await fillMilForm(page, '#hf-mil form', { date: '2027-01-10', phone: '(555) 555-5555', leadSource: 'LinkedIn', smsConsent: true });

  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expectForm11Basics(posts[0]);
  expect(posts[0].entries['field[8]']).toBe('2027-01-10');
  expect(posts[0].entries['field[32]']).toBe('6-12 months');
  expect(posts[0].entries['field[47]']).toBe('LinkedIn');
  expect(posts[0].entries.sms_consent).toBe('on'); // checked box posts on, same as AC embed
  expect(posts[0].entries.phone).toBe('+15555555555');

  // Calendly script is blocked, so calPopup falls back to window.open.
  const opens = await page.evaluate(() => window.__opens);
  expect(opens).toHaveLength(1);
  expect(opens[0]).toContain('calendly.com/patrick-service2software/initial-call-with-service-2-software');
  expect(opens[0]).toContain('name=Jane%20Doe');
  expect(opens[0]).toContain('email=jane%40example.com');
  await expect(page.locator('#hf-book-cal')).toBeVisible();
});

test('home #hf-mil: already-separated date skips Calendly', async ({ page }) => {
  await openPage(page, '/');
  await page.evaluate(() => hfPick('mil'));
  await fillMilForm(page, '#hf-mil form', { date: '2026-06-14' });

  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expectForm11Basics(posts[0]);
  expect(posts[0].entries['field[8]']).toBe('2026-06-14');
  expect(posts[0].entries['field[32]']).toBe('Already separated');
  expect(posts[0].entries['field[47]']).toBe(''); // optional lead source left unselected posts empty (same as AC embed)
  expect(posts[0].entries.sms_consent).toBeUndefined(); // unchecked consent box is omitted entirely
  expect(posts[0].entries.phone).toBe(''); // optional phone left blank stays blank

  expect(await page.evaluate(() => window.__opens)).toHaveLength(0);
  expect(await page.evaluate(() => LAST_CAL)).toBeNull();
  await expect(page.locator('#hf-book-cal')).toBeHidden();
  await expect(page.locator('#hf-book-s')).toContainText('follow up by email');
});

test('/military #ac-mil: less-than-3-months date skips Calendly', async ({ page }) => {
  await openPage(page, '/military');
  await fillMilForm(page, '#ac-mil form', { date: '2026-08-01' });

  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expectForm11Basics(posts[0]);
  expect(posts[0].entries['field[8]']).toBe('2026-08-01');
  expect(posts[0].entries['field[32]']).toBe('Less than 3 months');

  expect(await page.evaluate(() => window.__opens)).toHaveLength(0);
  expect(await page.evaluate(() => LAST_CAL)).toBeNull();
  await expect(page.locator('#ac-book-cal')).toBeHidden();
  await expect(page.locator('#ac-book-s')).toContainText('follow up by email');
});

test('/military #ac-mil: more-than-12-months window opens Calendly', async ({ page }) => {
  await openPage(page, '/military');
  await fillMilForm(page, '#ac-mil form', { date: '2028-01-01', phone: '+44 20 7946 0958' });

  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expectForm11Basics(posts[0]);
  expect(posts[0].entries['field[8]']).toBe('2028-01-01');
  expect(posts[0].entries['field[32]']).toBe('More than 12 months');
  expect(posts[0].entries.phone).toBe('+442079460958');

  const opens = await page.evaluate(() => window.__opens);
  expect(opens).toHaveLength(1);
  expect(opens[0]).toContain('calendly.com/patrick-service2software/initial-call-with-service-2-software');
  await expect(page.locator('#ac-book-cal')).toBeVisible();
});

test('Military Spouse: date field hidden, posts field[32]="N/A - Spouse" without field[8], opens Calendly', async ({ page }) => {
  await openPage(page, '/');
  await page.evaluate(() => hfPick('mil'));

  const dateField = page.locator('#hf-mil form input[name="field\\[8\\]"]');
  // Selecting Military Spouse hides the date input and drops its required flag...
  await page.selectOption('#hf-mil form [name="field\\[5\\]"]', 'Military Spouse');
  await expect(dateField).toBeHidden();
  expect(await dateField.evaluate((el) => el.required)).toBe(false);
  // ...and switching back restores it.
  await page.selectOption('#hf-mil form [name="field\\[5\\]"]', 'US Army');
  await expect(dateField).toBeVisible();
  expect(await dateField.evaluate((el) => el.required)).toBe(true);

  await fillMilForm(page, '#hf-mil form', { branch: 'Military Spouse', leadSource: 'SpouseWorks' });

  const posts = await page.evaluate(() => window.__acPosts);
  expect(posts).toHaveLength(1);
  expectForm11Basics(posts[0], 'Military Spouse');
  expect(posts[0].entries['field[32]']).toBe('N/A - Spouse');
  expect(posts[0].entries['field[8]']).toBeUndefined(); // empty date dropped from payload
  expect(posts[0].entries['field[47]']).toBe('SpouseWorks');

  // Spouses book the intro call as usual (only the two timing values skip).
  const opens = await page.evaluate(() => window.__opens);
  expect(opens).toHaveLength(1);
  expect(opens[0]).toContain('calendly.com/patrick-service2software/initial-call-with-service-2-software');
  await expect(page.locator('#hf-book-cal')).toBeVisible();
});

const FIELD_47_OPTIONS = [
  '', '7 Eagle', 'Allegiant Vets', 'Candidate Referral', 'Facebook', 'Flyer',
  'Job Fair', 'LinkedIn', 'S2S Website', 'SFL-TAP', 'SkillBridge Network',
  'DoW Skillbridge Website', 'Rate My Skillbridge', 'SpouseWorks', 'Other'
];

test('both mil forms: required Separation Date input, field[47] options match AC Form 11, no ETS dropdown', async ({ page }) => {
  await openPage(page, '/');
  for (const sel of ['#hf-mil form', '#ac-mil form']) {
    const form = page.locator(sel);
    const date = form.locator('input[type=date][name="field\\[8\\]"]');
    await expect(date).toHaveAttribute('required', '');
    await expect(form.locator('label', { hasText: 'Separation Date' })).toHaveCount(1);
    await expect(form.locator('select[name="field\\[32\\]"]')).toHaveCount(0);
    const field47Values = await form.locator('select[name="field\\[47\\]"] option')
      .evaluateAll((opts) => opts.map((o) => o.value));
    expect(field47Values).toEqual(FIELD_47_OPTIONS);
    const consent = form.locator('input[type=checkbox][name=sms_consent]');
    await expect(consent).toHaveCount(1);
    expect(await consent.evaluate((el) => el.required)).toBe(false); // optional, same as AC Form 11
    await expect(form.locator('.ac-consent span')).toContainText('from Service 2 Software at the number provided');
  }
});
