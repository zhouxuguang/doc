const fs=require('fs');const path=require('path');
const pkg='/private/tmp/atmos-blog-web/node_modules/mathjax-full/js/';
const {mathjax}=require(pkg+'mathjax.js');
const {TeX}=require(pkg+'input/tex.js');
const {SVG}=require(pkg+'output/svg.js');
const {liteAdaptor}=require(pkg+'adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require(pkg+'handlers/html.js');
const {AllPackages}=require(pkg+'input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const tex=new TeX({packages:AllPackages,tags:'ams'});
const document=mathjax.document('',{InputJax:tex,OutputJax:new SVG({fontCache:'none'})});
const out=path.join(__dirname,'qa','math_svg');fs.mkdirSync(out,{recursive:true});
const expressions=JSON.parse(fs.readFileSync(path.join(__dirname,'qa','math_expressions.json'),'utf8'));
let count=0;
for(const expr of expressions.filter(x=>x.display)){
 const node=document.convert(expr.tex.replace(/\\tag\{\d+\}/g,''),{display:true});
 const markup=adaptor.outerHTML(node);
 const svg=markup.match(/<svg[\s\S]*<\/svg>/)[0];
 const eq=expr.tex.match(/\\tag\{(\d+)\}/)[1];
 if(markup.includes('data-mjx-error'))throw new Error('Equation '+eq+' failed');
 fs.writeFileSync(path.join(out,'eq_'+eq.padStart(3,'0')+'.svg'),svg);count++;
}
console.log('SVG equations rendered:',count);
