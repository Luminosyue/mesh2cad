# 下一步决策
RECOMMENDED_DATA_FACTORY_TO_SCALE=HYBRID（基于现有实现；不是批准启动生成）。

1K：已有advanced1000是DSL CAD-first准备数据，不能改名CadQuery数据。若目标为native CadQuery，优先复用现有独立CadQuery builder/真实mesh拟合+468候选资产，先确认目标格式、曲线输入和坐标契约；保留CAD-first合成对作为对齐可控支线。3个抽查case的上游GLB/标签路径缺失，因此目前可重用的是已保存source.obj以后的流程，不能直接重新跑完整原始提取入口。
10K：当前未证明一键10K native CadQuery工厂。PartSAM原池2112、attempted2000、最终468（23.4%/attempted），有限来源不能通过复制或降阈值宣称达到10K。CAD-first扩参数具备对齐优势，但需找回advanced1000生成入口和seed/operation定义；仅5个手写demo不能支撑操作多样性。更大规模同样需要可审计的去重、对象split与数据完整性。
EXACT9998提供的是独立的source-history→DSL成功组织资产，不混入“GPT/Hunyuan synthetic”统计。若选择扩其路线，继续作为CONTROLLED_SOURCE_CAD_DATA。

| existing route | program quality | mesh realism | alignment | observed yield | diversity | reuse/scaling |
|---|---|---|---|---|---|---|
| CAD-first templates | genuine parametric GT | tessellation only | by construction, same body | 5 demos; DSL1000 separate | hand-written limited, DSL operators restricted | reuse executor/export; full 10K generator not verified |
| PartSAM geometric fit | parametric pseudo-CAD | source mesh | approximate; shared source part | 468/2000=23.4% final | extrusion/loft/primitive biases | generator/filter reusable; source pool ceiling |
| P3+X-Part+fit | inferred CAD | completed mesh, may alter source | approximate; track normalization | global dedup yield UNKNOWN | spline/loft, long sequences | reusable frontend; expensive and no original design GT |
| LLM/qwen DSL | constrained DSL | inherited source mesh | approximate | two evidenced LLM parts; no broad yield | limited allowed operators | supplementary; not scalable-GPT proof |
| GPT6 named100 | DSL; identity not independently verified | source STL | all rejected | 0/100 accepted | UNKNOWN | cannot scale as qualified factory |
| faceted BREP | embeds mesh, no inferred features | source mesh | face copying | 2112 conversions | triangle topology only | reference/visualization, reject as native feature supervision |

MAIN_LIMITATION_OF_OLD_PIPELINE=provenance labels mixed with implementation, pseudo-CAD fidelity and source pool limits, coordinate/metric differences, missing generator entrypoints, long spline/loft programs, truncated NPZ inputs。
WHAT_MUST_CHANGE_FOR_CADQUERY=明确输出为独立可执行CadQuery源码；禁止把DSL文本或嵌入三角网格wrapper冒充参数化CQ；保留source hash、构建器/参数/模型证据、坐标变换和版本；独立STEP重载/BRep/mesh geometry gate；对象级split与去重；重建surface/curve缓存并验证token/context。已有Compact IR spline/ruled-loft无法无损降到冻结DSL V1，不得硬转换。
NEXT_ALLOWED_STAGE=审阅审计、恢复缺失生成入口并冻结扩量方案/验收标准；本轮不生成、不训练。
