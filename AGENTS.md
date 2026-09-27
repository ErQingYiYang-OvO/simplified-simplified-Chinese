# 本项目的制作约定

- 用户已明确：字形制作和调整阶段先只交付 Illustrator 导出的 SVG 草稿，放在 `glyphs/ai/drafts/`。
- 必须等用户明确确认该版满意后，才能写入字体、字典及正式字形和部件目录。不能把一次修改请求当作入库确认。
- 草稿阶段不生成 OTF、SFD 或正式 AI 文件，不覆盖 `glyphs/svg/`、`components/index.json`、`glyphs/index.json`、`data/dictionary.json` 或已有字体。可在 `build/` 放临时制作脚本和用于审阅的预览图。
- 原版思源黑体及许可证保持不变。简中版作为底板，简中和日文版共同提供部件。
- 造字法名称为意字、简字、拼字、俗字、借字。字形比例、线条调整必须遵循用户当前反馈。
- “能”已在用户手动调整第四版 SVG 并明确确认后入库。正式轮廓的依据为 `glyphs/versions/glyph-0001/v4-approved/user-confirmed.svg`，字体为 `releases/ZaiJianSans-Regular.otf`。不得运行旧部件拼装脚本覆盖用户定稿；后续修改仍先做 SVG 草稿，再等用户确认。
