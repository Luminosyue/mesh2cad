# CAD validity 与 pair 几何过滤
所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。

CAD_VALIDATION_PIPELINE=Python AST parse → CadQuery subprocess → shape/BRep validity → STEP export → importStep reload → exported mesh load → metrics（各支线具体顺序有差异）。DSL支线另加受限AST parse、canonical serialize/roundtrip、执行、token/context检查。

## PartSAM Top1000
`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/scripts/pipeline.py:626-660,673-741,1086-1108`：双向各18000面积采样，固定SEED与SEED+1，KDTree最近邻；CD=两方向平均距离的均值，NCD=CD/source bbox diagonal。Hausdorff为样本max，不是H95。bbox extent与bbox center均按source diagonal归一化。
IoU64候选筛选>=0.50，再IoU128精排。使用共同union bbox，pitch=max_extent/(resolution-4)，体素占据包含fill策略；非水密源也计算，这不是严格ground-truth solid Volume-IoU。
最终阈值：CAD valid + STEP reload + IoU valid + IoU128>=0.90 + NCD<=0.01 + bbox_error<=0.03 + centroid_error<=0.02；去重+历史复现差值abs(delta IoU128)<=0.005。2000候选→1994执行→488合格→468最终。存在source_watertight=false而IoU很高，不能宣称恢复真实实心设计。

## PartSAM P1
`/data/home/cuiyuehan/project/mesh2cad/build_partsam_p1.py:117-135`：双向各4096固定面积采样，点到三角面精确距离/source diagonal，mean_each<=0.003，p95_each<=0.01，sampled_max<=0.03。另有最小厚度>=1e-4 diagonal、collator/context检查。30 geometry_ready→16 training_ready。和Top1000的NCD/体素IoU不是同一口径，不能把468直接当16的上游真值。

## PartObjaverse pilot20 / initial LLM pilot
Stage B每方向100000点，最大bbox归一至1，工作坐标100，3轮择优；20/20 BRep与metrics通过不表示geometry quality threshold通过。IoU仅双边水密时计算，报告有效分母0。初始LLM pilot每方向50000点，STEP reload硬gate，V2 IoU约0.45137、CD-L1约0.018914；不把低精度pilot当扩量合格样本。

## P3 feature fitting与CADFit
P3 feature builder质量协议记录双向6000点到面、P95<=diagonal1%、samplemax<=4%，详见 `_cadquery_batch_code_20260922/quality.py` 和 assemble_cases.py；不同重建版本需按对应记录判断。
CADFit synthetic demo历史审计区分 raw IoU=0 与 aligned IoU约0.9063的case_a，来自坐标尺度差异；高aligned指标不能替代原坐标pair对齐。`/data/home/cuiyuehan/project/mesh2cad/CADFit/artifacts/synthetic_high_mesh_two_case_v1/geometry_provenance_report.md:7-13,31-63`。

Chamfer操作是CAD倒角；Chamfer Distance是距离指标。advanced1000 的 CHAMFER_DISTANCE_SCALE_PASS 指倒角参数缩放，不等于mesh-CAD Chamfer Distance筛选。Volume error只在支线条件满足时有意义，不能将缺值或0代理理解为真实体积精确。
