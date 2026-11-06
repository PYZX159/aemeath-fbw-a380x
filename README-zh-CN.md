# 爱弥斯 / AEMEATH — AM-01

《鸣潮》爱弥斯主题 FlyByWire A380X 虚构涂装。珍珠白机首、深靛蓝后机身与尾翼，樱粉/冰青流线、星轨纹章。左右使用不同官方角色构图，采用无污渍、无掉漆的干净漆面。

## 安装

1. 退出 MSFS 2024。
2. 把工作区根部完整的 `aemeath-fbw-a380x-stable` 文件夹复制至当前实际启用的 Community 目录。
3. 文件夹根部应直接包含 `manifest.json`、`layout.json` 和 `SimObjects`。
4. 选择 FBW A380X 涂装：**Aemeath / AM-01 - Guiding Starlance B-38AM**。

兼容本机已安装的非模块化 **FlyByWire A380X Stable 2024.1.0**。沿用国航涂装已在用户游戏中验证能加载的独立变体结构。所有定制 DDS 均带同名 `.DDS.json` 描述文件，并加入 `layout.json`。

## 身份元素

| 位置 | 内容 |
|---|---|
| 机身两侧、左翼下、驾驶舱铭牌 | 虚构机号 B-38AM |
| 机首和副标题 | AM-01 / GUIDING STARLANCE |
| 前起落架舱门 | AM / 01 |
| 发动机 | 01 左外、02 左内、03 右内、04 右外 |
| 主题 ATC 名称 | AEMEATH，航班号 001 |

保留驾驶舱原 SELCAL、机翼安全区域和步行标记、门框及模型面板细节。

## 可编辑源文件

- `artwork/projection/*.xcf`：两侧构图及发动机、翼尖、编号的 GIMP 分层母版。
- `artwork/source/`：角色蒙版、驾驶舱注册号源文件。
- `artwork/xcf/*.xcf`：最终 13 张 UV 贴图的 GIMP 源文件。
- `artwork/final/*.PNG`：最终贴图 PNG。
- `preview/`：真实 paintkit 几何的最终 PNG 预览。
- `references/SOURCES.md`：角色素材下载地址与来源。

制作通过 GIMP 后台脚本完成，不使用屏幕控制。Blender 用于真实 UV 投影与三维位置检查。

## 校验

`Update-PackageLayout.ps1` 为 13 张 DDS 生成描述文件并更新索引；`Validate-Package.ps1` 只读检查包内容、尺寸、格式、完整 mipmap 和本机基础机模引用。

预览是模型渲染，并非模拟器截图；独立涂装仍需要在游戏内试装确认。
