import sys,pathlib,json,collections,csv,hashlib,subprocess,concurrent.futures,os
import numpy as np
from fusion_units_probe import R,B,step,ratio,save
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2'
P=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v1'
def main():
 rows=json.loads((O/'results602.json').read_text());old=[r for r in json.loads((B/'reports/AUDITED_ROWS_WITH_IDENTITIES.json').read_text()) if r['dataset']=='fusion360']
 if len(sys.argv)>1 and sys.argv[1]=='--baseline':
  r=rows[int(sys.argv[2])]
  try:print(json.dumps(ratio(step(B/'replay'/r['cad_id']/'reconstructed.step'),r['source_geometry'])))
  except Exception as e:print(json.dumps({'error':repr(e)}))
  return
 def baseline(i):
  try:
   env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='')
   p=subprocess.run([sys.executable,'-B',__file__,'--baseline',str(i)],capture_output=True,text=True,timeout=60,env=env)
   if p.returncode:return {'error':'isolated STEP reader exit '+str(p.returncode),'stderr':p.stderr[-1000:]}
   return json.loads(p.stdout.strip().splitlines()[-1])
  except Exception as e:return {'error':repr(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:baseline_rows=list(pool.map(baseline,range(len(rows))))
 save(O/'baseline_ratios_isolated.json',baseline_rows)
 assert len(rows)==len(old)==602 and len({r['cad_id'] for r in rows})==602
 before={r['cad_id']:r for r in old};evidence=[];riskrows=[]
 for idx,r in enumerate(rows):
  b=before[r['cad_id']];entry=dict(cad_id=r['cad_id'],before_chamfer=b.get('chamfer_rel'),after_chamfer=r.get('chamfer_rel'),before_coverage=b.get('coverage_02'),after_coverage=r.get('coverage_02'),after_label_pass=r.get('label_gate'),failure_stage=r.get('failure_stage'),after_ratios=r.get('scale_ratios'))
  br=baseline_rows[idx]
  if 'error' in br:entry['before_ratio_unavailable']=br
  else:entry['before_ratios']=br
  evidence.append(entry)
  parent=pathlib.Path(r['source_step']).parent;src=json.loads((parent/'source.json').read_text());entities=src.get('entities',{});types=collections.Counter(entities.get(t.get('entity'),{}).get('type','MISSING') for t in src.get('timeline',[]));conv=json.loads((parent/'meta.json').read_text()).get('conversion',{})
  risks=dict(cad_id=r['cad_id'],label_pass=r.get('label_gate'),timeline_types=dict(types),ignored_timeline_features={k:v for k,v in types.items() if k not in ('Sketch','ExtrudeFeature')},filtered_intersect=conv.get('filtered_intersect',0),circle_rectangle_non_one_side=[x for x in conv.get('operations',[]) if x.get('profile_kind') in ('circle','rectangle') and x.get('extent_type') not in (None,'OneSideFeatureExtentType')],negative_extent_distances=[],profile_curve_types={})
  ct=collections.Counter()
  for ent in entities.values():
   if ent.get('type')=='ExtrudeFeature':
    for key in ('extent_one','extent_two'):
     v=((ent.get(key) or {}).get('distance') or {}).get('value',0)
     if v<0:risks['negative_extent_distances'].append(v)
   if ent.get('type')=='Sketch':
    for prof in ent.get('profiles',{}).values():
     for lp in prof.get('loops',[]):
      for c in lp.get('profile_curves',[]):ct[c.get('type','MISSING')]+=1
  risks['profile_curve_types']=dict(ct);riskrows.append(risks)
 save(O/'before_after602.json',evidence);save(O/'residual_conversion_risks.json',riskrows)
 def stats(rr,after):
  ratios=[x['after_ratios' if after else 'before_ratios']['diag_ratio'] for x in evidence if x.get('after_ratios' if after else 'before_ratios')]
  return dict(total=len(rr),dsl_execution=sum(r.get('execution_ok') is True for r in rr),step_reload=sum(r.get('step_reload') is True for r in rr),bbox_dsl_over_source_median=float(np.median(ratios)),bbox_source_over_dsl_median=float(np.median(1/np.array(ratios))),bbox_measurable=len(ratios),chamfer_pass=sum(r.get('chamfer_rel',float('inf'))<=.01 for r in rr),coverage_pass=sum(r.get('coverage_02',-1)>=.98 for r in rr),joint_geometry_pass=sum(r.get('label_gate') is True for r in rr),timeouts=sum(r.get('failure_stage')=='timeout' for r in rr),geometry_measurable=sum('chamfer_rel' in r for r in rr),chamfer_median=float(np.median([r['chamfer_rel'] for r in rr if 'chamfer_rel' in r])))
 a=stats(old,False);z=stats(rows,True);verify=json.loads((O/'after_v1_hashes.json').read_text());timeout=[r for r in rows if r['cad_id']=='fusion360__23658_c75a430c_0000'][0]
 risksummary={k:dict(total=sum(bool(r[k]) for r in riskrows),nonpassing=sum(bool(r[k]) and r['label_pass'] is not True for r in riskrows)) for k in ('ignored_timeline_features','filtered_intersect','circle_rectangle_non_one_side','negative_extent_distances')}
 gate=dict(CURRENT_GATE='FUSION360_UNIT_LABEL_GEOMETRY',STATUS='BLOCKED_RESIDUAL_LABEL_GEOMETRY',UNIT_METADATA_CONTRACT_COUNT=sum((O/'samples'/r['cad_id']/'unit_contract.json').exists() for r in rows),before=a,after=z,residual_risk_counts=risksummary,execution_rate=z['dsl_execution']/602,reload_rate=z['step_reload']/602,geometry_pass_rate=z['joint_geometry_pass']/602,thresholds={'chamfer_rel_max':.01,'coverage_02_min':.98,'coverage_distance_rel':.02,'execution_rate_min':.99,'reload_rate_min':.99},v1_hash_check=verify,V2_100_STARTED=False,NEW_TRAINING_STARTED=False,TEST_METRICS_READ=False,OLD_SPLIT_MODIFIED=False,UNIFORM_SCALING_SUFFICIENT=False,previous_timeout=dict(cad_id=timeout['cad_id'],timeout_s=timeout.get('timeout_s'),status=timeout.get('failure_stage','passed'),elapsed_s=timeout.get('elapsed_s'),label_gate=timeout.get('label_gate')),grouping='2796 pack records ->2644 provisional groups; not independent CAD count; final regroup and split NOT performed')
 save(O/'UNIT_LABEL_GATE.json',gate)
 header=['cad_id','source_bbox_diag','dsl_bbox_diag','mesh_bbox_diag','surface_bbox_diag','dsl_source_ratio','mesh_source_ratio','dsl_axis_extent_ratios','dsl_volume_cuberoot_ratio']
 probes=json.loads((P/'probe20.json').read_text())
 with (O/'PROBE20.csv').open('x',newline='') as f:
  w=csv.writer(f);w.writerow(header)
  for r in probes:w.writerow([r['cad_id'],r['source']['diag'],r['dsl']['diag'],r['mesh']['diag'],r['surface']['diag'],r['dsl_over_source']['diag_ratio'],r['mesh_over_source']['diag_ratio'],json.dumps(r['dsl_over_source']['axis_extent_ratio']),r['dsl_over_source']['volume_cuberoot_ratio']])
 lines=['# Fusion360 V2 单位修复与602条复测','', '**结论：单位混用已定位并在隔离目录修正，但标签几何 Gate 未通过。V2-100与训练继续暂停。**','', '## 前后对照','', '|指标|修复前|修复后|','|---|---:|---:|']
 for title,k in [('DSL执行成功','dsl_execution'),('STEP重载成功','step_reload'),('DSL/source bbox比例中位数','bbox_dsl_over_source_median'),('source/DSL bbox比例中位数','bbox_source_over_dsl_median'),('Chamfer通过','chamfer_pass'),('coverage通过','coverage_pass'),('联合几何通过','joint_geometry_pass'),('超时/几何未知','timeouts')]:lines.append(f'|{title}|{a[k]}|{z[k]}|')
 lines+=['','分母均为602；比例中位数仅针对可测形状。注意比例方向：旧DSL/source约0.1，source/DSL约10，不是旧DSL/source约10。','', '## 定位与合同','', '20条按构造调用数分层（简单7/中等6/困难7），固定哈希排序取样，不按指标筛选。原始STEP声明centimetre，OCP读取目标MM；官方OBJ与STEP的extent约0.1，V1 pack mesh与STEP约1。旧transform却由厘米OBJ计算后直接作用于毫米STEP表面，导致canonical输入尺度错误。','', '同时，20条DSL的轴比例与体积立方根比例并不全部一致：不是单一全局缩放即可解决全部标签。单位转换因子10来源于cm→mm合同，而不是拟合Chamfer。每条合同记录source原生cm、读取mm、旧DSL cm、新DSL mm、共同canonical尺度和位移。canonical transform由源STEP bbox一次生成，surface与DSL共用；不旋转，不改变法向，保留源surface的8192行顺序。','', '每条保存旧DSL副本、旧逆变换DSL、修正毫米DSL、新canonical DSL、unit_contract、coordinate_transform、surface、reconstructed STEP与audit。旧逆变换沿用基线6位精度，单位转换不额外舍入；不在本次修改DSL拓扑/操作语义。遇到未覆盖语法立即报错，不默默保留长度参数。','', '## 冻结方法与限制','', '几何比较严格沿用旧方法：源/重建各20000个确定性面积均匀采样点，同一cad_id种子及异或种子；双向未平方NN均值/源tessellation bbox对角线；Chamfer≤0.01，源→重建距离≤0.02时coverage≥0.98。无ICP，无逐样本缩放拟合。表面文件检查8192×6。','', 'point cloud无实体体积，体积比标记为不可用；OBJ仅在watertight时报告体积。轴、bbox和CAD实体体积比保留在probe20.json与before_after602.json，不用bbox体积冒充实体体积。','', f"原超时样本仅对实际DSL重放提高一次上限到600秒：{gate['previous_timeout']}。超时保持unknown，不自动记为几何失败。",'', '## 残留错误：只诊断，不继续缩放','', '旧转换器只遍历ExtrudeFeature，跳过其他timeline类型（fusion360_to_dsl.py:332）；圆/矩形快捷分支没有传递双侧或对称拉伸参数（231–249），而polygon分支有；距离取abs（194–195）；曲线采样可能产生近似误差。这些是代码证据与候选风险，尚未证明每个失败的具体因果。', '', f'602条源JSON风险计数：{risksummary}。详情见residual_conversion_risks.json；不能仅因DSL不含LOFT/SWEEP就声称本批失败由缺少这些操作造成。','', '## 门禁与冻结','', f"V1基线哈希检查：{verify['checked']}文件，变化{len(verify['changed'])}。",'', '当前只交付单位修复与标签审计。未覆盖旧checkpoint、日志、配置、报告或split；未读取test decode或模型测试指标（使用了全库GT标签做数据质量审计）；未启动训练。旧运行未作停止/重启操作。2796是pack记录数，2644仍只是候选去重组。','', 'unit_audit_v1中的初轮复测误把source_points的8192×3当作含法向数组，在执行DSL前被schema检查阻断；记录保留，不作为前后对照。权威复测为unit_audit_v2/results602.json。','', '后续需获得授权修复DSL转换语义并复测，不制作V2-100，不改阈值。','', '## 复现','', '代码：scripts/geometry_pack_v2_mesh2cad/；fusion_units_probe.py、fusion_unit_contract.py、test_fusion_unit_contract.py、fusion_units_retest_v2.py、fusion_units_report.py。Python环境cadfit-env；CPU-only，24 workers，BLAS线程1。脚本使用排他写入，禁止直接在已完成输出目录重跑；复现须指定新的隔离输出目录。']
 with (O/'FUSION360_UNIT_REPORT.md').open('x') as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
