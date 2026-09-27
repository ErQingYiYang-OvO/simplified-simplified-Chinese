"""Reproducible outline extraction and pristine-base rebuild for the first draft."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib.tables.DefaultTable import DefaultTable
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sources/09_SourceHanSansSC/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf'
WORK = ROOT / 'build/neng-0001'


def svg_for(glyph, glyphs):
    pen = SVGPathPen(glyphs)
    glyph.draw(pen)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><g transform="translate(0 880) scale(1 -1)"><path fill="#202720" d="' + pen.getCommands() + '"/></g></svg>'


def extract():
    font = TTFont(BASE)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    for code, name in [(0x80FD, 'neng'), (0x529B, 'li')]:
        (WORK / ('original-' + name + '.svg')).write_text(svg_for(glyphs[cmap[code]], glyphs), encoding='utf-8')
    recording = RecordingPen()
    glyphs[cmap[0x80FD]].draw(recording)
    contours, current = [], []
    for command in recording.value:
        current.append(command)
        if command[0] in ('closePath', 'endPath'):
            contours.append(current)
            current = []
    selected = []
    bounds = []
    for index, contour in enumerate(contours):
        pen = BoundsPen(glyphs)
        for operation, args in contour:
            getattr(pen, operation)(*args)
        if pen.bounds[2] < 520 and pen.bounds[1] > 500:
            selected.append(index)
            bounds.append(pen.bounds)
    if len(selected) != 1:
        raise RuntimeError('Upper-left component must resolve to one original contour')
    path = SVGPathPen(glyphs)
    for operation, args in contours[selected[0]]:
        getattr(path, operation)(*args)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><g transform="translate(0 880) scale(1 -1)"><path fill="#202720" d="' + path.getCommands() + '"/></g></svg>'
    (ROOT / 'components/svg/cmp-0001.svg').write_text(svg, encoding='utf-8')
    (ROOT / 'components/svg/cmp-0002.svg').write_text(svg_for(glyphs[cmap[0x529B]], glyphs), encoding='utf-8')
    (WORK / 'extraction.json').write_text(json.dumps({'top_contour_indices': selected, 'top_bounds': bounds, 'top_glyph_name': cmap[0x80FD], 'bottom_glyph_name': cmap[0x529B]}, indent=2), encoding='utf-8')
    print('Original components extracted without altering source font')


def finalize(approved_svg=None):
    registered = json.loads((ROOT / 'glyphs/index.json').read_text(encoding='utf-8-sig'))['entries']
    if any(item.get('original') != '能' and item.get('status') == '用户确认' for item in registered):
        raise RuntimeError('Use font_tools/build_approved.py to preserve every approved glyph.')
    if not approved_svg:
        entries = json.loads((ROOT / 'data/dictionary.json').read_text(encoding='utf-8-sig'))['entries']
        if any(item.get('original') == '\u80fd' and item.get('status') == '\u7528\u6237\u786e\u8ba4' for item in entries):
            raise RuntimeError('User-confirmed outline cannot be overwritten by an old donor. Submit a new SVG draft for approval.')
    if approved_svg:
        approved_svg = Path(approved_svg).resolve()
        tree = ET.parse(approved_svg)
        group = tree.getroot().find('{http://www.w3.org/2000/svg}g')
        if group is None or group.get('transform') != 'translate(0 880) scale(1 -1)':
            raise RuntimeError('Approved SVG coordinate system requires review')
        paths = list(group.findall('{http://www.w3.org/2000/svg}path'))
        if len(paths) != 2 or any(path.get('transform') for path in paths):
            raise RuntimeError('Approved SVG structure requires review')

        class ApprovedOutline:
            def draw(self, pen):
                for path in paths:
                    parse_path(path.attrib['d'], pen)

        donor_name = 'approved'
        donor_glyphs = {donor_name: ApprovedOutline()}
        shutil.copyfile(approved_svg, ROOT / 'glyphs/svg/glyph-0001.svg')
    else:
        donor = TTFont(WORK / 'neng-donor.otf')
        donor_glyphs = donor.getGlyphSet()
        donor_name = donor.getBestCmap()[0x80FD]
        svg = svg_for(donor_glyphs[donor_name], donor_glyphs)
        (ROOT / 'glyphs/svg/glyph-0001.svg').write_text(svg, encoding='utf-8')
    font = TTFont(BASE, recalcBBoxes=False, recalcTimestamp=False)
    glyph_name = font.getBestCmap()[0x80FD]
    top = font['CFF '].cff.topDictIndex[0]
    original = top.CharStrings[glyph_name]
    pen = T2CharStringPen(font['hmtx'][glyph_name][0], font.getGlyphSet())
    donor_glyphs[donor_name].draw(pen)
    replacement = pen.getCharString(private=original.private, globalSubrs=font['CFF '].cff.GlobalSubrs)
    slot = top.CharStrings.charStrings[glyph_name]
    top.CharStrings.charStringsIndex.items[slot] = replacement
    bbox = BoundsPen(donor_glyphs)
    donor_glyphs[donor_name].draw(bbox)
    font['hmtx'][glyph_name] = (1000, round(bbox.bounds[0]))
    family = 'ZaiJian Sans' if approved_svg else 'ZaiJian Sans Draft'
    ps = 'ZaiJianSans-Regular' if approved_svg else 'ZaiJianSansDraft-Regular'
    names = {1: family, 2: 'Regular', 3: '0.001;ZJ;'+ps, 4: family, 6: ps, 16: family, 17: 'Regular'}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    for key, value in names.items():
        font['name'].setName(value, key, 3, 1, 0x409)
    font['CFF '].cff.fontNames[0] = ps
    top.FamilyName = family
    top.FullName = family
    raw_cmap = DefaultTable('cmap')
    raw_cmap.data = font.reader['cmap']
    font['cmap'] = raw_cmap
    output = ROOT / 'releases/ZaiJianSans-Regular.otf' if approved_svg else WORK / 'ZaiJianSansDraft-Regular.otf'
    font.save(output)
    candidate = TTFont(output)
    clean = TTFont(BASE)
    preserved = ('cmap', 'hhea', 'vhea', 'OS/2', 'GDEF', 'GPOS', 'GSUB', 'VORG', 'vmtx')
    checks = {tag: clean.getTableData(tag) == candidate.getTableData(tag) for tag in preserved}
    checks['all_advance_widths'] = all(clean['hmtx'][name][0] == candidate['hmtx'][name][0] for name in clean.getGlyphOrder())
    checks['glyph_order'] = clean.getGlyphOrder() == candidate.getGlyphOrder()
    modified = []
    old_cs = clean['CFF '].cff.topDictIndex[0].CharStrings
    new_cs = candidate['CFF '].cff.topDictIndex[0].CharStrings
    for name in clean.getGlyphOrder():
        old_cs[name].compile()
        new_cs[name].compile()
        if old_cs[name].bytecode != new_cs[name].bytecode:
            modified.append(name)
    checks['only_neng_outline_changed'] = modified == [glyph_name]
    candidate_glyphs = candidate.getGlyphSet()
    candidate_box = BoundsPen(candidate_glyphs)
    candidate_glyphs[glyph_name].draw(candidate_box)
    checks['outline_bounds_match'] = all(abs(a-b) < 0.01 for a,b in zip(bbox.bounds, candidate_box.bounds))
    audit = {'checks': checks, 'modified_charstrings': modified, 'bounds': bbox.bounds, 'review_status': 'user_confirmed' if approved_svg else 'draft_for_user_review'}
    audit_path = ROOT / 'releases/neng-0001-audit.json' if approved_svg else WORK / 'audit.json'
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    if not all(checks.values()):
        raise RuntimeError('Font audit failed: ' + str(checks))
    print('Draft font reconstructed and preservation audit passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['extract', 'finalize'])
    parser.add_argument('--approved-svg', help='User-confirmed Illustrator SVG; requires explicit user approval')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.stage == 'extract':
        extract()
    else:
        finalize(args.approved_svg)
