"""Render the released font itself for review."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
base = root/'sources/09_SourceHanSansSC/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf'
release = root/'releases/ZaiJianSans-Regular.otf'
image = Image.new('RGB',(1100,790),'white')
draw = ImageDraw.Draw(image)
label = ImageFont.truetype(str(base),28)
draw.text((45,25),'是 · 用户确认版',font=label,fill='#202720')
for x,title,path in [(45,'原字',base),(585,'新字',release)]:
    draw.text((x,90),title,font=label,fill='#52624c')
    draw.text((x,590),'是',font=ImageFont.truetype(str(path),470),anchor='ls',fill='#202720')
    draw.text((x,645),'是非  是否  不是  能力',font=ImageFont.truetype(str(path),36),fill='#202720')
draw.text((45,735),'意字：系绳于树的联想；结构与“为”相似',font=label,fill='#52624c')
image.save(root/'proofs/shi-0002-approved.png')
