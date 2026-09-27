# 三个目录的字段约定

三个 JSON 文件都采用 `{"schema_version": 1, "entries": []}`。以下仅为格式示例，不是已入库内容。

## 部件：components/index.json

```json
{
  "id": "cmp-0001",
  "name": "ム·独体",
  "source": "Source Han Sans Japanese / Regular / ム U+30E0 / 完整轮廓",
  "outline": "components/svg/cmp-0001.svg"
}
```

名称和来源是必填属性。来源应写明地区版、字重、源字符或字体内部字形名，以及完整提取还是局部截取。后续可以增加具体源字体路径、字形名、位置变体、修改记录等字段。

## 字形：glyphs/index.json

```json
{
  "id": "glyph-0001",
  "original": "能",
  "outline": "glyphs/svg/glyph-0001.svg",
  "component_ids": ["cmp-0001"]
}
```

原字为必填属性。`component_ids` 可省略或填空列表；填入时必须引用已有部件。`outline` 指向确认用于展示的字形图，不能指向 AI 文件、手稿照片或源字体。

## 字典：data/dictionary.json

```json
{
  "id": "entry-0001",
  "original": "能",
  "method": "意字",
  "idea": "此处填写经确认的造字思路。",
  "glyph_id": "glyph-0001"
}
```

原字、造字法、造字思路均必填。`glyph_id` 必须关联同一原字的已有字形。可为同一原字保留多条独立方案，不用原字本身作为唯一编号。

## 文件与坐标

- 所有路径相对项目根目录，推荐使用 `/`。
- 部件 SVG 放在 `components/svg/`，字形 SVG 放在 `glyphs/svg/`。
- 轮廓使用闭合填充路径，避免字体或外部图片依赖。
- 建议 SVG 采用统一的 `viewBox="0 0 1000 1000"`；字体坐标到 SVG 坐标的转换与基线位置将在首字制作时校准。
- 相同字重统一模板，不能随意将每张 SVG 按其轮廓边界自动缩放。
- 输入 JSON 可以附加其他信息；基础查询界面只展示约定字段。

入库顺序：保存部件轮廓与部件记录 → 保存字形轮廓与字形记录 → 保存字典记录 → 检查关联 → 刷新 GUI。
