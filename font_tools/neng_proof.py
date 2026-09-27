"""Render the actual base and reconstructed fonts as review images."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--previous', action='store_true')
parser.add_argument('--revision', type=int, default=3)
parser.add_argument('--compare-to', type=int)
parser.add_argument('--approved', action='store_true')
args = parser.parse_args()

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sources/09_SourceHanSansSC/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf'
DRAFT = ROOT / 'build/neng-0001/ZaiJianSansDraft-Regular.otf'
if args.approved:
    DRAFT = ROOT / 'releases/ZaiJianSans-Regular.otf'
image = Image.new('RGB', (1500, 1150), '#f7f8f4')
draw = ImageDraw.Draw(image)
font = lambda size, path=BASE: ImageFont.truetype(str(path), size)
draw.text((70, 45), '能 · 用户确认版' if args.approved else ('能 · 第三版调整' if args.revision == 3 else '能 · 第二版调整'), font=font(44), fill='#233c2b')
draw.text((70, 110), '上下结构   /   意字   /   思源黑体 Regular', font=font(24), fill='#72806e')
prior_revision = args.compare_to or 1
comparing = args.previous or args.compare_to is not None
previous = ROOT / f'build/neng-0001/v{prior_revision}/ZaiJianSansDraft-Regular.otf'
left = previous if comparing else BASE
for x, caption, path in [(80, '调整前' if comparing else '原字', left), (810, '新字形 · 已确认' if args.approved else '调整后 · 待审阅', DRAFT)]:
    draw.text((x, 180), caption, font=font(27), fill='#52624c')
    draw.rounded_rectangle((x, 230, x+600, 830), radius=10, fill='white', outline='#dbe2d4', width=2)
    for delta in (300,):
        draw.line((x+delta, 230, x+delta, 830), fill='#e5eadf', width=1)
        draw.line((x, 230+delta, x+600, 230+delta), fill='#e5eadf', width=1)
    draw.text((x+40, 750), '能', font=font(520, path), anchor='ls', fill='#202720')
    draw.text((x, 885), '能力  能量  用力  做功', font=font(43, path), fill='#202720')
    draw.text((x, 970), ('采用用户手动微调的定稿轮廓' if args.approved else '可见外框 890 × 890，上部提高、下部压扁') if path == DRAFT else (f'第 {prior_revision} 版轮廓' if comparing else '未改动的原版轮廓'), font=font(23), fill='#74826d')
    if path == DRAFT:
        draw.text((x, 1010), '下部选用“力”，记录能力与能量的联想', font=font(22), fill='#74826d')
image.save(ROOT / ('proofs/neng-0001-approved.png' if args.approved else (f'proofs/neng-0001-v{prior_revision}-v{args.revision}.png' if comparing else 'proofs/neng-0001-comparison.png')))
single = Image.new('RGB', (1000,1000), 'white')
ImageDraw.Draw(single).text((0,880), '能', font=font(1000,DRAFT), anchor='ls', fill='#202720')
single.save(ROOT / 'proofs/neng-0001-glyph.png')
