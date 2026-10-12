# 历史 LLM 与 CAD 生成溯源
所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。

## 核心判断
LLM_USED=YES，但已恢复的直接 API→CAD 证据是 qwen-plus→PROJECT_DSL，不是整批 GPT→CadQuery。
GPT_TO_CADQUERY_BATCH_VERIFIED=UNKNOWN。不能用目录名、注释“LLM_SELECTED_ROUTE”或 metadata 模型名代替调用证据。

1. PartObjaverse Stage B：`code_text(case,rep,version)` 按 bbox/category 拼接 CadQuery；三轮规则固定。`plan()` 同样是字符串模板。无 API 调用。模型 NO、prompt 是自动生成说明文件，不是请求日志。证据 `/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1/scripts/stage_b_pipeline.py:79-102,137-145`，实际 `cad_code/*_v1.py` 与三轮 metrics 交叉核对。
2. llm_mesh_to_cad_pilot_v1：存有程序、计划、诊断与 STEP reload 日志；单例 CADPART_000 的 V1 reload 失败、V2 成功、V3 disconnected wire。作者是否交互式 GPT/具体模型 UNKNOWN；未恢复 prompt/response transport。原始 source OBJ 先存在，CAD 是拟合重建。`/data/home/cuiyuehan/project/mesh2cad/ours3/llm_mesh_to_cad_pilot_v1/reports/FINAL_REPORT.md` 和 evaluator 源码相符。三例补充见 `additional_cases/REPORT.md`。
3. GPT6 named Pilot100：准备代码写 `gpt-6-astra` 和 `READY_FOR_GPT_RESPONSES_API`，API_BLOCKER 记载当时 endpoint 不匹配。后续 100 个 provenance 写 `generator_model=gpt-6-codex; protocol=current Codex generation; attempt_count=1`。实际 `canonical_program.txt` 是 `ExtrudePolygon/Union/...` DSL，不是 `import cadquery` Python。最新 PILOT10_PROGRESS 虽名 Pilot10，TOTAL=100、FIRST_PASS_VALID=100、FINAL_REJECT=100、GOLD=SILVER=0。保留两阶段事实；不能推出成功调用 Astra。生成入口、真实模型服务、请求/响应、重试实现均 UNKNOWN。INPUT_MODALITY=记录为 mesh geometry summary/PCA；8幅视图存在，但是否送入生成器 UNKNOWN。OUTPUT_LANGUAGE=PROJECT_DSL，OUTPUT_FILE_FORMAT=.txt，EXECUTION_VALIDATION=历史 metrics CAD valid/STEP reload，GEOMETRY_FILTER=全部 reject。证据 `/data/home/cuiyuehan/project/mesh2cad/ours3/GPT6_PARTSAM_REALMESH_PSEUDOCAD_DATASET_V1/API_BLOCKER.json`、`PILOT10_PROGRESS.json`、`samples/*/provenance.json`、`canonical_program.txt` 与 `/data/home/cuiyuehan/project/mesh2cad/ours3/prepare_fast.py:21-34`。
4. 实际 LLM API 闭环：`/data/home/cuiyuehan/project/mesh2cad/scripts/edge_aware_cad_planner_v1/llm_planner.py:18-35,63-90,121-180` 的 system prompt+geometry brief+feature plan，经 `/chat/completions` 返回 DSL；`report.json` 的 PART_005 和 PART_019 都保留 `planner=llm; model=qwen-plus; dsl_raw; ok=true`。INPUT_MODALITY=TEXT geometry evidence，OUTPUT_LANGUAGE=PROJECT_DSL。PROMPT_TEMPLATE_PATH=上述源码 SYSTEM_PROMPT/build_llm_user_prompt。返回 `choices[0].message.content`；具体执行与错误处理由 DSL/上层模块完成。不存在已证实的通用批量 GPT 自修复生成器。

GPT_PAIR_GENERATION_MODE=UNKNOWN（GPT身份未经传输日志确认）；已证实局部模式为 MESH_GEOMETRY_TEXT_TO_LLM_TO_DSL_TO_STEP。未找到 GPT 同时独立生成源 mesh 与 CAD 的证据。重建 CAD 导出的 STL 不能当成原始 mesh 与 CAD 独立配对。

## CAD 程序分类
- CADQUERY：PartObjaverse 模板、PartSAM 拟合、CADFit、P3/X-Part feature_runtime、手写合成 demo。
- CADQUERY (FACETED_BREP)：PartSAM instance_cad 包含 base85 压缩的原三角网格；用 makePolygon/makeFromWires/sewing，不是恢复设计历史。
- PROJECT_DSL：P1/EXACT9998、GPT6 named pilot、synthetic64/advanced1000；Python 语法外观不等于任意 Python。
- DEEPCADE_SOURCE_HISTORY / FUSION_SOURCE_HISTORY：受控数据的上游 JSON；编译后 canonical DSL，独立于 pseudo-CAD。
- FREEFORM_PYTHON / OTHER：辅助脚本与混合表达；不能把任意 .py 计为 CAD target。
- STEP_ONLY：本轮未确认可训练、无程序的唯一 pair 总数，UNKNOWN。

V2 parser/executor `/data/home/cuiyuehan/project/mesh2cad/scripts/canonical_cad_dsl_v2.py:9-30,50-56`：AST 只允许赋值、允许的函数调用与显式 result；Box、Cylinder、Extrude、ExtrudePolygon、Union、Cut、Circle、Sketch、PolygonProfile、Axis、TrueRevolve、Fillet、Chamfer。V1/V2 与 Compact IR 不能混为同一种监督语言。CadQuery 则在实际源码中出现 extrude/revolve/cut/union/loft/spline；fillet/chamfer 仅部分支线支持，sweep 不可据关键词泛化为数据覆盖。
