FlyByWire A380X — 爱弥斯 / Aemeath AM-01 Guiding Starlance 虚构痛机
版本 0.1.0 / 主题编号 AM-01 / 虚构注册号 B-38AM

适用机模
本包适用于非原生、非模块化的 FlyByWire A380X Stable 2024.1.0，
基础容器应为 SimObjects/AirPlanes/FlyByWire_A380_842。
本包不适用于较新的 Native 2024 模块化 A380X。

安装
1. 退出微软模拟飞行 2024。
2. 确认本次启动实际加载的 Community 插件目录。
   此电脑 UserCfg.opt 记录的 InstalledPackagesPath 为：
     D:\Microsoft Flight Simulator 2024(ChaJian)
   但发现的基础 A380X 位于其中 Community2024，同时也存在 Community。
   请通过当前插件管理器或 FlyByWire Installer 的 MSFS 2024 目标设置确认。
3. 复制整个 aemeath-fbw-a380x-stable 文件夹到实际启用的 Community 目录。
   复制后的文件夹根部应直接包含 manifest.json、layout.json 与 SimObjects。
   不要只复制 texture.AEMEATH，不要覆盖基础机模或其他涂装。
4. 启动模拟器，选择 FlyByWire A380X，在涂装列表选择：
     Aemeath / AM-01 - Guiding Starlance B-38AM

注册号与素材
主题名称为 Aemeath / AM-01，主题航班号为 001，ATC 航空公司名称为 AEMEATH。
这是虚构主题，没有编造或声明真实分配的 ICAO 航司代码。
外部机身、左翼下方与驾驶舱铭牌使用同一虚构机号 B-38AM。
前起落架前舱门采用 AM / 01 简写，四台发动机依位置编号为 01—04。
动态机身编号已关闭，避免与绘制编号重复。
驾驶舱编号由 A380X_REGISTRATION_ALBEDO.PNG.DDS 控制，并保留透明通道。
角色与系列相关素材的出处见制作工作区 references/SOURCES.md。
此为个人使用的同人涂装，不表示取得官方联名或公开分发授权。

文件完整性
十三张定制 DDS 各自必须带同名 .DDS.json，且两者都应列入 layout.json。
采用无污渍/磨损的干净漆面，保留必要门框、警示和步行区域标记。
翼下机号使用 A380_EXTERIOR_WING1_ALBEDO.PNG.DDS；四张翼面贴图均已覆盖为干净版本。
工作区中的 Update-PackageLayout.ps1 会先生成描述文件再更新索引。
Validate-Package.ps1 为只读校验，不会安装、更新或覆盖游戏内容。
文件校验通过不代表已完成模拟器内的视觉验收。

卸载
退出模拟器，只移除独立的 aemeath-fbw-a380x-stable 文件夹。
保留 flybywire-aircraft-a380-842 基础机模及其他涂装。
