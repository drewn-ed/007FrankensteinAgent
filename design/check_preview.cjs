// Run with an available Playwright installation and Chromium/Chrome.
const { chromium } = require('playwright');
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.DESIGN_CHROME_PATH ? { executablePath: process.env.DESIGN_CHROME_PATH } : {}),
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('requestfailed', request => errors.push(request.url() + ': ' + request.failure().errorText));
  await page.goto(pathToFileURL(path.join(__dirname, 'brand-guide.html')).href);
  await page.evaluate(() => document.fonts.ready);
  const report = { scope: 'Static design preview only', layout: [], interactions: [], errors };
  for (const width of [1440, 1024, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const id of ['overview', 'type', 'colors', 'icons', 'media', 'use']) {
      await page.locator('#tab-' + id).click();
      await page.evaluate(() => document.fonts.ready);
      const layout = await page.evaluate(() => ({
        width: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        visiblePanels: [...document.querySelectorAll('[role="tabpanel"]')].filter(el => !el.hidden).length,
      }));
      report.layout.push({ width, panel: id, ...layout, pass: layout.scrollWidth <= width && layout.visiblePanels === 1 });
    }
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.locator('#tab-icons').click();
  const icons = await page.locator('#icons .icon-tile').count();
  const rendered = await page.locator('#icons svg use').evaluateAll(nodes => nodes.every(node => {
    const id = node.getAttribute('href').slice(1);
    const box = node.getBBox();
    return document.getElementById(id) && box.width > 0 && box.height > 0;
  }));
  report.interactions.push({ name: '20 pixel icons resolve and render', pass: icons === 20 && rendered });
  await page.screenshot({ path: path.join(__dirname, 'preview-icons.png'), fullPage: true });
  await page.locator('#tab-type').click();
  await page.locator('#sample-input').fill('Ready for the next task. Version 007.');
  await page.locator('#sample-family').selectOption('display');
  report.interactions.push({ name: 'Font specimen input and available weight', pass: await page.locator('#type-sample').textContent() === 'Ready for the next task. Version 007.' && await page.locator('#sample-weight').inputValue() === '400' });
  await page.locator('#sample-family').selectOption('display');
  await page.locator('#sample-weight').selectOption('400');
  await page.locator('#sample-input').fill('Learn. Keep. Reuse.');
  await page.screenshot({ path: path.join(__dirname, 'preview-typography.png'), fullPage: true });
  await page.locator('#plain-type').click();
  report.interactions.push({ name: 'Plain typography replaces pixel headings', pass: !(await page.locator('#type h2').evaluate(el => getComputedStyle(el).fontFamily)).includes('Pixel') });
  await page.reload();
  report.interactions.push({ name: 'Plain typography preference persists', pass: await page.locator('#plain-type').getAttribute('aria-pressed') === 'true' });
  await page.locator('#plain-type').click();
  report.interactions.push({ name: 'Pixel typography restored', pass: (await page.locator('#type h2').evaluate(el => getComputedStyle(el).fontFamily)).includes('Geist Pixel Square') });
  report.interactions.push({ name: 'Real local pixel font loaded', pass: await page.evaluate(() => [...document.fonts].some(f=>f.family==='Geist Pixel Square' && f.status==='loaded')) });
  await page.locator('#tab-colors').click();
  await page.locator('#theme-toggle').click();
  report.interactions.push({ name: 'Dark preview toggle', pass: await page.locator('#app-preview').getAttribute('data-ds-theme') === 'dark' });
  await page.locator('#app-preview').screenshot({ path: path.join(__dirname, 'preview-dark.png') });
  await page.locator('#theme-toggle').click();
  await page.locator('#sample-action').click();
  report.interactions.push({ name: 'Concept button stays illustrative', pass: (await page.locator('#mock-response').textContent()).includes('No task was started') });
  await page.evaluate(() => { document.getElementById('mock-response').textContent = 'Visual concept only. No task is running here.'; });
  await page.locator('[data-copy="#FF8A3D"]').click();
  await page.waitForFunction(() => document.getElementById('notice').textContent.includes('#FF8A3D'));
  report.interactions.push({ name: 'HEX copy or visible fallback', pass: (await page.locator('#notice').textContent()).includes('#FF8A3D') });
  await page.locator('#tab-colors').click();
  await page.screenshot({ path: path.join(__dirname, 'preview-interface.png'), fullPage: true });
  await page.locator('#app-preview').screenshot({ path: path.join(__dirname, 'preview-app.png') });
  await page.locator('#tab-media').click();
  await page.locator('#replay').click();
  report.interactions.push({ name: 'One-shot motion preview', pass: (await page.locator('#film-frame').getAttribute('class')).includes('playing') });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.locator('#replay').click();
  report.interactions.push({ name: 'Reduced motion', pass: await page.locator('.frame-title span').first().evaluate(el => getComputedStyle(el).animationName) === 'none' });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.locator('#tab-overview').click();
  await page.locator('#tab-overview').focus();
  await page.keyboard.press('ArrowRight');
  report.interactions.push({ name: 'Keyboard tab navigation', pass: await page.locator('#tab-type').getAttribute('aria-selected') === 'true' });
  await page.locator('#tab-overview').click();
  await page.screenshot({ path: path.join(__dirname, 'preview-overview.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, 'preview-mobile.png'), fullPage: true });
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(pathToFileURL(path.join(__dirname, 'title-card.html')).href);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(__dirname, 'title-card-1920x1080.png') });
  report.interactions.push({ name: 'Video title dimensions', pass: await page.locator('.stage').evaluate(el => el.offsetWidth === 1920 && el.offsetHeight === 1080) });
  await page.goto(pathToFileURL(path.join(__dirname, 'brand-guide.html')).href);
  report.accessibility = [];
  for (const mode of ['spacing overrides', '200% text enlargement']) {
    await page.setViewportSize({ width: mode === 'spacing overrides' ? 320 : 1440, height: 1000 });
    for (const id of ['overview','type','colors','icons','media','use']) {
      await page.goto(pathToFileURL(path.join(__dirname, 'brand-guide.html')).href+'#'+id);
      await page.reload();
      await page.evaluate(() => document.fonts.ready);
      if(mode==='spacing overrides') await page.addStyleTag({content:'* { line-height:1.5!important; letter-spacing:.12em!important; word-spacing:.16em!important; } p { margin-bottom:2em!important; }'});
      else await page.evaluate(()=>{
        const items=[...document.querySelectorAll('body *')].filter(el=>el instanceof HTMLElement).map(el=>[el,parseFloat(getComputedStyle(el).fontSize)*2]);
        items.forEach(([el,size])=>el.style.setProperty('font-size',size+'px','important'));
      });
      const geometry=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
      report.accessibility.push({mode,panel:id,...geometry,pass:geometry.scrollWidth<=geometry.width});
      if (id==='type' && mode==='200% text enlargement') await page.screenshot({path:path.join(__dirname,'preview-type-enlarged.png'),fullPage:true});
    }
  }
  report.accessibilityScope = 'No horizontal overflow under text enlargement and spacing overrides, plus manual screenshot review. Not a full WCAG or assistive-technology audit.';
  report.fonts = await page.evaluate(() => [...document.fonts].map(font => ({ family: font.family, status: font.status })));
  report.passed = report.accessibility.every(item => item.pass) && report.layout.every(item => item.pass) && report.interactions.every(item => item.pass) && errors.length === 0;
  fs.writeFileSync(path.join(__dirname, 'browser-validation.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ passed: report.passed, layoutChecks: report.layout.length, accessibility: report.accessibility, interactions: report.interactions, errors }));
  await browser.close();
  if (!report.passed) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
