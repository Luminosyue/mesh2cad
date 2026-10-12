CURRENT_GATE = HISTORICAL_MESH2CAD_AUDIT_COMPLETE_WITH_PROVENANCE_GAPS; READ_ONLY_GUARD=PASS

=====================
HISTORICAL CAD
=====================

HISTORICAL_PRIMARY_CAD_GENERATION_MODE = MIXED: deterministic mesh fitting/templates (PartSAM/PartObjaverse/P3), CADFIT_SEARCH_TO_CADQUERY, hand-written CAD-first; source-history DSL separately; GPT batch identity UNKNOWN

CAD_PROGRAM_LANGUAGE = CADQUERY + PROJECT_DSL/COMPACT_IR; faceted CadQuery wrappers separate

CAD_GENERATOR_SCRIPT = partsam_cad_iou_top1000_v1/scripts/pipeline.py; stage_b_pipeline.py; p3_xpart_open_cases/_cadquery_batch_code_20260922/feature_runtime.py; CADFit/run_pipeline.py; build_partsam_p1.py

LLM_USED = YES (verified qwen-plus -> DSL); GPT_TO_CADQUERY batch UNKNOWN

LLM_MODEL = qwen-plus verified; gpt-6-codex metadata-only; gpt-6-astra planned/blocked

PROMPT_TEMPLATE = scripts/edge_aware_cad_planner_v1/llm_planner.py:SYSTEM_PROMPT/build_llm_user_prompt; GPT prompt UNKNOWN

CAD_EXECUTOR = CadQuery/OCC; restricted AST DSL executor; OCP sewing for faceted branch

CAD_STEP_EXPORT = YES


=====================
HISTORICAL MESH
=====================

HISTORICAL_PRIMARY_MESH_GENERATION_MODE = MIXED: PartObjaverse/PartSAM source mesh + P3/X-Part completion + CAD tessellation; NPZ upstream UNKNOWN

HUNYUAN3D_USED = YES (Hunyuan3D-Part/X-Part); image-to-mesh implementation found, executed cohort UNKNOWN

HUNYUAN3D_ROLE = MESH_ONLY_SOURCE (mesh-conditioned part completion); IMAGE_TO_MESH code present; CAD_TO_RENDER_TO_MESH UNKNOWN

P3_USED = YES (mesh segmentation/bboxes)

CAD_DIRECT_TESSELLATION_USED = YES (synthetic GT and reconstruction meshes; no new tessellation executed)

MESH_POSTPROCESS = branch-specific normalization/inverse transform, extraction, X-Part completion; image wrapper Taubin/decimate/repair code; no universal postprocess


=====================
PAIR DIRECTION
=====================

PRIMARY_PAIR_PIPELINE = MIXED (CAD_FIRST + MESH_FIRST; source history conversion separately)

MESH_AND_CAD_SHARE_SAME_SOURCE = MIXED (same GT body in CAD-first; same input part but approximate pseudo-CAD in mesh-first; some upstream UNKNOWN)


=====================
PIPELINES
=====================

PIPELINE_1 = PartSAM mesh -> geometric fitting -> CadQuery -> STEP -> filter

PIPELINE_1_CASE_N = 2112 available; 2000 attempted; 1994 executed; 488 qualified; 468 final

PIPELINE_2 = CAD-first synthetic: native CadQuery demos; seeded synthetic DSL cohorts separate

PIPELINE_2_CASE_N = 5 native CQ GT demos; 64 DSL chamfer; 1000 advanced DSL (non-additive; cross-cohort dedup UNKNOWN)

PIPELINE_3 = existing mesh -> P3 -> X-Part -> fitted CadQuery -> Compact IR experiments

PIPELINE_3_CASE_N = 20 frozen overfit cases; Toaster initial39 X-Part /3 P1 smoke; global unique pairs UNKNOWN


=====================
PAIR VALIDATION
=====================

CAD_EXECUTION_CHECK_USED = YES

STEP_RELOAD_CHECK_USED = YES

MESH_CAD_CD_USED = YES

MESH_CAD_IOU_USED = YES (protocol differs by branch; some surface/fill proxy)

PAIR_FILTER_THRESHOLD = PartSAM: IoU128>=0.90,NCD<=0.01,bbox<=0.03,centroid<=0.02; dedup+repro delta<=0.005; P1 mean<=.003,p95<=.01,max<=.03


=====================
EXISTING DATA
=====================

TOTAL_REUSABLE_PAIR_N = UNKNOWN globally; 468 qualified CQ pair paths verified; 16 historical P1-ready DSL; overlaps/other cohorts not summed; EXACT9998 separate

CADQUERY_PAIR_N = 468 qualified PartSAM rows verified; global count UNKNOWN

DSL_PAIR_N = 16 P1-ready; 64/1000 synthetic historical reports; EXACT9998=9998 separately; global dedup UNKNOWN

STEP_ONLY_PAIR_N = UNKNOWN; 2112 faceted conversions are not STEP-only or feature targets

HUNYUAN_PAIR_N = 20 frozen P3/X-Part overfit references; global validated count UNKNOWN

REAL_MESH_PAIR_N = 468 qualified PartSAM; global count UNKNOWN


=====================
REUSABILITY
=====================

CAN_REUSE_OLD_CAD_GENERATOR = YES (recovered fitting/templates/CADFit; start from retained OBJ; upstream GLB/labels missing in sampled traces; not a verified GPT batch factory)

CAN_REUSE_OLD_HUNYUAN_PIPELINE = YES (P3/X-Part code); image branch historical execution UNKNOWN

CAN_REUSE_OLD_PAIR_FILTER = YES (retain protocol distinctions; current results not re-executed)

CAN_REUSE_OLD_SURFACE_PREPROCESS = YES (build_partsam_p1.py and existing canonical preprocess)

CAN_REBUILD_CURVE_INPUT = YES conditionally from valid STEP with compatible schema/runtime; not run


=====================
DECISION
=====================

RECOMMENDED_DATA_FACTORY_TO_SCALE = HYBRID; recover/freeze generator and target contracts before scaling

MAIN_LIMITATION_OF_OLD_PIPELINE = pseudo-target fidelity, misleading provenance labels, missing upstream GLB/labels and generator entrypoints, finite source pool, geometry/coordinate mismatch and corrupt NPZ

WHAT_MUST_CHANGE_FOR_CADQUERY = native standalone feature-based CQ targets; preserve transforms/provenance; STEP/BRep and geometry gate; compatible surface/curve/token pipeline; no faceted wrappers or lossy DSL substitution

NEXT_ALLOWED_STAGE = AUDIT_REVIEW_AND_FACTORY_PROTOCOL_FREEZE_ONLY; no generation or training authorized in this audit



## 证据与范围
本轮递归记录3,443,377个文件元数据；排除.git、__pycache__、.pytest_cache、node_modules，不遍历目录symlink。扫描覆盖不等于逐文件人工解释；未恢复的case总数与上游身份明确UNKNOWN。
CAD_GENERATION_SCRIPT_INVENTORY将静态关键词候选和逐行审阅的入口分开，不能把API_CODE_PRESENT当真实运行。基础证据为源码、manifest、logs、metrics、mtime和39个case产物hash。mtime只表明观察时间窗，不能直接证明生成时间。
主报告所有计数均非跨数据集求和。源mesh与CAD reconstructed mesh明确分开；历史报告通过不等于本轮重新执行通过。最后引用核验：3个抽查source OBJ哈希一致；但历史GLB/instance-label上游共6条路径缺失，无法本轮重核上游hash。P3 frozen20的60条mesh/CAD/STEP引用均存在。详见integrity/REFERENCE_VALIDATION.json。
已证实LLM=qwen-plus；PartObjaverse20实际是模板。GPT6 pilot100实际DSL、全部reject，Astra调用未证实。PartSAM2112 faceted转换不作为参数化训练目标。468是质量筛选的pseudo-CAD，不是原设计GT。EXACT9998单列CONTROLLED_SOURCE_CAD_DATA。
此前实际训练：P3 Compact IR joint20的frozen manifest + joint_train.log +最终报告记录update640/TF15；Airplane9/Demo5历史摘要记录9/9与5/5。准备状态的PartSAM16、DSL1000与synthetic64不能据文件名说已经训练；后续训练另有目录，未闭合的运行关联UNKNOWN。EXACT9998及其ablation训练为独立受控源监督，不在历史synthetic合计中。
CAD-first与mesh-first都存在。Independent generation配对、GPT双生成、CAD-render-Hunyuan配对、全局唯一训练就绪pair总数均未证实。

详见audit/8个审计文件、stats/2个计数表、HISTORICAL_PIPELINE_DIAGRAM.md、NEXT_STEP_DECISION.md。
READ_ONLY_GUARD覆盖3,443,377个已有文件size/mtime/mode，改变0、丢失0；1,606份证据SHA核对一致。本轮没有API调用、生成、训练、重tessellation或导入项目执行模块。完整初始元数据gzip与证据索引保存在服务器integrity/；本地交付包不复制历史大数据。
