// Local-only UI harness. Stubs auth and microphone; never a production/session check.
const path=require('node:path'), fs=require('node:fs'), http=require('node:http'), os=require('node:os');
const webpack=require('../../Build/web/node_modules/next/dist/compiled/webpack/webpack').webpack;
const out=path.join(os.tmpdir(),'n74-ui');
const root=path.resolve(__dirname,'../../Build/web');
webpack({mode:'development',entry:path.join(__dirname,'entry.jsx'),output:{path:out,filename:'ui.js'},resolve:{extensions:['.js','.jsx','.mjs'],modules:[path.join(root,'node_modules'),'node_modules'],alias:{'@clerk/nextjs$':path.join(__dirname,'clerk-fixture.jsx'),'next/link$':path.join(__dirname,'link-fixture.jsx')}},module:{rules:[{test:/\.jsx$/,use:path.join(__dirname,'jsx-loader.cjs')}]},devtool:false},(err,stats)=>{
 if(err||stats.hasErrors()){console.error(err||stats.toString({all:false,errors:true}));process.exit(1);}
 http.createServer((req,res)=>{ if(req.url==='/ui.js'){res.setHeader('content-type','text/javascript');res.end(fs.readFileSync(path.join(out,'ui.js')));}
 else if(req.url==='/styles.css'){res.setHeader('content-type','text/css');res.end(fs.readFileSync(path.join(root,'src/app/styles.css')));}
 else if(req.url==='/workspace.css'){res.setHeader('content-type','text/css');res.end(fs.readFileSync(path.join(root,'src/workspace/workspace.css')));}
 else if(req.url==='/editor.css'){res.setHeader('content-type','text/css');res.end(fs.readFileSync(path.join(root,'src/lab-editor/lab-editor.css')));}
 else if(['/brand/mark.svg','/brand/mark-dark.svg'].includes(req.url)){res.setHeader('content-type','image/svg+xml');res.end(fs.readFileSync(path.join(root,'public',req.url)));}
 else{res.setHeader('content-type','text/html');res.end('<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/workspace.css"><link rel="stylesheet" href="/editor.css"></head><body><div id="root"></div><script src="/ui.js"></script></body></html>');}
 }).listen(3175,'127.0.0.1',()=>console.log('UI fixture http://localhost:3175/?signed=1'));
});
