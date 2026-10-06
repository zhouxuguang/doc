import sys, re, json, shutil
from pathlib import Path
sys.path.insert(0,'/private/tmp/atmos-blog-deps')
from markdown_it import MarkdownIt
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'.article_tools/qa'
source=(ROOT/'预计算大气散射技术详解.md').read_text()
math=[]
def replace_math(segment):
    pattern=r'\$\$(.*?)\$\$|(?<!\$)\$(?!\$)([^\n$]+?)\$(?!\$)'
    def sub(m):
        display=m.group(1) is not None
        formula=m.group(1) if display else m.group(2)
        ident=len(math);math.append({'id':ident,'display':display,'tex':formula.strip()})
        return 'ATMOSMATH'+str(ident).zfill(6)+'END'
    return re.sub(pattern,sub,segment,flags=re.S)
parts=re.split(r'(^```[^\n]*\n.*?^```\s*$)',source,flags=re.M|re.S)
marked=''.join(p if p.startswith('```') else replace_math(p) for p in parts)
QA.joinpath('math_expressions.json').write_text(json.dumps(math,ensure_ascii=False))
QA.joinpath('article_body.html').write_text(MarkdownIt('commonmark',{'html':True}).enable('table').render(marked))
print('Math expressions:',len(math),'display:',sum(m['display'] for m in math))
