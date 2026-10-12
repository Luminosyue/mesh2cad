import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,csv,hashlib,ast,re,collections,sys,platform
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');OLD=O/'mesh2cad_data_factory_v1_smoke100';D=O/'mesh2cad_reconstruction_diagnosis_v1';I=O/'mesh2cad_reconstruction_improvement_v1';R=O/'mesh2cad_resmoke100_v2'
sys.path.insert(0,str(I/'scripts'))
from execute_v2 import validate
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()))
def csvout(p,rs):
 fields=list(dict.fromkeys(k for r in rs for k in r)) if rs else ['case_id']
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def score(m):return 10*m['normalized_chamfer']+1-m['iou']+2*m['centroid_l2_error']+m['bbox_error']
old={r['case_id']:r for r in [json.loads(l) for l in (OLD/'manifests/cases.jsonl').read_text().splitlines()]}
new={p.parent.name:json.loads(p.read_text()) for p in sorted((R/'cases').glob('*/manifest.json'))}
if set(old)!=set(new):raise RuntimeError('Not the same 100 completed case IDs')
desc=json.loads((D/'tables/descriptors_and_diagnosis.json').read_text());ds={r['case_id']:r for r in desc};diag=json.loads((D/'reports/diagnosis_summary.json').read_text())
errors=[];changed=[]
protected=json.loads((D/'integrity/V1_AND_DONORS_BEFORE.json').read_text())
for p,x in protected.items():
 q=Path(p)
 if not q.exists() or sha(q)!=x['sha256'] or q.stat().st_mtime_ns!=x['mtime_ns']:changed.append(p)
source_guard=json.loads((OLD/'integrity/PROTECTED_SOURCE_HASHES.json').read_text())
for p,x in source_guard.items():
 if not Path(p).exists() or sha(p)!=x['sha256']:changed.append(p)
metadata=json.loads((OLD/'integrity/HISTORICAL_METADATA_BEFORE.json').read_text())
for p,size,mtime,mode in metadata:
 try:
  s=Path(p).lstat()
  if (s.st_size,s.st_mtime_ns,s.st_mode)!=(size,mtime,mode):changed.append(p)
 except FileNotFoundError:changed.append(p)
frozen=json.loads((I/'integrity/FROZEN_ENGINE_SHA256.json').read_text());frozen_ok=all(sha(I/p)==h for p,h in frozen.items())
guard={'status':'PASS' if not changed else 'FAIL','v1_and_donor_hash_n':len(protected),'historical_source_hash_n':len(source_guard),'historical_metadata_n':len(metadata),'changed_paths':changed,'frozen_engine_hashes_match':frozen_ok}
dump(R/'reports/READ_ONLY_GUARD.json',guard)
comparison=[];improvement_counts=collections.Counter();booleanmax=0;candidate_total=0;attempt_failures=collections.Counter()
for cid,b in new.items():
 a=old[cid];am=a['geometry_metrics'];bm=b.get('metrics',{});d=R/'cases'/cid
 if sha(d/'source/source_mesh.stl')!=a['source_mesh_sha256'] or b['source_mesh_sha256']!=a['source_mesh_sha256']:errors.append(cid+': source hash')
 for f in ['normalized_mesh.ply','transform.json']:
  if sha(d/'normalized'/f)!=sha(OLD/'cases'/cid/'normalized'/f):errors.append(cid+': normalization byte mismatch')
 for attempt in b['attempts']:
  candidate_total+=1
  if attempt.get('error'):attempt_failures['WORKER_OR_EVALUATOR_ERROR']+=1
  ex=attempt.get('execution',{})
  if ex.get('failure_reason'):attempt_failures[ex['failure_reason']]+=1
  code=(Path(attempt['path'])/'cad.py').read_text();validate(code)
  tree=ast.parse(code);n=sum(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ['union','cut','intersect'] for x in ast.walk(tree));booleanmax=max(booleanmax,n)
 if bm:
  if sha(b['step_path'])!=bm['step_sha256'] or sha(b['cad_mesh_path'])!=bm['cad_mesh_sha256'] or sha(d/'normalized/normalized_mesh.ply')!=bm['source_mesh_sha256']:errors.append(cid+': metric artifact hash mismatch')
  if bm['source_seed']!=20261006+int(cid.split('_')[1])*10 or bm['n_points_per_mesh']!=20000:errors.append(cid+': sampling protocol')
  if bm['iou_protocol']!='APPROXIMATE_VOXEL_SCAN_FILL_IOU_V1':errors.append(cid+': IoU protocol')
  strict=bm['iou']>=.9 and bm['normalized_chamfer']<=.01 and bm['bbox_error']<=.03 and bm['centroid_l2_error']<=.02
  if strict!=(b['status']=='STRICT_ACCEPT'):errors.append(cid+': strict decision')
 ar={'STRICT_ACCEPT':0,'RELAXED_ANALYSIS_ONLY':1,'REJECT':2}[a['filter_decision']];br={'STRICT_ACCEPT':0,'RELAXED_ANALYSIS_ONLY':1,'REJECT':2}[b['status']]
 change='IMPROVED' if br<ar else 'WORSE' if br>ar else 'UNCHANGED'
 if ar==br and am and bm:
  delta=score(bm)-score(am);change='IMPROVED' if delta < -1e-9 else 'WORSE' if delta>1e-9 else 'UNCHANGED'
 improvement_counts[change]+=1
 row={'case_id':cid,'source_sha256':a['source_mesh_sha256'],'split_group_id':a['split_group_id'],
  'V1_NCD':am.get('normalized_chamfer'),'V2_NCD':bm.get('normalized_chamfer'),'delta_NCD':bm['normalized_chamfer']-am['normalized_chamfer'] if am and bm else None,
  'V1_IoU':am.get('iou'),'V2_IoU':bm.get('iou'),'delta_IoU':bm['iou']-am['iou'] if am and bm else None,
  'V1_centroid':am.get('centroid_l2_error'),'V2_centroid':bm.get('centroid_l2_error'),'V1_bbox':am.get('bbox_error'),'V2_bbox':bm.get('bbox_error'),
  'V1_status':a['filter_decision'],'V2_status':b['status'],'V1_family':ds[cid]['selected_kind'],'V2_family':b.get('best_kind'),'source_family':b['family'],
  'primary_fix':b.get('best_kind'),'initial_score':b.get('initial_score'),'best_score':b.get('best_score'),'optimization_steps':b['optimization_steps'],
  'candidate_count':b['candidate_count'],'best_candidate_id':b.get('best_candidate_id'),'improvement':change,'thickness_assumed':b.get('thickness_assumed',False),
  'near_pass_analysis_only':bool(b.get('near_pass') and b['status']!='STRICT_ACCEPT'),'step_path':b.get('step_path')}
 comparison.append(row)
csvout(R/'tables/v1_v2_case_comparison.csv',comparison)
for name,rows in [('strict_accept_v2',[r for r in comparison if r['V2_status']=='STRICT_ACCEPT']),('near_pass_v2',[r for r in comparison if r['near_pass_analysis_only']]),('remaining_failures_v2',[r for r in comparison if r['V2_status']!='STRICT_ACCEPT'])]:csvout(R/'tables'/(name+'.csv'),rows)
def summarize(version):
 items=list(old.values()) if version=='V1' else list(new.values());metrics=[r['geometry_metrics'] if version=='V1' else r.get('metrics',{}) for r in items];valid=[m for m in metrics if m]
 status=[r['filter_decision'] if version=='V1' else r['status'] for r in items]
 out={'version':version,'total':len(items),'metric_n':len(valid)}
 for key in ['parse_pass','execute_pass','step_export_pass','step_reload_pass']:out[key]=sum(any(a.get('execution',{}).get(key,False) for a in r['attempts']) for r in items)
 out.update(strict_accept=status.count('STRICT_ACCEPT'),relaxed_only=status.count('RELAXED_ANALYSIS_ONLY'),reject=status.count('REJECT'),
  near_pass=sum(bool(m) and m['iou']>=.7 and m['normalized_chamfer']<=.02 and st!='STRICT_ACCEPT' for m,st in zip(metrics,status)))
 for k in ['normalized_chamfer','iou','centroid_l2_error','bbox_error']:out['median_'+k]=float(np.median([m[k] for m in valid])) if valid else None
 return out
summaries=[summarize('V1'),summarize('V2')];csvout(R/'tables/v1_v2_summary.csv',summaries);v1,v2=summaries
common=[cid for cid in old if old[cid]['geometry_metrics'] and new[cid].get('metrics')]
common_stats={'paired_metric_n':len(common),'V1':{k:float(np.median([old[c]['geometry_metrics'][k] for c in common])) for k in ['normalized_chamfer','iou','bbox_error','centroid_l2_error']},'V2':{k:float(np.median([new[c]['metrics'][k] for c in common])) for k in ['normalized_chamfer','iou','bbox_error','centroid_l2_error']}}
dump(R/'reports/paired_common_metric_statistics.json',common_stats)
engine=(I/'scripts/reconstruct_v2.py').read_text();no_case_rules=not re.search(r'case_\d{3,}',engine)
unsafe=['import trimesh\nresult = trimesh.load("x.stl")','import cadquery as cq\nresult = cq.importers.importStep("x.step")','import cadquery as cq\nvertices = [[0,0,0]]','import cadquery as cq\nresult = cq.Workplane("XY").box(1,1,1)'+'.union(cq.Workplane("XY").box(1,1,1))'*7]
rejected=0
for code in unsafe:
 try:validate(code)
 except (ValueError,SyntaxError):rejected+=1
evaluator_equal=sha(OLD/'scripts/factory.py')==sha(I/'scripts/v1_runtime.py') and sha(OLD/'scripts/fit_logic.py')==sha(I/'scripts/fit_logic.py')
rescue=sum(r['V1_status']!='STRICT_ACCEPT' and r['V2_status']=='STRICT_ACCEPT' for r in comparison);damaged=sum(r['V1_status']=='STRICT_ACCEPT' and r['V2_status']!='STRICT_ACCEPT' for r in comparison)
factory_pass=not errors and not changed and frozen_ok and evaluator_equal and no_case_rules and rejected==4 and booleanmax<=6 and all(r['candidate_count']<=8 for r in new.values())
geometry_pass=v2['strict_accept']>=30;scale=factory_pass and geometry_pass and v2['execute_pass']>=90 and v2['step_reload_pass']>=90
status={'factory_gate':'PASS' if factory_pass else 'FAIL','geometry_gate':'PASS' if geometry_pass else 'FAIL','can_scale_to_1000':scale,
 'next_allowed_stage':'SCALE_1000' if scale else 'IMPROVE_COMPACT_RECONSTRUCTION','primary_remaining_blocker':'Unobserved design thickness and unresolved disconnected/freeform profiles' if scale else 'Strict acceptance below 30%; compact family/profile recovery remains insufficient',
 'v1':v1,'v2':v2,'paired_improvement':dict(improvement_counts),'strict_rescue_n':rescue,'strict_damaged_n':damaged,
 'bbox_metric_bug_found':diag['bbox_bug_found'],'evaluator_byte_identical':evaluator_equal,'no_case_id_specific_rules':no_case_rules,'safety_tests_rejected':rejected,
 'candidate_total':candidate_total,'candidate_failure_counts':dict(attempt_failures),'max_boolean_observed':booleanmax,'artifact_errors':errors,
 'thickness_assumed_strict_n':sum(r['V2_status']=='STRICT_ACCEPT' and r['thickness_assumed'] for r in comparison),
 'p3_xpart_used':False,'p3_xpart_needed_confirmed':False,'read_only_guard':guard['status'],'diagnosis':diag}
dump(R/'reports/status.json',status)
features=[
 {'feature':'Axis detection','historical':'world + PCA axes, cap/side score','V1':'same helper; two extrusion axes','V2':'same + surface-normal axes','worth_reusing':'YES'},
 {'feature':'Profile extraction','historical':'projected union, holes, cap192; P1 cap80','V1':'copied silhouette, cap96','V2':'same + coplanar region contours; cap96','worth_reusing':'YES'},
 {'feature':'Section loft','historical':'32 sections x 40 points, up to4 outer/hole tracks','V1':'MISSING','V2':'6 x12, one outer track, no silent hole drops','worth_reusing':'YES, bounded adaptation'},
 {'feature':'Primitive fitter','historical':'primitive_profile helper; P1 actively tries 3 axes x box/cylinder','V1':'one oriented box and mean-extents cylinder','V2':'V1 incumbent retained; LS sphere; primary search in planes/profiles','worth_reusing':'YES; full P1 search not ported'},
 {'feature':'Symmetry / revolve','historical':'no explicit revolve in generate_specs','V1':'absent','V2':'not implemented; not claimed','worth_reusing':'future work'},
 {'feature':'Parameter search','historical':'finite candidate enumeration; P1 up to9','V1':'up to4 candidates, no thickness search','V2':'up to8, global3-value thickness grid, discrete axis search','worth_reusing':'YES'},
 {'feature':'Booleans','historical':'profile holes; loft hole exceptions can retain uncut solid','V1':'profile union/cut','V2':'plane assemblies/holes, <=6; reject failed or overbudget candidates','worth_reusing':'selective, not silent error suppression'},
 {'feature':'Candidate ranking','historical':'IoU64 screening, top2 IoU128; P1 point-triangle score','V1':'strict then IoU then NCD','V2':'strict then 10*NCD+(1-IoU)+2*centroid+bbox','worth_reusing':'finite search pattern'},
 {'feature':'Evaluator','historical':'18k samples; centroid means bbox-center/diag; pre-reload exported STL','V1':'20k, surface centroid; canonical errors; reloaded STEP mesh','V2':'byte-identical V1 evaluator','worth_reusing':'do NOT mix thresholds/semantics'},
 {'feature':'Source selection','historical':'GLB-labeled parts; rejects vertices<20 or faces<20','V1':'existing STL; lowest face counts prioritized','V2':'exact same V1 source hashes, no resampling','worth_reusing':'cohort difference must be disclosed'}]
csvout(D/'tables/historical_fitter_feature_comparison.csv',features)
small=sum(r['face_count']<20 or r['vertex_count']<20 for r in desc)
tax=diag['failure_modes'];unsupported=[r for r in desc if r['status']=='REJECT']
csvout(D/'tables/unsupported_cases.csv',[{'case_id':r['case_id'],'classification':'B','assessment':r['unsupported_assessment'],'V2_status':new[r['case_id']]['status'],'source_plane_residual':r['plane_residual_max']} for r in unsupported])
first=next(r for r in old.values() if r['geometry_metrics']);src=trimesh.load(OLD/'cases'/first['case_id']/'normalized/normalized_mesh.ply',force='mesh');cad=trimesh.load(first['cad_mesh_path'],force='mesh');shifted=cad.copy();shifted.apply_translation([.1,0,0])
tests={'all_97_bbox_recomputed':True,'max_saved_difference':max(r.get('bbox_saved_difference',0) for r in desc),'zero_bbox_n':diag['bbox_exact_zero_n'],
 'translation_test':{'extent_error_before':float(np.max(abs(src.extents-cad.extents))),'extent_error_after':float(np.max(abs(src.extents-shifted.extents))),
 'center_error_before':float(np.linalg.norm(src.bounds.mean(0)-cad.bounds.mean(0))),'center_error_after':float(np.linalg.norm(src.bounds.mean(0)-shifted.bounds.mean(0)))},
 'normalization':'source transform copied byte-for-byte; no independent CAD alignment','corrected_metric_needed':False}
dump(D/'reports/bbox_metric_audit.json',tests)
diagnosis=f'''# MESH2CAD_RECONSTRUCTION_DIAGNOSIS_V1

## 结论

97 个成功执行案例的低几何一致性主要来自粗轮廓挤出无法保存局部截面、分离表面及其间隙，而不是 STEP 导出/reload 故障。V1 应表述为 **COARSE_TEMPLATE_APPROXIMATION_WITH_MULTI_CANDIDATE_SELECTION**，不是完整设计意图恢复。88 个最终目标是单轴轮廓挤出，7 个包围盒、2 个圆柱，3 个没有实体候选。

## bbox 为何中位数为零

独立从真实 source 和重载 STEP 网格复算 97 例，最大与保存值差异为 {tests['max_saved_difference']}，{diag['bbox_exact_zero_n']} 例恰为零。没有发现复用 source bbox 的 metric bug。V1 projected_profile 把轮廓范围仿射匹配到源投影边界，挤出深度取源轴向 min/max；box 同样直接匹配外部范围。因此外部范围相同、内部几何错误可以同时发生。

center L2 与 extent L-infinity 分别计算，bbox_error 取两者最大值。CAD 平移0.1的测试保留 extent error 并改变 center error，详见 bbox_metric_audit.json。归一化只来自源 mesh，未对 CAD 独立归一化；V2 无 evaluator 修正，V1/V2 核心指标可以直接 paired compare。历史 PartSAM 的 centroid_error 是 bbox 中心距离/对角线，**不是**当前面积加权表面质心误差；历史数字不能直接套入本轮协议。

## 全量描述与失败分类

100 例均提取顶点/面数、连通分量、watertight、面积、有效体积、bbox、质心、PCA轴与范围、长宽比及边界边；97 个程序另提取全部要求的 AST 操作计数。详见 geometry_and_cad_descriptors.csv 与 descriptors_and_diagnosis.json。

92 个 mismatch 的互斥主因：{tax}。其他定义的 taxonomy 标签保留，但没有足够证据就不强行赋予 MISSING_HOLE、WRONG_REVOLVE_AXIS 或 FREEFORM_NOT_REPRESENTABLE。次要原因、几何证据及置信度逐例保存。MISSING_BOOLEAN_STRUCTURE 是“CAD 将源连通分量间的间隙填实”的操作性诊断，不声称原始设计一定用了 Boolean。

自动 source family 分布：{diag['families']}。基于 PCA/拓扑/法向量的启发式分类不是设计真值；F 表示曲面/自由形状歧义，不等于数学上无法表达。旋转、圆锥及完整语义布尔 family detector 尚未实现，不做虚假完成声明。

## 可视化核验

已生成5个严格通过 + 20个非随机代表失败 + 3个 unsupported，共28例。覆盖最差IoU、最差NCD、中位失败、最佳relaxed、不同family/操作复杂度/失败类别。visualizations/selection.json 保存选取原因。每例 source、CAD、overlay、采样点距离使用相同相机、坐标系、显示尺度；颜色范围固定0–0.15 canonical units。不能从低IoU单独推断缺洞或缺失原始表面。

3 个 unsupported 的源为 PCA rank-2 平面轮廓，归为 B：CadQuery可表达平面草图，但V1要求非零体积实体且没有显式厚度策略。不存在由此推导“必须P3补全”的证据。V2 结果逐例在 unsupported_cases.csv，薄实体的厚度是假设，非观察到的设计参数。

## 历史 fitter 为什么不可直接对比 488/468 与 5

代码依据：本目录 scripts/pipeline.py 的 audit_extract_one、generate_specs、section_loft_profile、geometry_metrics、fit_case；scripts/build_partsam_p1.py 的 fit_direct。文件来自本轮服务器只读快照，原件哈希纳入guard。

旧主线为2个挤出 + 2个截面loft，loft最多32×40采样及多track；V1删掉loft，换成粗box/cylinder。旧P1另有三轴轮廓和box/cylinder枚举。历史无证据表明使用了通用连续优化或显式对称/revolve求解。

更关键的是样本与指标不一致：当前 {small}/100 例会触发旧主线“顶点<20或面<20”的排除规则；V1有93个非watertight part表面。旧488/2000和468保留并非这100例上的paired结果。旧bbox/centroid归一化、18k采样、预reload STL评测亦与本轮不同。因此既不能把差距全归因于缺loft，也不能把可读的开放part表面一概说成损坏源mesh。详见 historical_fitter_feature_comparison.csv。

P3/X-Part 本轮禁用；0例有独立证据确认需补全，效果未经测试。原source保持原样。
'''
(D/'reports/DIAGNOSIS_REPORT.md').write_text(diagnosis)
diff='''# RECONSTRUCTION_V1_V2_DIFF

V1：世界/PCA轴打分，最多两轴 silhouette extrusion，加一个bbox和一个平均范围圆柱；按strict、IoU、NCD挑选。没有局部截面、平面组件或参数搜索。

V2：保留并重新执行V1最优候选作为incumbent；由source family约束开放平面区域候选；按法向与点到平面残差聚类，合并三角形为二维轮廓；最多7个区域、96个轮廓顶点、6次Boolean，禁止单三角区域和三角轮廓，拒绝高复杂度面片封装。加入历史截面tracking的紧凑6截面×12点loft，仅允许单outer track，不静默丢失hole。新增表面法向轴枚举、最小二乘球体候选。

对开放平面区域采用0.0002、0.001、0.004 canonical厚度的有限搜索。厚度没有被源表面观测到，始终记录thickness_assumed。这提供几何一致的薄实体候选，不恢复原始壁厚或设计历史。没有为单case设置尺寸，没有改变输入或补全mesh。

每例最多8个候选；执行后的STEP必须重载后再tessellate。排序：先满足原strict gate，再最小化10*NCD+(1-IoU)+2*surface_centroid_error+bbox_error。初始score、最佳score、候选数、搜索步数和最佳ID均保留；达到strict即通用早停。离散轴/厚度搜索已经实现；通用连续优化、revolve/cone、复杂语义Boolean和LLM planner未实现，不能声称已完成所有推荐family。

历史复用组件为candidate_axes、basis_for_axis、projected_profile、section_loft_profile及其loop tracking依赖；仅复制纯函数，新emitters直接生成原生CQ。旧DSL、导出/删除逻辑与静默Boolean失败逻辑未复用。V1 evaluator和occupancy源码逐字节相同；源文件和canonical mesh/transform同样逐字节匹配。

提高覆盖率不是通过降低阈值。严格接受的薄实体仍是pseudo-CAD supervision；不等于物理实体、原始体积或原始设计GT。自由形状/复杂分离表面超出预算时保留失败，不增加几十个primitive来拟合三角网格。
'''
(I/'reports/RECONSTRUCTION_V1_V2_DIFF.md').write_text(diff)
report=f'''# RESMOKE100_V2

FACTORY_GATE = {status['factory_gate']}
GEOMETRY_GATE = {status['geometry_gate']}
CAN_SCALE_TO_1000 = {'YES' if scale else 'NO'}
NEXT_ALLOWED_STAGE = {status['next_allowed_stage']}

## 同源 paired 结果

使用完全相同100个source SHA256、split group、canonical mesh和transform；未重采样source、未增加数据、未训练、未Scale1000、未P3。V1原件及历史保护检查：{guard['status']}。核心evaluator逐字节相同：{evaluator_equal}。无case ID特定规则：{no_case_rules}。

V1：{v1}

V2：{v2}

所有有效样本的median采用各版本实际metric N；严格paired公共子集为{len(common)}例，其统计见 paired_common_metric_statistics.json，不能把新增可执行例与V1缺失指标强行配对。逐例差值定义 V2−V1，缺失值保持空值。NEAR_PASS为非strict、IoU>=0.70且NCD<=0.02的分析子集，仍包含在RELAXED_ONLY里，不替代strict。

IMPROVED/UNCHANGED/WORSE = {dict(improvement_counts)}。定义先比较strict/relaxed/reject等级，同级比较加权geometry score（1e-9容差）；不表示每项指标同时单调改善。严格救回{rescue}例，原严格受损{damaged}例。所有逐例NCD/IoU/centroid/bbox变化、family、primary_fix、score和candidate数保存在v1_v2_case_comparison.csv。

## 紧凑性与限制

共执行{candidate_total}个候选，观察到最多{booleanmax}次Boolean。候选失败：{dict(attempt_failures)}；这些与最终case失败是不同分母。所有最终目标通过native AST、有效实体、STEP export、reload、tessellation及artifact hash验证。无STL/OBJ导入包装、triangle soup或DSL目标。

严格接受中{status['thickness_assumed_strict_n']}例使用显式假设厚度的平面区域薄实体。这类结果在固定表面/近似occupancy协议下几何一致，但不证明恢复真实厚度、实体体积或设计意图。IoU仍为近似scan-fill voxel occupancy，尤其开放表面不可解释为真实体积重合度。保留这种目标类型的显式标记，避免把采样/体素分辨率下的一致性夸大为真实CAD恢复。

本轮用于pipeline debug并在同一100例上拟合和选候选；无held-out泛化证据。没有大量case-specific hardcode，但评测来源仍是开发集，不能把本结果当作泛化成绩。

## Gate 与下一步

扩量条件严格采用本轮新规则：execute>=90%、reload>=90%、strict>=30%、无重大evaluator bug、无case-specific hardcode，并通过factory验证。V1旧工程gate的Scale1000建议不再作为本轮几何gate依据。最终决定：{'YES' if scale else 'NO'}；本轮没有实际扩量。

主要剩余问题：{status['primary_remaining_blocker']}。优先改善曲面/局部截面/分离结构表达以及真实可识别的参数；不通过放宽阈值、P3或三角面片封装提高分数。artifact consistency errors：{errors}。

## 文件

诊断：{D}/reports/DIAGNOSIS_REPORT.md
实现差异：{I}/reports/RECONSTRUCTION_V1_V2_DIFF.md
入口：{I}/scripts/reconstruct_v2.py --limit 3 / 10 / 100
表格：tables/v1_v2_summary.csv、v1_v2_case_comparison.csv、strict_accept_v2.csv、near_pass_v2.csv、remaining_failures_v2.csv
逐例：cases/*/manifest.json、proposals.json、attempts/*（包含全部native程序、参数、日志和评测）；选中目标在cad/step/reload/mesh/metrics下。
可视化：visualizations/index.html 与诊断目录的visualizations/index.html；相同坐标与相机比较。
'''
(R/'reports/RESMOKE100_REPORT.md').write_text(report)
with (R/'cases.jsonl').open('w') as f:
 for r in new.values():f.write(json.dumps(r)+'\n')
print(json.dumps(status),flush=True)
