import collections,contextlib,datetime,hashlib,io,json,pathlib
import nbformat

BASE=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2')
R=BASE/'reports'
def load(name):return json.loads((R/name).read_text())
def save(name,data):
    with (R/name).open('x',encoding='utf8') as f:
        if isinstance(data,str):f.write(data)
        else:json.dump(data,f,ensure_ascii=False,indent=2)

s=load('FULL_SUMMARY.json'); norm=load('NORMALIZATION_SUMMARY.json'); rows=load('FULL_RESULTS.json'); groups=load('FULL_GROUPING.json'); freeze=load('FULL_V1_VERIFY.json')
inventory=json.loads((BASE/'inventory.json').read_text())
rows=[{**inventory[r['index']],**r} for r in rows]
assert len(rows)==len(inventory)==2796 and len({r['index'] for r in rows})==2796
passing=[r for r in rows if r.get('label_gate')]
quota=collections.Counter((r['dataset'],'simple' if r['operation_count']<=5 else 'medium' if r['operation_count']<=10 else 'hard') for r in passing)
affected=collections.Counter()
for g in groups['matches']:
    if len(set(g['old_splits']))>1:affected[g['method']]+=1
gate={'CURRENT_GATE':'V2_STAGE1_LABEL_UNITS_AND_GROUPING_AUDIT','audited':2796,'V1_FROZEN':freeze['pass'],'LABEL_EXECUTABLE':sum(bool(r.get('execution_ok')) for r in rows),'STEP_RELOADABLE':sum(bool(r.get('step_reload')) for r in rows),'LABEL_GEOMETRY_PROVISIONAL_PASS':len(passing),'NORMALIZATION_PROTOCOL':'FAIL_FUSION360_FACTOR10_UNIT_CHAIN','SOURCE_AND_GEOMETRY_GROUPING':'PROPOSAL_ONLY_NOT_NEW_SPLIT','candidate_identity_groups':s['identity_groups'],'unique_cad_count_certified':False,'cohort100_selected':False,'practical_v2_samples_built':0,'overfit_started':False,'test_decode_results_read':False,'new_training_started':False,'old_experiments_modified':False,'thresholds_frozen':False,'full_v2_expansion_authorized_by_gate':False}
gate['geometry_fingerprint_coverage']=sum(bool(r.get('geometry_fingerprint')) for r in rows)
gate['timeout_count']=sum(r.get('failure_stage')=='timeout' for r in rows)
save('STAGE1_GATE.json',gate)
save('AUDITED_ROWS_WITH_IDENTITIES.json',rows)
save('COHORT100_FEASIBILITY.json',{'required':{'simple':30,'medium':40,'hard':30,'fusion360_min':30,'meshfit_raw_curves_gt128_min':10},'qualified_label_rows_by_dataset_and_difficulty':{str(k):v for k,v in quota.items()},'source_counts_before_gate':{'deepcad':2194,'fusion360':602},'meshfit_curve_quota':'NOT_MEASURED; oracle count cannot substitute','status':'BLOCKED_UNITS_AND_LABEL_GATE','operation_definition':s['operation_count_definition']})
text=f'''# V2 数据制作前审计：暂不放行100条训练

## 结论

已逐条审计全部2796条（DeepCAD 2194、Fusion360 602）。本次仅完成标签重放、存储协议核验和保守去重分组；没有制作100条practical数据，没有启动训练，没有改写旧split或V1。

602条Fusion360均存在约10倍单位链路不一致，当前不能直接作为新V2输入。标签几何统计使用原始STEP读入坐标，不通过ICP、缩放搜索或阈值调节隐藏不一致。此处的FAIL不能简单解释为所有Fusion360的拓扑或程序内容错误：单位错误与真实形状误差必须在修复单位合同后分开复测。

## 标签重放结果（初始阈值，尚未冻结）

| 来源 | 数量 | DSL执行 | STEP重载 | 暂定几何Gate通过 | Chamfer_rel中位数 |
|---|---:|---:|---:|---:|---:|
'''
for ds,a in s['by_source'].items():
    med=a['chamfer_quantiles'].get('median')
    text+=f"| {ds} | {a['n']} | {a['execution_ok']} | {a['reload_ok']} | {a['label_pass']} | {med} |\n"
text+=f'''
全体可执行 {gate['LABEL_EXECUTABLE']}/2796，可重载 {gate['STEP_RELOADABLE']}/2796；暂定几何通过 {len(passing)}/2796。每条结果、失败阶段、DSL源坐标副本、reconstructed.step均保留。没有使用原始source JSON回退重建来冒充DSL执行成功。

## 指标和范围

重放目标为cad_target.dsl；先按记录的仿射变换逆变换，再用同一CadQuery/OCP DSL执行器导出STEP并重新读入。参考是每条metadata明确指向的model.step。两个STEP都用同一tessellation实现。

Chamfer_rel = 两个方向最近邻欧氏距离均值的平均 / GT tessellation bbox对角线；不平方。每边独立、确定性均匀面积采样20000点，不做对齐。coverage_02 = GT采样点到重放采样点距离/D <=0.02的比例。暂定通过条件是Chamfer_rel<=0.01且coverage_02>=0.98，同时表面文件8192x6且manifest与pack标签AST一致。

这不是模型test性能；读取了全体GT标签和源几何以执行用户要求的数据审计，没有读取test decode输出、预测或模型test指标。样本级几何误差与样本身份分组均可复核。

## Fusion360单位链路

全体602条的surface原始采样bbox对角线约为coordinate_transform.source_diagonal的10倍。所有2796条curve normalization与surface记录的scale/translation字段相同，但相同字段不代表字段对应的输入单位正确。

例：fusion360__102525_06a3094b_0000，官方model.obj的x范围约[-0.195,0.195]，STEP tessellation后的x范围[-1.95,1.95]；V1将从官方OBJ生成的scale=9.3000904用于STEP采样，生成canonical surface x范围约[-16.322,19.949]。对应DSL却是宽3.627035的canonical Box。原STEP显式声明CENTI/METRE；源码build_fusion360_sample.py复制官方STEP和OBJ，而geometry_pack_v1/pack.py重新tessellate STEP后直接套用旧OBJ变换。

应在V2中明确存储STEP文件单位、reader输出单位、DSL源数值单位、统一工作单位，再应用一个共享变换。禁止仅凭metric最优自动选择10或0.1，也禁止永久改动V1。单位合同确认后重新报告无额外对齐的几何指标。

归一化检查另发现14条DeepCAD的detected-edge法向存在非单位值；必须检查零向量/相邻法向抵消并显式保存有效性，不能对零向量盲目归一化。数值误差、数组形状和各样本证据见NORMALIZATION_ROWS.json。

## 去重分组不等于已经得到2796个独立CAD

用source STEP身份、source JSON hash、规范化DSL AST hash以及归一化三角网格fingerprint连接分组，得到{s['identity_groups']}个候选组，其中{s['duplicate_groups']}组含多个记录。旧跨split组数按方法分别为{dict(affected)}，这些方法相互重叠，不能求和当成重复CAD数。

几何fingerprint保留方向，消除平移和统一缩放，对顶点/三角形重排及朝向翻转不敏感；量化1e-5 bbox diagonal。它仍依赖tessellation，未穷尽重网格或近似形状重复。其中1条Fusion360重放审计150秒超时，未保存几何fingerprint；实际fingerprint覆盖2795/2796。因此候选组数不是“已认证独立CAD数”，FULL_SUMMARY.grouping_complete只表示全部记录已尝试处理。未新划split、未删除任何样本。若新目标必须保持2796个独立CAD，需从合格whole-part候选源补足去重/标签排除造成的缺口，不能把clean/practical计为新CAD。

## 100条配额与训练状态

当前标签Gate通过行的来源/难度计数为{dict(quota)}。难度按全部DSL构造器调用计数，包括sketch/boolean；这一定义必须在最终100条选择前固定。曲线>128配额必须从practical meshfit完整曲线计数核验，不能拿oracle计数代替。尚未选择100条，也未退而求其次减少Fusion360配额。

官方Llama-3.2-1B-Instruct本地目录存在，但文件名为config (2).json、model (2).safetensors和tokenizer (2).json等，不是标准from_pretrained布局。未重命名它们，未加载或混用SpatialLM微调语言模型。训练前还需独立整理可追溯模型载入布局，并明确Sonata/C2/projector的初始化来源。

## 实验设计与下一步

按顺序：确认并修复新V2的单位合同 → 复测标签并冻结阈值 → 完成近重复核验、组级划分和必要补样 → 按30/40/30及Fusion360>=30、practical曲线>128至少10条选择100条 → 制作同一mesh/同一次锐边检测驱动的B0/B1/M2输入 → B0/M2 overfit与跨CAD correct/shuffle → 通过后才制作2796版与更大数据。

完整曲线必须保留；128只作为训练时可审计的选择预算。官方SpatialLM轴向约定为axis-aligned、z-up；不独立旋转输入，所有位置、轴和方向参数保持一致。来源：https://github.com/manycore-research/SpatialLM 。新任务的主实验是mesh-derived；oracle单独命名为上界，不与practical B1混比。

需要用户确认：允许先修复V2单位合同，并在去重后补充合格CAD以达到“2796个独立CAD”，还是先接受数量较少的严格合格pilot？本次未自动改变样本总数或标签。

## 复现、保护和限制

V1冻结哈希复核：{freeze['checked_files']}个文件，变化列表={freeze['changed']}。冻结范围覆盖目标DSL、transform、source JSON、表面、检测/锐边点、source STEP、执行器及原surface index cache；不是整个10TB工作区快照。旧训练进程在本轮开始时已不在，未由本次终止或修改。

执行代码：code/audit_v2_labels.py；归一化检查：code/inspect_v2_protocol.py；5个审计单元测试通过。详细报告JSON均在本目录。审计首版_audit_stage1_v1因相对STEP路径处理缺陷中止并保留，其结果不可使用；本版所有2796条路径已规范为绝对路径并通过存在性检查。本版CPU调度从8并发调整至24并发时只更换本次调度器，完成样本未重写；全体结果仍来自相同代码、参数和执行器。

几何数值受tessellation和Monte Carlo点采样影响；曲线局部归一化会丢失全局centroid是另一个表示层问题，未在此自动修改C2。固定practical、噪声在线增强、post-encoder预算和LLM拼接hook尚未实现，不能宣称通过。
'''
save('STAGE1_REPORT.md',text)
save('REPRODUCE_COMMANDS.md','''# Reproduction

Interpreter: /data/miniconda3/envs/cadfit-env/bin/python

The code has exclusive-create guards. Do not rerun into a populated directory; clone the scripts to a NEW audit directory and change only OUT/BASE to that new directory. Keep existing inputs unchanged.

1. python -B code/audit_v2_labels.py --inventory
2. python -B code/audit_v2_labels.py --workers 24 --tag FULL
3. python -B code/inspect_v2_protocol.py
4. python -B code/test_v2_audit.py
5. /data/miniconda3/envs/spatiallm/bin/python -B code/finalize_v2_audit_complete.py

No model weights are loaded; CUDA_VISIBLE_DEVICES is empty in replay workers. Per-sample subprocess timeout:150 seconds. No source-JSON fallback. A failed worker is explicitly a failed audit, never silently omitted.
''')
cells=[nbformat.v4.new_markdown_cell('# V2 label-quality audit companion\n\n## tl;dr\n2796 records audited; unit inconsistency blocks V2 creation and training. The notebook recomputes summaries from saved evidence, not models.'),nbformat.v4.new_markdown_cell('## Context & Methods\n### Key Assumptions\nSymmetric unsquared NN Chamfer divided by source STEP bbox diagonal; 20000 area-uniform points per shape. Provisional thresholds 0.01 and coverage_02 >=0.98. No alignment or hidden unit correction. Full replay code is ../code/audit_v2_labels.py.'),nbformat.v4.new_code_cell("from pathlib import Path\nimport json, collections\nreport_dir=Path("+repr(str(R))+")\nrows=json.loads((report_dir/'FULL_RESULTS.json').read_text())\nassert len(rows)==2796\nprint('audited',len(rows))"),nbformat.v4.new_markdown_cell('## Data\nDeterministic first ten identities and validation states; no prediction metrics.'),nbformat.v4.new_code_cell("print([{k:r.get(k) for k in ['cad_id','dataset','execution_ok','step_reload','label_gate']} for r in rows[:10]])"),nbformat.v4.new_markdown_cell('## Results'),nbformat.v4.new_code_cell("for ds in ['deepcad','fusion360']:\n    subset=[r for r in rows if r.get('dataset')==ds]\n    print(ds, len(subset), 'label_pass',sum(bool(r.get('label_gate')) for r in subset))\nnormalization=json.loads((report_dir/'NORMALIZATION_SUMMARY.json').read_text())\nprint(normalization['source'])\nfrozen=json.loads((report_dir/'FULL_V1_VERIFY.json').read_text())\nassert frozen['pass']\nprint('unchanged source files',frozen['checked_files'])"),nbformat.v4.new_markdown_cell('## Takeaways\nDo not train or expand yet. Resolve units explicitly, then rerun label comparisons and finalize group-level splits. Geometry fingerprint grouping is conservative and incomplete for retessellated near-duplicates. Saved audit script is the expensive replay entry point; this companion only recomputes evidence summaries.')]
notebook=nbformat.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'validation':{'method':'sequential Python exec in a fresh namespace, not Jupyter kernel','reason':'nbclient/ipykernel unavailable; every code cell executed in order'}})
scope={};counter=0
for c in notebook.cells:
    if c.cell_type!='code':continue
    counter+=1;buf=io.StringIO()
    with contextlib.redirect_stdout(buf):exec(compile(c.source,'audit_companion','exec'),scope)
    c.execution_count=counter;c.outputs=[nbformat.v4.new_output('stream',name='stdout',text=buf.getvalue())]
nbformat.validate(notebook)
with (R/'AUDIT_COMPANION.ipynb').open('x',encoding='utf8') as f:nbformat.write(notebook,f)
save('FILE_MANIFEST.json',{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('code','reports') for p in (BASE/folder).iterdir() if p.is_file()})
print(json.dumps(gate,indent=2));print('report',R/'STAGE1_REPORT.md')
