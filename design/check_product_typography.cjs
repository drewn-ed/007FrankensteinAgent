// UI-only fixture: no model requests, task creation or stored product data.
const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.DESIGN_CHROME_PATH?{executablePath:process.env.DESIGN_CHROME_PATH}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure().errorText));
 await page.route('**/api/**',route=>{
  if(route.request().method()!=='GET')throw new Error('No mutations allowed in typography checks');
  return route.fulfill({json:{model:'UI test fixture',model_ready:true,busy:false,limits:{calls:10,seconds:90},registry:[],runs:[]}});
 });
 await page.route('**/qa-text-spacing.css',route=>route.fulfill({contentType:'text/css',body:'*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'}));
 const base=process.env.DESIGN_PRODUCT_URL||'http://127.0.0.1:8767';
 const checks=[];const add=(name,pass)=>checks.push({name,pass});
 await page.goto(base);await page.evaluate(()=>document.fonts.ready);
 add('Actual pixel font loaded',await page.evaluate(()=>[...document.fonts].some(f=>f.family==='Geist Pixel Square'&&f.status==='loaded')));
 add('Actual IBM Plex Mono loaded',await page.evaluate(()=>[...document.fonts].some(f=>f.family==='IBM Plex Mono'&&f.status==='loaded')));
 add('Pixel heading',await page.locator('h1').first().evaluate(el=>getComputedStyle(el).fontFamily.includes('Pixel')));
 add('IBM Plex Mono task input',await page.locator('#message').evaluate(el=>!getComputedStyle(el).fontFamily.includes('Pixel')&&getComputedStyle(el).fontFamily.includes('IBM Plex Mono')));
 await page.locator('#settings').click();
 await page.locator('#plain-type').focus();await page.keyboard.press('Space');
 add('Keyboard preference changes heading',await page.locator('h1').first().evaluate(el=>!getComputedStyle(el).fontFamily.includes('Pixel')));
 await page.reload();add('Plain preference persists',await page.locator('#plain-type').getAttribute('aria-pressed')==='true');await page.locator('#settings').click();await page.locator('#plain-type').click();await page.locator('#close-settings').click();
 await page.screenshot({path:'/tmp/plex-product-desktop.png',fullPage:true});
 for(const width of [1440,720,390,320]){await page.setViewportSize({width,height:1000});add('Document width at '+width,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
 await page.addStyleTag({url:base+'/qa-text-spacing.css'});
 add('Spacing at 320 CSS px',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:'/tmp/plex-product-spacing.png',fullPage:true});
 await page.setViewportSize({width:1440,height:1000});await page.reload();await page.evaluate(()=>document.fonts.ready);
 await page.evaluate(()=>{
  const sizes=[...document.querySelectorAll('body *')].filter(el=>el instanceof HTMLElement).map(el=>[el,parseFloat(getComputedStyle(el).fontSize)*2]);
  sizes.forEach(([el,size])=>el.style.setProperty('font-size',size+'px','important'));
 });
 add('200% text enlargement',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:'/tmp/plex-product-enlarged.png',fullPage:true});
 const report={scope:'Typography of the browser design preview with its default example content; API requests intercepted, no inference. Document overflow checks do not detect clipping inside fixed app panels. Not a complete accessibility audit.',checks,errors,passed:checks.every(c=>c.pass)&&!errors.length};
 fs.writeFileSync(path.join(__dirname,'browser-product-typography.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));await browser.close();if(!report.passed)process.exitCode=1;
})().catch(error=>{console.error(error);process.exit(1)});
