# RESMOKE100_V2

FACTORY_GATE = PASS
GEOMETRY_GATE = FAIL
CAN_SCALE_TO_1000 = NO
NEXT_ALLOWED_STAGE = IMPROVE_COMPACT_RECONSTRUCTION

## 同源 paired 结果

使用完全相同100个source SHA256、split group、canonical mesh和transform；未重采样source、未增加数据、未训练、未Scale1000、未P3。V1原件及历史保护检查：PASS。核心evaluator逐字节相同：True。无case ID特定规则：True。

V1：{'version': 'V1', 'total': 100, 'metric_n': 97, 'parse_pass': 97, 'execute_pass': 97, 'step_export_pass': 97, 'step_reload_pass': 97, 'strict_accept': 5, 'relaxed_only': 92, 'reject': 3, 'near_pass': 2, 'median_normalized_chamfer': 0.026544768899841475, 'median_iou': 0.11857379767827529, 'median_centroid_l2_error': 0.05616278005337948, 'median_bbox_error': 0.0}

V2：{'version': 'V2', 'total': 100, 'metric_n': 100, 'parse_pass': 100, 'execute_pass': 100, 'step_export_pass': 100, 'step_reload_pass': 100, 'strict_accept': 27, 'relaxed_only': 73, 'reject': 0, 'near_pass': 2, 'median_normalized_chamfer': 0.011538041170488938, 'median_iou': 0.29260826659393524, 'median_centroid_l2_error': 0.029636170917170357, 'median_bbox_error': 0.00017606280744075775}

所有有效样本的median采用各版本实际metric N；严格paired公共子集为97例，其统计见 paired_common_metric_statistics.json，不能把新增可执行例与V1缺失指标强行配对。逐例差值定义 V2−V1，缺失值保持空值。NEAR_PASS为非strict、IoU>=0.70且NCD<=0.02的分析子集，仍包含在RELAXED_ONLY里，不替代strict。

IMPROVED/UNCHANGED/WORSE = {'UNCHANGED': 37, 'IMPROVED': 63}。定义先比较strict/relaxed/reject等级，同级比较加权geometry score（1e-9容差）；不表示每项指标同时单调改善。严格救回22例，原严格受损0例。所有逐例NCD/IoU/centroid/bbox变化、family、primary_fix、score和candidate数保存在v1_v2_case_comparison.csv。

## 紧凑性与限制

共执行520个候选，观察到最多6次Boolean。候选失败：{'BOOLEAN_FAILURE': 3}；这些与最终case失败是不同分母。所有最终目标通过native AST、有效实体、STEP export、reload、tessellation及artifact hash验证。无STL/OBJ导入包装、triangle soup或DSL目标。

严格接受中22例使用显式假设厚度的平面区域薄实体。这类结果在固定表面/近似occupancy协议下几何一致，但不证明恢复真实厚度、实体体积或设计意图。IoU仍为近似scan-fill voxel occupancy，尤其开放表面不可解释为真实体积重合度。保留这种目标类型的显式标记，避免把采样/体素分辨率下的一致性夸大为真实CAD恢复。

本轮用于pipeline debug并在同一100例上拟合和选候选；无held-out泛化证据。没有大量case-specific hardcode，但评测来源仍是开发集，不能把本结果当作泛化成绩。

## Gate 与下一步

扩量条件严格采用本轮新规则：execute>=90%、reload>=90%、strict>=30%、无重大evaluator bug、无case-specific hardcode，并通过factory验证。V1旧工程gate的Scale1000建议不再作为本轮几何gate依据。最终决定：NO；本轮没有实际扩量。

主要剩余问题：Strict acceptance below 30%; compact family/profile recovery remains insufficient。优先改善曲面/局部截面/分离结构表达以及真实可识别的参数；不通过放宽阈值、P3或三角面片封装提高分数。artifact consistency errors：[]。

## 文件

诊断：/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_reconstruction_diagnosis_v1/reports/DIAGNOSIS_REPORT.md
实现差异：/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_reconstruction_improvement_v1/reports/RECONSTRUCTION_V1_V2_DIFF.md
入口：/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_reconstruction_improvement_v1/scripts/reconstruct_v2.py --limit 3 / 10 / 100
表格：tables/v1_v2_summary.csv、v1_v2_case_comparison.csv、strict_accept_v2.csv、near_pass_v2.csv、remaining_failures_v2.csv
逐例：cases/*/manifest.json、proposals.json、attempts/*（包含全部native程序、参数、日志和评测）；选中目标在cad/step/reload/mesh/metrics下。
可视化：visualizations/index.html 与诊断目录的visualizations/index.html；相同坐标与相机比较。
