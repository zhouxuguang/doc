import sys, re
from pathlib import Path
sys.path.insert(0,'/private/tmp/atmos-blog-deps')
import pymupdf as fitz
from PIL import Image,ImageDraw
qa=Path(__file__).resolve().parent/'qa'
files=sorted((qa/'math_svg').glob('*.svg'))
for batch in range((len(files)+7)//8):
    sheet=Image.new('RGB',(2200,1200),'white')
    for j,src in enumerate(files[batch*8:(batch+1)*8]):
        svg=src.read_text().replace('currentColor','#172c40')
        vb=re.search(r'viewBox="([^"]+)"',svg).group(1).split();vw,vh=float(vb[2]),float(vb[3])
        width=min(1040,vw*.022);height=width*vh/vw
        if height>246:width*=246/height;height=246
        svg=re.sub(r'width="[^"]+"',f'width="{width}px"',svg,count=1)
        svg=re.sub(r'height="[^"]+"',f'height="{height}px"',svg,count=1)
        doc=fitz.open(stream=svg.encode(),filetype='svg')
        pdf=fitz.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        x=(j%2)*1100;y=(j//2)*300
        sheet.paste(im,(x+(1100-im.width)//2,y+(280-im.height)//2))
        ImageDraw.Draw(sheet).text((x+20,y+12),src.stem,fill='#1766a3')
        ImageDraw.Draw(sheet).line((x,y+297,x+1090,y+297),fill='#dce5ee')
    sheet.save(qa/f'formula_sheet_{batch+1:02}.png')
print('Formula contact sheets:',(len(files)+7)//8)
