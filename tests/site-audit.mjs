import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const MAIN_URL = process.env.MAIN_URL || 'https://aipubs.cloud/';
const BLOG_URL = process.env.BLOG_URL || 'https://blog.aipubs.cloud/';
const BLOG_ARTICLE_URL = process.env.BLOG_ARTICLE_URL || '';

const failures = [];

function fail(message) {
  failures.push(message);
  console.error(`FAIL: ${message}`);
}

async function assertReachable(request, url, label) {
  try {
    const response = await request.get(url, { timeout: 30000, failOnStatusCode: false });
    if (!response.ok()) fail(`${label} returned HTTP ${response.status()}: ${url}`);
    else console.log(`PASS: ${label} ${response.status()} ${url}`);
  } catch (error) {
    fail(`${label} could not be fetched: ${error.message}`);
  }
}

async function auditPage(page, url, label) {
  console.log(`\nAuditing ${label}: ${url}`);
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  if (!response || !response.ok()) fail(`${label} navigation returned ${response?.status() ?? 'no response'}`);
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

  const axe = await new AxeBuilder({ page }).analyze();
  for (const violation of axe.violations) {
    fail(`${label} axe violation ${violation.id}: ${violation.help} (${violation.nodes.length} node(s))`);
  }

  const placeholders = await page.locator('a[href="#"]').count();
  if (placeholders > 0) fail(`${label} contains ${placeholders} placeholder href="#" anchor(s)`);

  const inertButtons = await page.locator('button:not([disabled])').evaluateAll(buttons =>
    buttons.filter(button => {
      const text = (button.textContent || '').trim();
      const label = button.getAttribute('aria-label') || button.getAttribute('title') || '';
      const handler = button.getAttribute('onclick') || '';
      return !text && !label && !handler;
    }).length
  );
  if (inertButtons > 0) fail(`${label} contains ${inertButtons} unlabeled/inert button(s)`);

  const interactiveNames = await page.locator('a,button,input,select,textarea,[role="button"]').evaluateAll(nodes =>
    nodes.filter(node => {
      const style = window.getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    }).length
  );
  console.log(`PASS: ${label} exposes ${interactiveNames} visible interactive element(s)`);
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

try {
  await assertReachable(context.request, MAIN_URL, 'Main site');
  await assertReachable(context.request, BLOG_URL, 'Blog site');
  if (BLOG_ARTICLE_URL) await assertReachable(context.request, BLOG_ARTICLE_URL, 'Blog article');

  await auditPage(page, MAIN_URL, 'Main site');

  // Exercise the main mobile navigation without depending on implementation details.
  await page.setViewportSize({ width: 390, height: 844 });
  const menuButton = page.getByRole('button', { name: /open menu/i });
  if (await menuButton.count()) {
    await menuButton.click();
    const closeButton = page.getByRole('button', { name: /close menu/i });
    if (!(await closeButton.count())) fail('Mobile menu opened without an accessible close control');
    else await closeButton.click();
  } else {
    fail('Mobile menu does not expose an accessible Open menu control');
  }

  // Return to desktop and exercise keyboard access to the global search.
  await page.setViewportSize({ width: 1440, height: 900 });
  const search = page.locator('#global-search');
  if (await search.count()) {
    await search.focus();
    if (!(await search.evaluate(el => document.activeElement === el))) fail('Global search cannot receive keyboard focus');
  } else {
    fail('Global search control is missing');
  }

  await auditPage(page, BLOG_URL, 'Blog site');
  if (BLOG_ARTICLE_URL) await auditPage(page, BLOG_ARTICLE_URL, 'Blog article');
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(`\n${failures.length} audit failure(s) detected.`);
  process.exit(1);
}

console.log('\nAll automated site audit checks passed.');
