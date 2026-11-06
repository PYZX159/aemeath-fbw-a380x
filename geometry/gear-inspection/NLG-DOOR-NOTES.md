# 前起落架舱门编号位置核查

此几何结论只读复用自 Megumin 项目的官方 paintkit 和本机安装版 `a380_exterior.gltf`，爱弥斯新项目尚未执行编号烘焙，必须等 root ART_READY。结论：**可以在前起落架舱门外皮上放 AM / 01，材质属于 FUSE1，不需要覆盖起落架机械件贴图。**

## 确认依据

安装模型：`D:/Microsoft Flight Simulator 2024(ChaJian)/Community2024/flybywire-aircraft-a380-842/SimObjects/AirPlanes/FlyByWire_A380_842/model/a380_exterior.gltf`。

安装模型的实际节点层级：

- `NLG_DOOR_FWD.L` → `MAIN FUSELAGE.017` → `A380X_FUSE1`
- `NLG_DOOR_FWD.R` → `MAIN FUSELAGE.018` → `A380X_FUSE1`
- `NLG_DOOR_AFT.L` → `MAIN FUSELAGE.015` → `A380X_FUSE1`
- `NLG_DOOR_AFT.R` → `MAIN FUSELAGE.016` → `A380X_FUSE1`

节点证据保存在 `installed-gltf-gear-node-evidence.json`。Paintkit 的对应对象为名称中的空格改下划线并带网格后缀，完整名称见 `nlg-door-report.json`。

实际外皮底图为 **`A380X_FUSE1_ALBEDO.PNG.DDS`**。`A380_EXTERIOR_NLG_ALBEDO.PNG.DDS` 是另一个起落架机械件材质，不是这四块舱门的外皮，不能把编号直接放到它上面。

## 几何与 UV（Blender 米制，当前为收起/关闭位置）

| 舱门 | Paintkit 对象 | 使用面世界 bounds (X,Y,Z) |
|---|---|---|
| FWD LH 左前门 | `MAIN_FUSELAGE.017_Mesh_44.234` | X 0.0023..1.2651；Y -34.0719..-31.7610；Z -1.2459..-0.3216 |
| FWD RH 右前门 | `MAIN_FUSELAGE.018_Mesh_44.239` | X -1.2651..-0.0023；Y -34.0719..-31.7610；Z -1.2459..-0.3216 |
| AFT LH 左后门 | `MAIN_FUSELAGE.015_Mesh_44.230` | X 0.0023..0.6731；Y -31.7858..-29.9506；Z -1.4480..-1.1642 |
| AFT RH 右后门 | `MAIN_FUSELAGE.016_Mesh_44.238` | X -0.6731..-0.0023；Y -31.7858..-29.9506；Z -1.4480..-1.1642 |

表格中的四门数据来自原几何核查；此新项目的编号脚本只使用下述两扇前门。

此新项目已复制左右前门 `NLG_FWD_LH_FUSE1_coordinates_uv.npz`、`NLG_FWD_RH_FUSE1_coordinates_uv.npz` 两个精确缓存。NPZ 格式沿用主工程缓存：`xyz`、`uv`、`normals` 为逐 polygon loop 数据，`face_offsets` 为面区间。因此可直接为选定门做编号墨层烘焙，再在 GIMP 中叠到现有 FUSE1，而不改门的其它区域。

门皮与小倒角分散在多块 UV 岛，整扇门的 UV 总 bounds 不适合直接当贴字矩形。报告中的平面 XY→UV 拟合误差较大，不能当作可靠仿射贴图；应使用原始 loop UV 烘焙。

## 推荐编号矩形

优先选两片较宽的前门外皮中央，闭合坐标：

- Y = **-33.20 .. -32.35 m**，长边沿机身纵向，宽 0.85 m。
- |X| = **0.45 .. 0.75 m**，短边横跨半扇门，字高约 0.30 m。
- 左门 X 为正，右门 X 为负；仅作用上述 FWD LH/RH 面，不把编号重复投到相邻机腹表面。

该区域采样到的 FUSE1 UV 约为：

- LH：U 0.185933..0.218649，V 0.142131..0.152043（约4096图上的 x=762..896、顶部原点 y=3473..3514）。
- RH：U 0.186041..0.218755，V 0.090995..0.100906（约 x=762..896、顶部原点 y=3683..3723）。

这些 UV 区间只是候选区顶点采样的参考包围盒，不应替代原面投影。黑/炭红底可用暖白或金色小号 AM / 01；浅色底用深色字。

如按闭合坐标做投影，可使用纵向 Y 为文字横轴，|X| 为文字竖轴。左右两侧的横轴读向需分别处理，避免开门后成为镜字。舱门打开时会随原模型动画变换，制作后需要在模拟器中验证实际开门姿态下的读向；本次没有声称已完成游戏内动画验证。
