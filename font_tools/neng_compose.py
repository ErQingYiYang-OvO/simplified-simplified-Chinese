"""Run using FontForge's Python. Compose the review draft using source outlines."""
import fontforge
import psMat
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'data/dictionary.json').read_text(encoding='utf-8-sig'))
if any(item.get('original') == '\u80fd' and item.get('status') == '\u7528\u6237\u786e\u8ba4' for item in catalog['entries']):
    raise RuntimeError('Legacy composition is disabled for the confirmed glyph. Create a new SVG draft for review.')
font = fontforge.font()
font.encoding = 'UnicodeFull'
font.ascent = 880
font.descent = 120
font.fontname = 'ZaiJianNengDonor-Regular'
font.familyname = 'ZaiJian Neng Donor'
font.fullname = 'ZaiJian Neng Donor Regular'
upper = font.createChar(0xE000, 'neng.upper')
lower = font.createChar(0xE001, 'neng.lower')
upper.importOutlines(str(ROOT / 'components/svg/cmp-0003.svg'), scale=False)
lower.importOutlines(str(ROOT / 'components/svg/cmp-0002.svg'), scale=False)
if not upper.isWorthOutputting() or not lower.isWorthOutputting():
    raise RuntimeError('Component SVG import produced an empty outline')
lower.transform(psMat.scale(0.58))
lower.changeWeight(24, 'auto', 0, 0, 'retain')
lower.removeOverlap()
lower.autoHint()
lower.condenseExtend(2.40, 0, 1, 0, False)
pre_flatten = lower.boundingBox()
lower.transform(psMat.scale(1, 460 / (pre_flatten[3] - pre_flatten[1])))
lower.changeWeight(10, 'auto', 0, 0, 'retain')
lower.removeOverlap()
pre_fit = lower.boundingBox()
fit_x = 890 / (pre_fit[2] - pre_fit[0])
fit_y = 460 / (pre_fit[3] - pre_fit[1])
lower.transform(psMat.scale(fit_x, fit_y))
upper_before = upper.boundingBox()
lower_before = lower.boundingBox()
upper_dx = 500 - (upper_before[0]+upper_before[2])/2
upper_dy = 835 - upper_before[3]
upper.transform(psMat.translate(upper_dx, upper_dy))
upper_bounds = upper.boundingBox()
lower_dx = 500 - (lower_before[0]+lower_before[2])/2
lower_dy = upper_bounds[1] - 10 - lower_before[3]
lower.transform(psMat.translate(lower_dx, lower_dy))
target = font.createChar(0x80FD, 'uni80FD')
target.foreground = upper.foreground + lower.foreground
target.width = 1000
target.vwidth = 1000
target.correctDirection()
target.addExtrema()
target.round()
validation = target.validate(True)
recipe = {
    'glyph_id': 'glyph-0001', 'original': '\u80fd', 'structure': 'top-bottom',
    'units_per_em': 1000, 'ascent': 880, 'descent': 120,
    'revision': 3,
    'upper': {'component_id': 'cmp-0003', 'manual_curve_refinement': True, 'target_height': 420, 'translate': [upper_dx, upper_dy]},
    'lower': {'component_id': 'cmp-0002', 'scale': 0.58, 'weight_compensation': 24, 'counter_extension': 2.40, 'flatten_target_height': 460, 'flatten_weight_compensation': 10, 'final_fit': [fit_x, fit_y], 'translate': [lower_dx, lower_dy]},
    'gap': 10, 'width': 1000, 'validation_flags': validation,
    'bounds': target.boundingBox(), 'visible_frame': [890, 890], 'status': 'draft_for_user_review'
}
box = target.boundingBox()
if abs((box[2]-box[0])-(box[3]-box[1])) > 1:
    raise RuntimeError('Visible glyph frame must be square')
if validation:
    raise RuntimeError('Outline validation failed: ' + str(validation))
font.save(str(ROOT / 'fontforge/neng-0001.sfd'))
font.generate(str(ROOT / 'build/neng-0001/neng-donor.otf'))
(ROOT / 'glyphs/recipes/glyph-0001.json').write_text(json.dumps(recipe, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(recipe, ensure_ascii=True))
