"""Rebuild the base font using every registered user-approved SVG."""
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.DefaultTable import DefaultTable
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sources/09_SourceHanSansSC/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf'


class Outline:
    def __init__(self, path):
        group = ET.parse(path).getroot().find('{http://www.w3.org/2000/svg}g')
        if group is None or group.get('transform') != 'translate(0 880) scale(1 -1)':
            raise ValueError('Unsupported approved SVG coordinates')
        self.paths = group.findall('{http://www.w3.org/2000/svg}path')
        if not self.paths or any(p.get('transform') for p in self.paths):
            raise ValueError('Unsupported approved SVG paths')

    def draw(self, pen):
        for path in self.paths:
            # These rectangular stems run opposite to the サ-derived bar.
            # SVG displays their union, whereas opposite CFF winding cuts holes.
            # Reverse traversal only; all points and the approved SVG stay intact.
            target = ReverseContourPen(pen) if path.get('id') in ('left-short-vertical', 'right-long-vertical') else pen
            parse_path(path.get('d'), target)


def build():
    records = json.loads((ROOT / 'glyphs/index.json').read_text(encoding='utf-8'))['entries']
    font = TTFont(BASE, recalcBBoxes=False, recalcTimestamp=False)
    top = font['CFF '].cff.topDictIndex[0]
    originals = font.getGlyphSet()
    expected, bounds = [], {}
    for record in records:
        if record.get('status') != '用户确认':
            continue
        path = ROOT / record['approved_source']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record['approved_svg_sha256'] or (ROOT / record['outline']).read_bytes() != path.read_bytes():
            raise ValueError('Approved SVG provenance mismatch: ' + record['id'])
        name = font.getBestCmap()[ord(record['original'])]
        if name in expected:
            raise ValueError('Duplicate approved character')
        outline = Outline(path)
        old = top.CharStrings[name]
        pen = T2CharStringPen(font['hmtx'][name][0], originals, roundTolerance=0)
        outline.draw(pen)
        replacement = pen.getCharString(private=old.private, globalSubrs=font['CFF '].cff.GlobalSubrs)
        top.CharStrings.charStringsIndex.items[top.CharStrings.charStrings[name]] = replacement
        box = BoundsPen(None)
        outline.draw(box)
        bounds[name] = box.bounds
        font['hmtx'][name] = (font['hmtx'][name][0], round(box.bounds[0]))
        expected.append(name)
    names = {1:'ZaiJian Sans',2:'Regular',3:'0.002;ZJ;ZaiJianSans-Regular',4:'ZaiJian Sans',6:'ZaiJianSans-Regular',16:'ZaiJian Sans',17:'Regular'}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    for key, value in names.items():
        font['name'].setName(value,key,3,1,0x409)
    font['CFF '].cff.fontNames[0] = 'ZaiJianSans-Regular'
    top.FamilyName = top.FullName = 'ZaiJian Sans'
    cmap = DefaultTable('cmap')
    cmap.data = font.reader['cmap']
    font['cmap'] = cmap
    candidate_path = ROOT / 'build/approved-candidate.otf'
    font.save(candidate_path)
    candidate, clean = TTFont(candidate_path), TTFont(BASE)
    preserved = ('cmap','hhea','vhea','OS/2','GDEF','GPOS','GSUB','VORG','vmtx')
    checks = {tag: clean.getTableData(tag)==candidate.getTableData(tag) for tag in preserved}
    checks['all_advance_widths'] = all(clean['hmtx'][n][0]==candidate['hmtx'][n][0] for n in clean.getGlyphOrder())
    checks['glyph_order'] = clean.getGlyphOrder()==candidate.getGlyphOrder()
    modified = []
    for name in clean.getGlyphOrder():
        a = clean['CFF '].cff.topDictIndex[0].CharStrings[name]
        b = candidate['CFF '].cff.topDictIndex[0].CharStrings[name]
        a.compile(); b.compile()
        if a.bytecode != b.bytecode:
            modified.append(name)
    checks['only_approved_outlines_changed'] = set(modified)==set(expected)
    checks['approved_bounds_match'] = True
    for name, expected_box in bounds.items():
        box = BoundsPen(candidate.getGlyphSet())
        candidate.getGlyphSet()[name].draw(box)
        checks['approved_bounds_match'] &= all(abs(a-b)<0.02 for a,b in zip(expected_box,box.bounds))
    if not all(checks.values()):
        raise RuntimeError(checks)
    output = ROOT / 'releases/ZaiJianSans-Regular.otf'
    output.write_bytes(candidate_path.read_bytes())
    audit = {'checks':checks,'modified_charstrings':modified,'approved_bounds':bounds,'font_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'review_status':'user_confirmed'}
    (ROOT / 'releases/approved-font-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False))


if __name__ == '__main__':
    build()
