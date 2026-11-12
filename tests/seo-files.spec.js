/*
 * robots.txt and sitemap.xml — crawler files served from the site root.
 *
 * robots.txt must allow all crawlers and point at the sitemap. sitemap.xml
 * must be well-formed XML listing exactly the public routes the in-page
 * router (PAGE_ROUTES in index.html) defines, minus the hidden
 * /sb-application page. Each listed URL must render its own page and
 * canonicalize to itself; unknown paths fall back to the homepage canonical,
 * which is why they don't belong in the sitemap.
 */
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const INDEX_HTML = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const ROBOTS_TXT = fs.readFileSync(path.join(ROOT, 'robots.txt'), 'utf8');
const SITEMAP_XML = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
const ORIGIN = 'https://s2s.test';
const CANONICAL_ORIGIN = 'https://service2software.org';
const HIDDEN_PATHS = ['/sb-application'];

function sitemapLocs() {
  return [...SITEMAP_XML.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
}

async function openPage(page, urlPath) {
  await page.route('**/*', (route) => {
    const req = route.request();
    if (req.resourceType() === 'document' && req.url().startsWith(ORIGIN)) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: INDEX_HTML });
    }
    return route.abort();
  });
  await page.goto(ORIGIN + urlPath);
}

test('robots.txt allows all crawlers and points at the sitemap', () => {
  expect(ROBOTS_TXT).toMatch(/^User-agent: \*$/m);
  expect(ROBOTS_TXT).toMatch(/^Allow: \/$/m);
  expect(ROBOTS_TXT).not.toMatch(/^Disallow:/m);
  expect(ROBOTS_TXT).toMatch(/^Sitemap: https:\/\/service2software\.org\/sitemap\.xml$/m);
});

test('sitemap.xml is well-formed and lists only canonical apex URLs', async ({ page }) => {
  await openPage(page, '/');
  const parseError = await page.evaluate((xml) => {
    const doc = new DOMParser().parseFromString(xml, 'application/xml');
    const err = doc.querySelector('parsererror');
    return err ? err.textContent : null;
  }, SITEMAP_XML);
  expect(parseError).toBeNull();

  expect(SITEMAP_XML).toContain('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
  const locs = sitemapLocs();
  expect(locs.length).toBeGreaterThan(0);
  expect(new Set(locs).size).toBe(locs.length);
  expect(locs).toContain(`${CANONICAL_ORIGIN}/`);
  for (const loc of locs) {
    expect(loc.startsWith(`${CANONICAL_ORIGIN}/`)).toBe(true);
    expect(loc).not.toContain('#');
    expect(loc).not.toContain('www.');
  }
  expect(locs).not.toContain(`${CANONICAL_ORIGIN}/sb-application`);
  expect(locs).not.toContain(`${CANONICAL_ORIGIN}/allegiantvets`);
});

test('sitemap matches the router: every public PAGE_ROUTES path, nothing else', async ({ page }) => {
  await openPage(page, '/');
  const routePaths = await page.evaluate(() =>
    Object.values(PAGE_ROUTES).map((r) => r.path)
  );
  const publicPaths = routePaths.filter((p) => !HIDDEN_PATHS.includes(p));
  const sitemapPaths = sitemapLocs().map((loc) => loc.slice(CANONICAL_ORIGIN.length));
  expect(sitemapPaths.sort()).toEqual(publicPaths.sort());
});

test('each sitemap URL renders a distinct page that canonicalizes to itself', async ({ page }) => {
  await openPage(page, '/');
  for (const loc of sitemapLocs()) {
    const urlPath = loc.slice(CANONICAL_ORIGIN.length);
    await page.goto(ORIGIN + urlPath);
    await expect(page.locator('link[rel=canonical]')).toHaveAttribute('href', loc);
    await expect(page.locator('.page.ac')).toHaveCount(1);
  }
});

test('unknown paths fall back to the homepage canonical and stay out of the sitemap', async ({ page }) => {
  await openPage(page, '/allegiantvets');
  await expect(page.locator('link[rel=canonical]')).toHaveAttribute('href', `${CANONICAL_ORIGIN}/`);
  await expect(page.locator('#page-home')).toHaveClass(/ac/);
});
