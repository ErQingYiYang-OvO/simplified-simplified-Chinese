# 本项目的制作约定

- 用户已明确：字形制作和调整阶段先只交付 Illustrator 导出的 SVG 草稿，放在 `glyphs/ai/drafts/`。
- 必须等用户明确确认该版满意后，才能写入字体、字典及正式字形和部件目录。不能把一次修改请求当作入库确认。
- 草稿阶段不生成 OTF、SFD 或正式 AI 文件，不覆盖 `glyphs/svg/`、`components/index.json`、`glyphs/index.json`、`data/dictionary.json` 或已有字体。可在 `build/` 放临时制作脚本和用于审阅的预览图。
- 原版思源黑体及许可证保持不变。简中版作为底板，简中和日文版共同提供部件。
- 造字法名称为意字、简字、拼字、俗字、借字。字形比例、线条调整必须遵循用户当前反馈。
- “能”已在用户手动调整第四版 SVG 并明确确认后入库。正式轮廓的依据为 `glyphs/versions/glyph-0001/v4-approved/user-confirmed.svg`，字体为 `releases/ZaiJianSans-Regular.otf`。不得运行旧部件拼装脚本覆盖用户定稿；后续修改仍先做 SVG 草稿，再等用户确认。
- “是”第二版经用户手动微调并确认后入库，依据为 `glyphs/versions/glyph-0002/v2-approved/user-confirmed.svg`。发行字体必须使用 `font_tools/build_approved.py` 从源字体加载所有确认条目重建，不能用仅处理“能”的旧脚本覆盖发行字体。
- “意”第一版经用户确认后入库，造字法为借字，直接使用简中思源黑体 Regular 的“义”完整轮廓，依据为 `glyphs/versions/glyph-0003/v1-approved/user-confirmed.svg`。编码仍为“意” U+610F，原字“义”保持不变。
- “等”第一版经用户确认后入库，造字法为俗字；横画与左短竖、右直长竖相交，右侧不带弯钩。依据为 `glyphs/versions/glyph-0004/v1-approved/user-confirmed.svg`，来源说明采用用户提供的草书楷化及数学课堂用法。
- 用户对“微”“算”“数”三个借字明确授权原样借用并直接入库，无需另行审阅。“微”借用简中 Regular 的“匕”，“算”完整借用已确认“等”新字形，“数”借用日文 Regular 的“ス”。分别为 glyph-0005、glyph-0006、glyph-0007，原字编码保持不变；此授权针对这三个字，后续字形仍遵循 SVG 草稿确认流程。
- “有”（glyph-0008）经用户授权直接入库，无需另行审阅，造字法为俗字，原样使用简中思源黑体 Regular 的“友”完整轮廓；来源为用户提供的2025年秋季线性代数B课堂书写习惯。原字编码保持不变。
- “得”（glyph-0009）第二版经用户批准后入库，造字法为借字，上工下儿，联想自「得る」的读音「エル」。用户先微调第一版，再将儿的两笔收近，正式依据为 `glyphs/versions/glyph-0009/v2-approved/user-confirmed.svg`；不得用初始拼装脚本覆盖定稿。
- “性”（glyph-0010）第一版经用户批准后入库，造字法为意字，左竖心旁右人，思路为“性，人心也”。依据为 `glyphs/versions/glyph-0010/v1-approved/user-confirmed.svg`；竖心旁来自原字性，右人来自从的右部，保留原笔画粗细。
