# 爱弥斯 Aemeath：官方视觉素材来源

采集日期：2026-11-06。下载原件与旧项目分开保存。原图版权归 KURO GAMES；本文仅记录实际出处和处理方式，不声明获得公开再分发授权。

## 角色确认与视觉

- 英文名 **Aemeath**。官网文章《Post-Lament Anthropocene: Stars Intertwined | Aemeath》及其主视觉直接印有 `AEMEATH`、`Digital Ghost`。
- 官方出处：https://wutheringwaves.kurogames.com/en/main/news/detail/4134 ，日期 2026-01-31。
- 官方角色简介：https://wutheringwaves.kurogames.com/en/main/news/detail/4140 ，日期 2026-02-01。
- 目视确认：樱粉色长发、金橙色眼睛，白色与深靛蓝服饰/装甲，金色细节、冰青色发饰与电子发光装饰。组合主视觉含机兵、星辉、电子碎片与蓝青色轨迹。
- 珍珠白/深靛蓝/樱粉/冰青可作为本涂装配色方向；项目自选色值不应标为官方标准色。

## 推荐制作素材

| 本地原件 | 真实尺寸 | alpha | 官方原件直接 URL | 用途 |
|---|---|---|---|---|
| `02-official-website-lihui.webp` | 1200×1200 | 有，四角 alpha=0 | https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-8ad56dae.webp | 单人常规立绘，适合 port 主视觉 |
| `07-official-website-five.webp` | 1300×1080 | 有，四角 alpha=0，边缘官方柔化 | https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-eb60fae0.webp | 爱弥斯+机兵的另一构图，可直接透明叠加 |
| `news-4134-1.jpg` | 2560×1440 | 无 | https://hw-media-cdn-mingchao.kurogame.com/object/1769702400000/fginweaaop2snunxp2-1769782061823.jpg | 更高清的同一组合海报；右侧裁剪可避开左侧信息栏 |

官网下载素材路径由官网当前公开 JS 实际引用核实，而非猜测文件名：

- 页面：https://wutheringwaves.kurogames.com/en/main/role
- 页面入口脚本：https://wutheringwaves.kurogames.com/static4.0/assets/index-18bb4391.js
- `../assets/images/desktop/role/lihui/aimisi.webp` → `aimisi-8ad56dae.webp`
- `../assets/images/desktop/role/five/aimisi.webp` → `aimisi-eb60fae0.webp`

已通过 GIMP 后台无重绘、无放大地转成 PNG：

- `../artwork/assets/aemeath_pose_A.png`：1200×1200。
- `../artwork/assets/aemeath_pose_B_official.png`：1300×1080。

`news-4134-1.jpg` 的 URL 从官网实际新闻 JSON 的 `articleContent` 提取：

https://hw-media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/en/article/4134.json

本地 `official-article-4134.json` 和 `official-article-4140.json` 保留当次公开响应，以便追溯资源。它们是数据记录，不作为执行脚本。

## 其他官方源备选

| 本地原件 | 尺寸/说明 | 直接 URL |
|---|---|---|
| `01-official-wiki-transparent-portrait.png` | 1046×1037，透明局部立绘；与主单人立绘姿态相同，不推荐优先放大 | https://prod-alicdn-community.kurobbs.com/forum/dbecc24a507441428f583e36b03e329f20260105.png |
| `05-official-wiki-poster.png` | 1104×648，主画面不透明，仅边缘存在alpha；清晰度低于官网新闻图 | https://prod-alicdn-community.kurobbs.com/forum/79842a0777fc4aceb3528d196260f9c020260205.png |
| `03-official-website-body-super.webp` | 750×1334，移动端机兵组合海报，带黑色渐变背景 | https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-super-d84063f6.webp |
| `04-official-website-body.webp` | 750×1334，移动端单人海报，带黑色渐变背景 | https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-aa9f83e9.webp |
| `06-official-website-lihui-background.webp` | 1168×837，网页用粉色/粒子背景；不是角色立绘 | https://wutheringwaves.kurogames.com/static4.0/assets/aimisi-b9d030ee.webp |

库街区官方 WIKI 角色页面：https://wiki.kurobbs.com/mc/item/1457744312692867072 。该站页面在本次命令行读取时响应较慢；两张原件本身已从库街区官方 CDN 成功下载。此页面关联最初通过公开素材清单定位，最终制作优先使用可直接从游戏官网入口脚本/新闻 JSON 核实的官网资源。

## 技术记录

GIMP 读取后的实际尺寸、alpha 与角点采样见 `ASSET-METADATA.json`。WebP 转 PNG 仅进行解码后无损保存，不恢复或虚构源图中不存在的细节。原图没有被覆盖。

## 最终使用方式

左侧采用官网1200×1200立绘。GIMP仅在原画右侧被画布截断的发丝区域加入透明柔边蒙版，脸部和主体像素保留；源文件为artwork/source/aemeath_port_edge_mask.xcf。右侧采用官网1300×1080组合图，通过GIMP轮廓蒙版去掉大面积外侧海报背景，镜像后使角色朝向机首；源文件为artwork/source/aemeath_starboard_cutout.xcf。图形、文字、机号和涂装配色为本项目另行设计。
