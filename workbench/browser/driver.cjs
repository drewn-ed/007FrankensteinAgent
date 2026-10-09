// Trusted, fixed browser operations. Model-generated JavaScript is never evaluated.
const { chromium } = require('playwright');
const readline = require('node:readline');
const fs = require('node:fs');
const path = require('node:path');
const downloadRoot=path.join(__dirname,'../../.runtime/browser-downloads');
let downloads=[], pendingDownloads=[];
let browser, context, page, origin, cached = {connected:false}, generation=0, refs=new Map();
const max = (text, size=12000) => String(text || '').slice(0,size);
function approvedURL(raw) {
  const url=new URL(raw);
  if(!['https:','http:'].includes(url.protocol) || url.username || url.password) throw Error('Use an HTTP or HTTPS URL without embedded credentials.');
  if(url.origin!==origin)throw Error('Navigation outside the connected site is not allowed. Connect that site separately.');
  return url;
}
function assertPage() { if(!page||page.isClosed())throw Error('Connect a browser first.'); approvedURL(page.url()); }
async function snapshot() {
  assertPage(); generation++;refs.clear();
  const controls=[];
  const handles=await page.locator('button,a[href],input:not([type=hidden]),textarea,select,[role=button],[role=checkbox],[role=tab],[contenteditable=true]').elementHandles();
  for(const el of handles.slice(0,250)) {
    if(controls.length>=100)break;
    if(!await el.isVisible().catch(()=>false))continue;
    const info=await el.evaluate(e=>{
      const label=e.labels?.[0]?.cloneNode(true);
      label?.querySelectorAll('input,select,textarea').forEach(node=>node.remove());
      const labelText=label?.textContent?.replace(/\s+/g,' ').trim();
      return {tag:e.tagName.toLowerCase(),role:e.getAttribute('role')||'',type:e.getAttribute('type')||'',name:e.getAttribute('aria-label')||labelText||e.getAttribute('placeholder')||e.innerText||e.getAttribute('title')||e.getAttribute('name')||'',disabled:!!e.disabled,value:e.type==='password'?'[hidden]':('value'in e?String(e.value).slice(0,200):undefined),checked:typeof e.checked==='boolean'?e.checked:undefined,options:e.tagName==='SELECT'?[...e.options].map(o=>({label:o.label,value:o.value})):undefined};
    });
    const ref=`e${generation}_${controls.length+1}`;refs.set(ref,el);controls.push({ref,...info,name:max(info.name,200).replace(/\s+/g,' ').trim()});
  }
  await Promise.all(pendingDownloads); pendingDownloads=[];
  const screenshot=await page.screenshot({type:'jpeg',quality:65,timeout:5000,animations:'disabled'});
  cached={connected:true,url:page.url(),origin,title:await page.title(),text:max(await page.locator('body').innerText({timeout:3000})),elements:controls,screenshot:screenshot.toString('base64'),updated_at:Date.now(),generation,download_files:downloads.splice(0)};
  if(origin==='https://event.workspace.demo')cached.event_state=await page.locator('#event-state').evaluate(e=>JSON.parse(e.textContent));
  if(origin==='https://workspace.demo')cached.registration_state=await page.evaluate(()=>({
    count:Number(document.querySelector('#count')?.textContent.match(/^(\d+) registered$/)?.[1]??NaN),
    records:[...document.querySelectorAll('#participants article')].map(row=>{
      const fields=row.querySelector('p')?.textContent.split(' · ')||[];
      return {name:row.querySelector('strong')?.textContent,email:fields[0],workshop:fields[1],checked:fields[2]==='Checked in'};
    })
  }));
  return cached;
}
async function connect(args) {
  if(browser)await browser.close();
  const parsed=new URL(args.url); origin=parsed.origin;approvedURL(args.url);
  browser=await chromium.launch({channel:'chrome',headless:args.headless===true});
  context=await browser.newContext({viewport:{width:1280,height:800},acceptDownloads:true,serviceWorkers:'block',permissions:[]});
  await context.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url());
    if(url.origin!==origin){await route.abort('blockedbyclient');return;}
    if(['https://workspace.demo','https://event.workspace.demo'].includes(origin)) {
      const name=url.pathname==='/'?(origin==='https://event.workspace.demo'?'event.html':'practice.html'):url.pathname.slice(1);
      const allowed={'practice.html':'text/html','practice.js':'text/javascript','practice.css':'text/css','event.html':'text/html','event.js':'text/javascript','event.css':'text/css'};
      const fonts={'plex.ttf':'../../design/fonts/IBMPlexMono-Regular.ttf','pixel.woff2':'../../design/fonts/GeistPixel-Square.woff2'};
      if(fonts[name]&&fs.existsSync(path.join(__dirname,fonts[name])))return route.fulfill({status:200,contentType:'font/woff2',body:fs.readFileSync(path.join(__dirname,fonts[name]))});
      if(!allowed[name])return route.fulfill({status:404,body:'Not found'});
      return route.fulfill({status:200,contentType:allowed[name],body:fs.readFileSync(path.join(__dirname,name))});
    }
    // continue() can follow a redirect without another route interception.
    // Fetch only the approved request, never automatically follow a Location.
    try {
      const response=await route.fetch({maxRedirects:0,maxRetries:0,timeout:15000});
      if(response.status()>=300&&response.status()<400&&response.headers().location) {
        await response.dispose();await route.abort('blockedbyclient');return;
      }
      await route.fulfill({response});await response.dispose();
    } catch { await route.abort('failed').catch(()=>{}); }
  });
  // No websocket capability is granted by this connector.
  await context.routeWebSocket('**/*',socket=>socket.close());
  page=await context.newPage();page.setDefaultTimeout(5000);
  context.on('page',p=>{if(p!==page)p.close().catch(()=>{});});
  page.on('download',download=>{
    const task=(async()=>{
      fs.mkdirSync(downloadRoot,{recursive:true,mode:0o700});
      const dest=path.join(downloadRoot,require('node:crypto').randomUUID());
      try {
        await download.saveAs(dest);
        if(fs.statSync(dest).size>10*1024*1024)throw Error('Download exceeds 10 MB.');
        downloads.push({name:path.basename(download.suggestedFilename()).replace(/[\\/:\r\n]/g,'_').slice(0,180)||'download',path:dest});
      } catch {if(fs.existsSync(dest))fs.unlinkSync(dest);}
      finally {await download.delete().catch(()=>{});}
    })();pendingDownloads.push(task);
  });
  page.on('dialog',dialog=>dialog.dismiss().catch(()=>{}));
  await page.goto(args.url,{waitUntil:'domcontentloaded',timeout:15000});
  return snapshot();
}
async function act(args) {
  assertPage();
  const {action,ref,value}=args;
  if(action==='inspect')return snapshot();
  if(action==='navigate'){await page.goto(approvedURL(value).href,{waitUntil:'domcontentloaded',timeout:15000});return snapshot();}
  const target=refs.get(ref);if(!target)throw Error('The element reference is stale. Inspect the current page again.');
  if(action==='upload'){if(typeof args.file_path!=='string')throw Error('No authorized file supplied.');await target.setInputFiles({name:args.file_name||'attachment',mimeType:args.file_mime||'application/octet-stream',buffer:fs.readFileSync(args.file_path)},{timeout:5000});}
  else if(action==='click')await target.click({timeout:5000});
  else if(action==='fill'){if(typeof value!=='string'||value.length>12000)throw Error('Invalid text input.');await target.fill(value,{timeout:5000});}
  else if(action==='select')await target.selectOption(String(value),{timeout:5000});
  else if(action==='check')await target.setChecked(value===true,{timeout:5000});
  else if(action==='press'){
    if(!['Enter','Tab','Escape','ArrowDown','ArrowUp','Space'].includes(value))throw Error('This key is not permitted.');
    await target.press(value,{timeout:5000});
  } else throw Error('Unsupported browser operation.');
  await new Promise(resolve=>setTimeout(resolve,180));
  await page.waitForLoadState('domcontentloaded',{timeout:2000}).catch(()=>{});
  return snapshot();
}
async function dispatch(message) {
  try {
    let result;
    if(message.method==='connect')result=await connect(message.params);
    else if(message.method==='act')result=await act(message.params);
    else if(message.method==='state')result=cached;
    else if(message.method==='disconnect'){if(browser)await browser.close();browser=context=page=null;refs.clear();result=cached={connected:false};}
    else throw Error('Unknown browser command.');
    process.stdout.write(JSON.stringify({id:message.id,result})+'\n');
  }catch(error){process.stdout.write(JSON.stringify({id:message.id,error:max(error.message,500)})+'\n');}
}
let queue=Promise.resolve();
readline.createInterface({input:process.stdin}).on('line',line=>{
  if(line.length>100000)return;
  try{const message=JSON.parse(line);queue=queue.then(()=>dispatch(message));}catch{}
}).on('close',()=>{if(browser)browser.close().finally(()=>process.exit());else process.exit();});
