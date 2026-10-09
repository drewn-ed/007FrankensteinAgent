const {chromium}=require('playwright');
const path=require('node:path');
const fs=require('node:fs');
const {pathToFileURL}=require('node:url');
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('requestfailed',request=>errors.push(request.url()+': '+request.failure().errorText));
    await page.goto(pathToFileURL(path.join(__dirname,'preview.html')).href);
    await page.evaluate(()=>document.fonts.ready);
    const fonts=await page.evaluate(()=>[...document.fonts].filter(font=>font.status==='loaded').map(font=>({family:font.family,weight:font.weight,status:font.status})));
    await page.screenshot({path:path.join(__dirname,'preview.png'),fullPage:true});
    await page.getByRole('button',{name:'Dark',exact:true}).click();
    await page.locator('.concept').screenshot({path:path.join(__dirname,'preview-dark.png')});
    await page.getByRole('button',{name:'One colour',exact:true}).click();
    const mono=await page.locator('#lockup').evaluate(el=>el.classList.contains('mono'));
    await page.getByRole('button',{name:'Wing: on',exact:true}).click();
    const noWing=await page.locator('body').evaluate(el=>el.classList.contains('no-wing'));
    await page.getByRole('button',{name:'Wing: off',exact:true}).click();
    await page.getByRole('button',{name:'Light',exact:true}).click();
    const layouts=[];
    for(const width of [1440,760,390]){
      await page.setViewportSize({width,height:1100});
      layouts.push(await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})));
    }
    const report={fonts,errors,mono,noWing,layouts};
    fs.writeFileSync(path.join(__dirname,'preview-check.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await browser.close();}
})();
