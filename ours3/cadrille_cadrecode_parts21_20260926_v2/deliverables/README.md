# Cadrille / CAD-Recode 分零件生成与装配

21 个案例，306 个 X-Part 零件，两种方法使用完全相同的输入。

流程：已有 X-Part 拆分 → 点云归一化与 256 点最远点采样 → 各模型生成 CadQuery → 有效实体与 STEP 重读检查 → 逆变换回原位 → 命名零件 STEP 装配。

坐标公式：point=(world-center)*2/extent；world=CAD*extent/200+center。没有按预测包围盒拟合尺寸。单位沿用输入网格，不能据此认定毫米。

每个失败零件最多使用三次固定种子的点云重采样；模型权重不变，不用其他方法的零件填补。COMPLETE 表示输入零件都得到有效 CAD，不代表几何完全复原；PARTIAL 缺件列表详见 SUMMARY.json。

每个案例目录含 assembled.step、assembled.stl、parts/*/world.step、原始 CadQuery 及 transform.json。原始 CadQuery 位于模型规范坐标系，world.step 已还原到装配坐标。

|方法|完整案例|有效零件|
|---|---:|---:|
|cadrille|18/21|302/306|
|cadrecode|16/21|298/306|

输入说明：沿用服务器已有 X-Part 完整/补全部件。本次没有重新训练分割模型。鸟屋、音箱、酒架的部件合并边界与原始整网格存在约 15%–22% 的最大边界偏差；详见 INPUT_COORDINATE_AUDIT.json。预览中的 Input 是实际送入两种方法的部件合并网格。

编辑后重建：安装 CadQuery，在 scripts 目录运行 python regenerate_case.py ../cadrille/案例名（或 ../cadrecode/案例名），生成 edited_assembled.step。