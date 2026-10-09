const {chromium}=require('playwright');
const path=require('node:path');
const fs=require('node:fs');
const {pathToFileURL}=require('node:url');
(async()=>{
 const macChrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
 const executablePath=process.env.DESIGN_CHROME_PATH||(fs.existsSync(macChrome)?macChrome:undefined);
 const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure().errorText));
  const modes=process.argv.slice(2);const report={errors,views:[]};
  for(const mode of modes.length?modes:['original','light','dark']){
   await page.setViewportSize({width:1440,height:1000});
   await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href+'?mode='+mode);
   await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(im=>im.decode()));});
   const type=await page.evaluate(()=>({headline:getComputedStyle(document.querySelector('h1')).fontFamily,body:getComputedStyle(document.querySelector('.description')).fontFamily,fonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+':'+f.weight)}));
   await page.locator('.hero').screenshot({path:path.join(__dirname,'hero-'+mode+'.png')});
   report.views.push({mode,width:1440,...type});
   if(mode!=='original'){
    // Inspect and record the composited background under the live text.
    const boxes=await page.evaluate(()=>Object.fromEntries(['h1','.description','.cta'].map(selector=>{const el=document.querySelector(selector),r=el.getBoundingClientRect(),h=document.querySelector('.hero').getBoundingClientRect(),s=getComputedStyle(el);return[selector,{x:r.x-h.x,y:r.y-h.y,width:r.width,height:r.height,color:s.color,background:s.backgroundColor}];})));
    fs.writeFileSync(path.join(__dirname,'boxes-'+mode+'.json'),JSON.stringify(boxes));
    await page.addStyleTag({content:'.hero-content,.site-nav,.scroll-note,.hero-number{visibility:hidden!important}'});
    await page.locator('.hero').screenshot({path:path.join(__dirname,'background-composite-'+mode+'.png')});
    await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href+'?mode='+mode);
    await page.setViewportSize({width:390,height:1000});
    await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(im=>im.decode()));});
    await page.locator('.hero').screenshot({path:path.join(__dirname,'hero-'+mode+'-mobile.png')});
    report.views.push(await page.evaluate(()=>({mode:document.documentElement.dataset.mode,width:innerWidth,scrollWidth:document.documentElement.scrollWidth})));
   }
  }
  fs.writeFileSync(path.join(__dirname,'render-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close();}
})();
