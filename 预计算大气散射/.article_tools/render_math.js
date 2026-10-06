const fs=require('fs');
const path=require('path');
const katex=require('/private/tmp/atmos-blog-web/node_modules/katex');
const qa=path.join(__dirname,'qa');
const expressions=JSON.parse(fs.readFileSync(path.join(qa,'math_expressions.json'),'utf8'));
let html=fs.readFileSync(path.join(qa,'article_body.html'),'utf8');
const errors=[];
for(const expr of expressions){
  try{
    const rendered=katex.renderToString(expr.tex,{displayMode:expr.display,throwOnError:true,strict:'error',output:'htmlAndMathml'});
    html=html.replace('ATMOSMATH'+String(expr.id).padStart(6,'0')+'END',expr.display?'<div class="equation">'+rendered+'</div>':rendered);
  }catch(e){errors.push({id:expr.id,tex:expr.tex,error:String(e)});}
}
fs.writeFileSync(path.join(qa,'latex_validation.json'),JSON.stringify({count:expressions.length,errors},null,2));
const head=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>预计算大气散射技术详解</title>
<link rel="stylesheet" href="katex/katex.min.css"><style>
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;margin:42px auto;max-width:1080px;padding:0 30px;color:#233649;font-size:17px;line-height:1.85;background:#fff}
h1,h2,h3{line-height:1.45;color:#153f61}h1{font-size:34px}h2{margin-top:48px;border-bottom:1px solid #dce5ee;padding-bottom:10px}h3{margin-top:34px}
a{color:#1766a3}img{display:block;max-width:100%;height:auto;margin:25px auto}table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.65;display:block;overflow-x:auto}td,th{border:1px solid #dce5ee;padding:9px 13px}th{background:#eef5f9;text-align:left}
pre{background:#f2f5f8;padding:20px;border-radius:8px;line-height:1.55;overflow:auto;font-size:14px}code{font-family:Menlo,monospace}p>code,td>code{font-size:14px;background:#f1f5f7;padding:2px 4px;border-radius:3px}
.equation{overflow-x:auto;padding:15px 20px;margin:12px 0;background:#fafcfd}.katex{font-size:1.05em}.katex-display{margin:0.35em 0}em{color:#617484;font-style:normal}blockquote{border-left:4px solid #20a4c0;padding-left:20px;color:#486275}
table:has(img){display:table;table-layout:fixed;width:100%}table:has(img) td,table:has(img) th{width:50%;text-align:center}table:has(img) img{width:100%;margin:10px auto}
</style></head><body>`;
// Image links are relative to the article workspace; preview is two directories deeper.
html=html.replace(/src="atmosphere_scattering_images\//g,'src="../../atmosphere_scattering_images/');
html=html.replace(/href="(?!https?:|#|\/)([^"]+)"/g,'href="../../$1"');
fs.writeFileSync(path.join(qa,'article_preview.html'),head+html+'</body></html>');
console.log(JSON.stringify({expressions:expressions.length,errors:errors.length,firstErrors:errors.slice(0,4)},null,2));
process.exitCode=errors.length?1:0;
