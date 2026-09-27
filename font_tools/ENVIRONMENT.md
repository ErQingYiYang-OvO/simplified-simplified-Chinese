# 工具可用性检查

检查日期：2026-09-27。工具路径与版本见 `environment.json`。

## 已通过

- Illustrator 2026（30.8.1）成功启动，可通过脚本创建矢量图、保存 AI、导出 SVG。
- FontForge 20251009 可运行 Python 脚本，已分别从简中 Regular 提取“能”、从日文 Regular 提取“ム”的轮廓。
- Illustrator 测试 SVG 已成功导入 FontForge，保存为 SFD，生成 OTF 并重新打开确认存在轮廓。
- 测试文件仅保存于 `build/tool_check/`，没有加入部件、字形或字典目录。
- 检查期间源字体与许可证的 16 个校验记录均通过。

## 后续操作约定

优先使用 Illustrator 脚本与 FontForge Python 接口完成制作。Illustrator 原生窗口截图接口目前返回兼容错误，尚未验证鼠标操作链路；脚本制作接口已实际验证。

思源黑体是 CID 字体，Unicode 提取要先在内存副本上处理 CID 结构。此次检测发现 FontForge 对 CID 字体对象的关闭存在字形生命周期错误；临时验证脚本采用保留字体对象到进程结束的方式完成。

FontForge 导入时会忽略 DSIG、VORG 表，因此本次临时测试字体仅用于验证工具链。实际发行字体须从原版底板整合轮廓，并独立验证编码、度量与排版表。

FontForge 初始化会写入用户目录中的插件配置。在受限环境调用时可能需要额外执行权限。
