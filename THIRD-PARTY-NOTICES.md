# Third-party notices / 第三方素材与署名

本文件记录 Aemeath / AM-01「Guiding Starlance」A380X 涂装所使用的第三方素材、处理方式及已有版权声明。记录日期：2026-11-06。

本项目为非官方同人涂装；不声称获得 KURO GAMES、FlyByWire Simulations、Microsoft 或 Airbus 的联名、认可或素材再许可。此文件不向第三方图像、机模、商标或字体授予新的许可；素材的原有权利和适用条款不因转换成 PNG、XCF 或 DDS 而改变。本仓库没有将所有内容统一授予 MIT、GPL 或其他通用许可。

## 1. KURO GAMES：《鸣潮》与爱弥斯 / Aemeath

《鸣潮 / Wuthering Waves》、爱弥斯 / Aemeath 的角色原画、机兵及相关官方视觉素材的权利归 KURO GAMES 及相应权利人所有。

最终涂装使用的两个角色构图来自《鸣潮》官方网站：

| 官方原件 | 原始尺寸 | 官方直接来源 | 本项目使用方式 |
| --- | --- | --- | --- |
| `aimisi-8ad56dae.webp` | 1200×1200 | [官网透明立绘](https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-8ad56dae.webp) | 左侧角色主视觉；使用透明蒙版柔化被原画画布截断的发丝边缘 |
| `aimisi-eb60fae0.webp` | 1300×1080 | [官网角色与机兵组合图](https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-eb60fae0.webp) | 右侧角色与机兵主视觉；轮廓蒙版去除外围背景，并镜像适配机身方向 |

角色原画通过 GIMP 解码、抠图、图层蒙版与排版处理；没有使用 AI 重绘角色或补造脸部细节。角色图像也存在于可编辑 XCF、投影图、最终 PNG/DDS、缩略图和预览中，这些派生文件仍包含上述第三方美术内容。

官方角色与文章出处：

- [《鸣潮》官网角色页](https://wutheringwaves.kurogames.com/en/main/role)
- [Post-Lament Anthropocene: Stars Intertwined | Aemeath](https://wutheringwaves.kurogames.com/en/main/news/detail/4134)
- [官网角色文章 4140](https://wutheringwaves.kurogames.com/en/main/news/detail/4140)

其他备选参考图、新闻图片和 CDN URL 的逐项记录见 [references/SOURCES.md](references/SOURCES.md)。这些链接用于追溯素材来源；本项目没有将“可从官网访问”表述为获得公开再分发授权，也没有给这些图像另加开放许可。

## 2. FlyByWire Simulations：A380X、paintkit 与派生成分

基础 A380X 飞机由 FlyByWire Simulations 及其贡献者制作。本涂装需要用户另行安装兼容的 A380X Stable 基础机模；安装包通过配置引用基础机模，不包含完整飞机模型、系统或声音。

实际制作使用官方 A380X paintkit 0.3 中的 `A380X_PAINTKIT_V0.3.psd` 与 `A380X_PAINTKIT.obj`。官方几何用于离线 UV 定位、投影烘焙和预览；仓库发布范围不包含原始 PSD、OBJ/FBX、打包了该几何的 Blender 工程或提取的 `.npz` 几何缓存。

本项目中仍含有 FBW 素材的导出或修改版本，包括：

- `artwork/clean-template/` 内从 paintkit 导出的机翼底色、步行区域标记及安全警示等图像。
- XCF、最终 PNG/DDS 中使用的这些模板成分；最终干净漆面没有叠加 paintkit 的污渍和擦痕图层。
- 驾驶舱编号贴图中保留的原始透明背景及 SELCAL 等标签；仅将机号文字改为虚构的 `B-38AM`。
- 使用官方 paintkit 几何生成的三维预览图片；这些是离线渲染，不是模拟器内截图。

来源与上游信息：

- [FlyByWire 官方网站](https://flybywiresim.com/)
- [FlyByWireOfficial 发布的 A380X Paint Kit 0.3](https://flightsim.to/addon/83825/a380x-paint-kit)
- [FlyByWire aircraft 上游仓库](https://github.com/flybywiresim/aircraft)
- [上游 LICENSE](https://github.com/flybywiresim/aircraft/blob/master/LICENSE)

paintkit 发布页要求通过官方渠道取得原始 paintkit，并禁止转载原始文件。本项目仅记录实际来源和派生使用方式，不将该要求改写为允许转载原始 paintkit，也不自行给其图形素材授予 MIT 或 GPL 许可。

`package/aemeath-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_Aemeath/model.AEMEATH/model.cfg` 保留了以下原有声明：

```ini
; Copyright (c) 2023-2024 FlyByWire Simulations
; SPDX-License-Identifier: GPL-3.0
```

该文件中的原有版权与许可标记应继续保留。它不为 KURO GAMES 角色图像或本项目中的全部图形成分另行指定许可。

## 3. 字体与制作工具

文字图层使用本机安装的 Arial、Arial Bold、Arial Bold Italic 与 Microsoft YaHei Bold 等字体。仓库保存可编辑文字图层及渲染结果，没有附带字体文件；重新编辑或生成文字时需要本机有相应字体，字体本身遵循其权利人的条款。

制作过程使用 GIMP 和 Blender；仓库不附带这些应用的可执行程序。工具名称仅用于说明制作流程，不表示工具开发者参与或背书本涂装。

## 4. 本项目新增内容与权利范围

本项目另行制作了涂装配色、星轨与电子装饰、文字排版、虚构机号 `B-38AM`、主题编号 `AM-01`、图层组织，以及制作、导出和校验脚本。这些新增内容与第三方原画、机模、模板成分应分别识别。

本文件是来源与署名说明，不是新增的通用代码许可或素材使用授权。已有文件级版权和许可声明继续适用；第三方商标及名称归各自权利人所有。
