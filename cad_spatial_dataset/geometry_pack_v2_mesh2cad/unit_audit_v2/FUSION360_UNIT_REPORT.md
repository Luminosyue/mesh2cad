# Fusion360 V2 单位修复与602条复测

**结论：单位混用已定位并在隔离目录修正，但标签几何 Gate 未通过。V2-100与训练继续暂停。**

## 前后对照

|指标|修复前|修复后|
|---|---:|---:|
|DSL执行成功|601|601|
|STEP重载成功|595|593|
|DSL/source bbox比例中位数|0.09999999999999996|0.9999999999999987|
|source/DSL bbox比例中位数|10.000000000000004|1.0000000000000013|
|Chamfer通过|0|282|
|coverage通过|0|253|
|联合几何通过|0|235|
|超时/几何未知|1|0|

分母均为602；比例中位数仅针对可测形状。注意比例方向：旧DSL/source约0.1，source/DSL约10，不是旧DSL/source约10。

## 定位与合同

20条按构造调用数分层（简单7/中等6/困难7），固定哈希排序取样，不按指标筛选。原始STEP声明centimetre，OCP读取目标MM；官方OBJ与STEP的extent约0.1，V1 pack mesh与STEP约1。旧transform却由厘米OBJ计算后直接作用于毫米STEP表面，导致canonical输入尺度错误。

同时，20条DSL的轴比例与体积立方根比例并不全部一致：不是单一全局缩放即可解决全部标签。单位转换因子10来源于cm→mm合同，而不是拟合Chamfer。每条合同记录source原生cm、读取mm、旧DSL cm、新DSL mm、共同canonical尺度和位移。canonical transform由源STEP bbox一次生成，surface与DSL共用；不旋转，不改变法向，保留源surface的8192行顺序。

每条保存旧DSL副本、旧逆变换DSL、修正毫米DSL、新canonical DSL、unit_contract、coordinate_transform、surface、reconstructed STEP与audit。旧逆变换沿用基线6位精度，单位转换不额外舍入；不在本次修改DSL拓扑/操作语义。遇到未覆盖语法立即报错，不默默保留长度参数。

## 冻结方法与限制

几何比较严格沿用旧方法：源/重建各20000个确定性面积均匀采样点，同一cad_id种子及异或种子；双向未平方NN均值/源tessellation bbox对角线；Chamfer≤0.01，源→重建距离≤0.02时coverage≥0.98。无ICP，无逐样本缩放拟合。表面文件检查8192×6。

point cloud无实体体积，体积比标记为不可用；OBJ仅在watertight时报告体积。轴、bbox和CAD实体体积比保留在probe20.json与before_after602.json，不用bbox体积冒充实体体积。

原超时样本仅对实际DSL重放提高一次上限到600秒：{'cad_id': 'fusion360__23658_c75a430c_0000', 'timeout_s': 600, 'status': 'execute', 'elapsed_s': 3.4461307525634766, 'label_gate': False}。超时保持unknown，不自动记为几何失败。

## 残留错误：只诊断，不继续缩放

旧转换器只遍历ExtrudeFeature，跳过其他timeline类型（fusion360_to_dsl.py:332）；圆/矩形快捷分支没有传递双侧或对称拉伸参数（231–249），而polygon分支有；距离取abs（194–195）；曲线采样可能产生近似误差。这些是代码证据与候选风险，尚未证明每个失败的具体因果。

602条源JSON风险计数：{'ignored_timeline_features': {'total': 0, 'nonpassing': 0}, 'filtered_intersect': {'total': 1, 'nonpassing': 1}, 'circle_rectangle_non_one_side': {'total': 53, 'nonpassing': 53}, 'negative_extent_distances': {'total': 182, 'nonpassing': 162}}。详情见residual_conversion_risks.json；不能仅因DSL不含LOFT/SWEEP就声称本批失败由缺少这些操作造成。

## 门禁与冻结

V1基线哈希检查：19580文件，变化0。

当前只交付单位修复与标签审计。未覆盖旧checkpoint、日志、配置、报告或split；未读取test decode或模型测试指标（使用了全库GT标签做数据质量审计）；未启动训练。旧运行未作停止/重启操作。2796是pack记录数，2644仍只是候选去重组。

unit_audit_v1中的初轮复测误把source_points的8192×3当作含法向数组，在执行DSL前被schema检查阻断；记录保留，不作为前后对照。权威复测为unit_audit_v2/results602.json。

后续需获得授权修复DSL转换语义并复测，不制作V2-100，不改阈值。

## 复现

代码：scripts/geometry_pack_v2_mesh2cad/；fusion_units_probe.py、fusion_unit_contract.py、test_fusion_unit_contract.py、fusion_units_retest_v2.py、fusion_units_report.py。Python环境cadfit-env；CPU-only，24 workers，BLAS线程1。脚本使用排他写入，禁止直接在已完成输出目录重跑；复现须指定新的隔离输出目录。
