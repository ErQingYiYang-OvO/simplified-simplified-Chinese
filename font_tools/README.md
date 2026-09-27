# 字体制作工具

这里保存源字形提取、部件拼装、原版字体重建及排版审计工具，均为重置后新建。

制作阶段以干净的简中源字体为底板，只替换指定字形，并检查字体名称、编码、字宽、行距及布局表。

## 首字“能”的脚本

- `neng_first_glyph.py extract`：使用 fontTools 提取原字左上轮廓和“力”。
- `neng_compose.py`：通过 FontForge 主程序拼装上下结构，保存 SFD、donor OTF 和配方。
- `neng_first_glyph.py finalize`：移植轮廓到干净原版，只替换“能”，保存测试字体及审计记录。
- `neng_proof.py`：用实际字体生成单字图及新旧对照样张。

提取、重建、样张脚本使用本机 Python313（安装 fontTools 4.61.0、Pillow）；GUI 和目录查询仍无需额外库。字体拼装使用 `environment.json` 中 FontForge 主程序的 `-lang=py -script` 接口。此次发现独立 `ffpython.exe` 在该环境的 SVG 导入失败，不用它进行轮廓导入。

首字 SVG 统一采用 1000×1000 字框，字体坐标转换为 `translate(0 880) scale(1 -1)`。AI 工作文件由当前 SVG 在 Illustrator 中保存，SVG 与配方是当前第一版的轮廓依据。未来在 AI 中修改后应同步导出 SVG，并更新配方或将修改后的 SVG 指定为新轮廓依据。
