const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const http=require('http'), fs=require('fs'), path=require('path'), assert=require('assert');
const root=__dirname;
const server=http.createServer((req,res)=>{
  const file=path.join(root,decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  fs.readFile(file,(err,data)=>{if(err){res.writeHead(404).end();return;}
    const types={'.html':'text/html; charset=utf-8','.css':'text/css','.jpg':'image/jpeg','.png':'image/png'};
    res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');res.end(data);
  });
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try {
    browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    const origin='http://127.0.0.1:'+server.address().port;
    await page.goto(origin+'/index.html');
    await page.getByRole('link',{name:'About me',exact:true}).click();
    await page.locator('.portrait img').evaluate(img=>img.decode());
    assert(await page.getByRole('heading',{level:1}).isVisible());
    assert(await page.locator('.portrait img').evaluate(img=>img.naturalWidth>0));
    await page.screenshot({path:path.join(root,'image-review/about-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(root,'image-review/about-mobile.png'),fullPage:true});
    await page.getByRole('link',{name:'Join the journey',exact:true}).click();
    assert(new URL(page.url()).pathname==='/index.html');
    assert(await page.getByRole('link',{name:'About me',exact:true}).isVisible());
    console.log('PASS: menu navigation, original photo loads, mobile has no horizontal overflow, journey link returns to stories.');
  } finally {if(browser)await browser.close();server.close();}
})().catch(err=>{console.error(err.message);process.exitCode=1;});
