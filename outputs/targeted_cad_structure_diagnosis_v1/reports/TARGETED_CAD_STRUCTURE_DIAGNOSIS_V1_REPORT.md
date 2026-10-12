# 定向 CAD 结构诊断 V1

本轮完成 45 个固定案例的残差驱动结构试验，同时完成全部 76 个 Near 的门槛统计、61 个 Extrude+Cut 和 47 个 Simple Primitive 的审计。

**结论：局部编辑可改善部分几何，但尚未证明可靠的工程特征恢复，不扩大到 209 全量。**

- 147 个候选，接受 13 次编辑，分布在 10 个案例；6 个案例达到明显改善。
- 新增 Strict 1 个；合并未变案例后为 18 Strict / 75 Near / 116 Reject，主要部件 Strict 仍为 15/153。
- 专门选取的 20 个 Near 中，明显改善 1 个（5%），未达到 30%；新增 Strict 也未达到 8 个。其他两组包含的 Near 单独计入 `NEAR_DENOMINATOR_SENSITIVITY.json`，不隐藏分母差异。
- 接受的 13 次编辑中，11 次缺少孔/槽/凹腔的侧壁证据，应解释为通用切除或端部修剪，不能用来宣称找回了真实工程孔槽。

## 主要诊断

76 个 Near 中 IoU 失败 61 个、bbox 失败 37 个、NCD 失败 35 个、质心失败 18 个；这些计数允许重叠。IoU 是最常见阻碍。

61 个 Extrude+Cut 中，按已公开的基础体覆盖规则，8 个基础体得到支持、53 个基础体不匹配。这个结论是近似占据与消融支持的规则诊断，不是人工真值。大量失败不能靠继续叠加小孔解决。

47 个 Simple Primitive 中，11 个仍支持简单体解释、4 个有规则支持的重新分类、32 个无法可靠区分参数问题、基础截面问题和类别问题。因此不能确认“主要因为误分类”。

## 证据与局限

复用原 20,000 个冻结源采样点、原 CAD 种子和 IoU128 协议。45 例重算基线指标漂移为零。残差组件包含体积、包围盒、质心、主轴、长宽比、CAD 距离代理量与源表面方向。所有候选先通过原生表示和 STEP 检查，再评测几何。Strict 门槛未改。

残差是原评测器的近似体素占据差，不是精确实体布尔差。细杆、薄片及开放的分割网格尤其受体素分辨率和填充方式影响。未独立标注语义真值，因此不报告虚构的孔槽检测准确率。几何接受率与语义正确率不能等同。

历史只读保护：51282 个文件，哈希/大小/修改时间与文件集合检查通过。未重跑 P3、未扩对象、未训练、未重新装配、未重做历史装配渲染。

## 报告

1. [Near 门槛分解](NEAR_GATE_FAILURE_REPORT.md)
2. [Extrude+Cut 诊断](EXTRUDE_CUT_DIAGNOSIS_REPORT.md)
3. [Simple Primitive 审计](SIMPLE_PRIMITIVE_AUDIT_REPORT.md)
4. [残差特征诊断](RESIDUAL_FEATURE_DIAGNOSIS_REPORT.md)
5. [结构修复试验](STRUCTURE_REFINEMENT_PILOT_REPORT.md)
6. [下一阶段决策](NEXT_STAGE_DECISION.md)
7. [完整数值输出](FINAL_READOUT.txt)
8. [45 例八面板诊断图](../visualizations/index.html)

下一阶段优先检查基础体和截面假设、开放网格占据误差，以及有独立证据的孔槽检测。当前不进入全量补特征、Reassembly 或 Scale100。
