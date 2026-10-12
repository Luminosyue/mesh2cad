# MESH2CAD_RECONSTRUCTION_DIAGNOSIS_V1

## 结论

97 个成功执行案例的低几何一致性主要来自粗轮廓挤出无法保存局部截面、分离表面及其间隙，而不是 STEP 导出/reload 故障。V1 应表述为 **COARSE_TEMPLATE_APPROXIMATION_WITH_MULTI_CANDIDATE_SELECTION**，不是完整设计意图恢复。88 个最终目标是单轴轮廓挤出，7 个包围盒、2 个圆柱，3 个没有实体候选。

## bbox 为何中位数为零

独立从真实 source 和重载 STEP 网格复算 97 例，最大与保存值差异为 0.0，51 例恰为零。没有发现复用 source bbox 的 metric bug。V1 projected_profile 把轮廓范围仿射匹配到源投影边界，挤出深度取源轴向 min/max；box 同样直接匹配外部范围。因此外部范围相同、内部几何错误可以同时发生。

center L2 与 extent L-infinity 分别计算，bbox_error 取两者最大值。CAD 平移0.1的测试保留 extent error 并改变 center error，详见 bbox_metric_audit.json。归一化只来自源 mesh，未对 CAD 独立归一化；V2 无 evaluator 修正，V1/V2 核心指标可以直接 paired compare。历史 PartSAM 的 centroid_error 是 bbox 中心距离/对角线，**不是**当前面积加权表面质心误差；历史数字不能直接套入本轮协议。

## 全量描述与失败分类

100 例均提取顶点/面数、连通分量、watertight、面积、有效体积、bbox、质心、PCA轴与范围、长宽比及边界边；97 个程序另提取全部要求的 AST 操作计数。详见 geometry_and_cad_descriptors.csv 与 descriptors_and_diagnosis.json。

92 个 mismatch 的互斥主因：{'WRONG_PROFILE': 43, 'MISSING_BOOLEAN_STRUCTURE': 33, 'WRONG_MAJOR_DIMENSIONS': 12, 'WRONG_CAD_FAMILY': 4}。其他定义的 taxonomy 标签保留，但没有足够证据就不强行赋予 MISSING_HOLE、WRONG_REVOLVE_AXIS 或 FREEFORM_NOT_REPRESENTABLE。次要原因、几何证据及置信度逐例保存。MISSING_BOOLEAN_STRUCTURE 是“CAD 将源连通分量间的间隙填实”的操作性诊断，不声称原始设计一定用了 Boolean。

自动 source family 分布：{'A_SINGLE_PRIMITIVE': 1, 'B_EXTRUSION_LIKE': 25, 'F_CURVED_OR_FREEFORM': 16, 'E_MULTI_PRIMITIVE_ASSEMBLY': 58}。基于 PCA/拓扑/法向量的启发式分类不是设计真值；F 表示曲面/自由形状歧义，不等于数学上无法表达。旋转、圆锥及完整语义布尔 family detector 尚未实现，不做虚假完成声明。

## 可视化核验

已生成5个严格通过 + 20个非随机代表失败 + 3个 unsupported，共28例。覆盖最差IoU、最差NCD、中位失败、最佳relaxed、不同family/操作复杂度/失败类别。visualizations/selection.json 保存选取原因。每例 source、CAD、overlay、采样点距离使用相同相机、坐标系、显示尺度；颜色范围固定0–0.15 canonical units。不能从低IoU单独推断缺洞或缺失原始表面。

3 个 unsupported 的源为 PCA rank-2 平面轮廓，归为 B：CadQuery可表达平面草图，但V1要求非零体积实体且没有显式厚度策略。不存在由此推导“必须P3补全”的证据。V2 结果逐例在 unsupported_cases.csv，薄实体的厚度是假设，非观察到的设计参数。

## 历史 fitter 为什么不可直接对比 488/468 与 5

代码依据：本目录 scripts/pipeline.py 的 audit_extract_one、generate_specs、section_loft_profile、geometry_metrics、fit_case；scripts/build_partsam_p1.py 的 fit_direct。文件来自本轮服务器只读快照，原件哈希纳入guard。

旧主线为2个挤出 + 2个截面loft，loft最多32×40采样及多track；V1删掉loft，换成粗box/cylinder。旧P1另有三轴轮廓和box/cylinder枚举。历史无证据表明使用了通用连续优化或显式对称/revolve求解。

更关键的是样本与指标不一致：当前 54/100 例会触发旧主线“顶点<20或面<20”的排除规则；V1有93个非watertight part表面。旧488/2000和468保留并非这100例上的paired结果。旧bbox/centroid归一化、18k采样、预reload STL评测亦与本轮不同。因此既不能把差距全归因于缺loft，也不能把可读的开放part表面一概说成损坏源mesh。详见 historical_fitter_feature_comparison.csv。

P3/X-Part 本轮禁用；0例有独立证据确认需补全，效果未经测试。原source保持原样。
