import json,sys,csv,shutil,zipfile
from pathlib import Path
import cadquery as cq
import trimesh
import numpy as np

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
delivery=ROOT/'deliverables'
delivery.mkdir(exist_ok=True)
rows=[]
for case in manifest['cases']:
    name=case['case']
    inputs=[trimesh.load(p['input_stl'],force='mesh',process=False) for p in case['parts']]
    source=trimesh.util.concatenate(inputs)
    source_folder=delivery/'input_parts'/name
    source_folder.mkdir(parents=True,exist_ok=True)
    source.export(source_folder/'assembled_input.stl')
    for meta in case['parts']:
        shutil.copy2(meta['input_stl'],source_folder/(meta['part']+'.stl'))
    for method in ['cadrille','cadrecode']:
        folder=delivery/method/name;folder.mkdir(parents=True,exist_ok=True)
        assembly=cq.Assembly(name=name)
        records=[];meshes=[]
        for meta in case['parts']:
            p=ROOT/method/name/meta['part']/'STATUS.json'
            r=json.loads(p.read_text()) if p.exists() else dict(status='NOT_RUN',part=meta['part'])
            auditdir=folder/'parts'/meta['part']/'attempts'
            for attempt in p.parent.glob('attempt_*'):
                dst=auditdir/attempt.name;dst.mkdir(parents=True,exist_ok=True)
                for f in ['raw.txt','cadquery.py','EXECUTION.json','execution.log']:
                    if (attempt/f).exists():shutil.copy2(attempt/f,dst/f)
            if r.get('status')=='PASS':
                try:
                    step=Path(r['world_step'])
                    shape=cq.importers.importStep(str(step)).val()
                    assert shape.isValid() and len(shape.Solids())>0
                    assembly.add(shape,name=meta['part'])
                    partdir=folder/'parts'/meta['part'];partdir.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(step,partdir/'world.step')
                    shutil.copy2(step.parent/'cadquery.py',partdir/'cadquery.py')
                    shutil.copy2(Path(meta['input_stl']).parent/'transform.json',partdir/'transform.json')
                    mesh=trimesh.load(step.parent/'world.stl',force='mesh',process=False)
                    meshes.append(mesh)
                except Exception as e:r.update(status='FINAL_VALIDATION_FAIL',error=repr(e))
            records.append(r)
        passed=sum(r['status']=='PASS' for r in records)
        status='COMPLETE' if passed==case['required_parts'] else 'PARTIAL' if passed else 'FAILED'
        if passed:
            assembly.save(str(folder/'assembled.step'))
            check=cq.importers.importStep(str(folder/'assembled.step')).val()
            assert check.isValid(),(method,name)
            trimesh.util.concatenate(meshes).export(folder/'assembled.stl')
        summary=dict(method=method,case=name,status=status,valid_parts=passed,required_parts=case['required_parts'],missing_parts=[r['part'] for r in records if r['status']!='PASS'],parts=records)
        (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
        rows.append({k:v for k,v in summary.items() if k!='parts'})
        print(method,name,status,passed,case['required_parts'],flush=True)
(delivery/'SUMMARY.json').write_text(json.dumps(rows,indent=2))
with (delivery/'summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
shutil.copy2(ROOT/'MANIFEST.json',delivery/'MANIFEST.json')
shutil.copy2(ROOT/'INPUT_COORDINATE_AUDIT.json',delivery/'INPUT_COORDINATE_AUDIT.json')
for file in ['run_inference.py','cadrecode_model.py','export_part.py','prepare_run.py','finalize_run.py','launch_run.py','regenerate_case.py','render_results.py']:
    (delivery/'scripts').mkdir(exist_ok=True);shutil.copy2(ROOT/file,delivery/'scripts'/file)
lines=['# Cadrille / CAD-Recode 分零件生成与装配','', '21 个案例，306 个 X-Part 零件，两种方法使用完全相同的输入。','', '流程：已有 X-Part 拆分 → 点云归一化与 256 点最远点采样 → 各模型生成 CadQuery → 有效实体与 STEP 重读检查 → 逆变换回原位 → 命名零件 STEP 装配。','', '坐标公式：point=(world-center)*2/extent；world=CAD*extent/200+center。没有按预测包围盒拟合尺寸。单位沿用输入网格，不能据此认定毫米。','', '每个失败零件最多使用三次固定种子的点云重采样；模型权重不变，不用其他方法的零件填补。COMPLETE 表示输入零件都得到有效 CAD，不代表几何完全复原；PARTIAL 缺件列表详见 SUMMARY.json。','', '每个案例目录含 assembled.step、assembled.stl、parts/*/world.step、原始 CadQuery 及 transform.json。原始 CadQuery 位于模型规范坐标系，world.step 已还原到装配坐标。','', '|方法|完整案例|有效零件|','|---|---:|---:|']
for method in ['cadrille','cadrecode']:
    rr=[r for r in rows if r['method']==method]
    lines.append(f"|{method}|{sum(r['status']=='COMPLETE' for r in rr)}/21|{sum(r['valid_parts'] for r in rr)}/306|")
lines += ['', '输入说明：沿用服务器已有 X-Part 完整/补全部件。本次没有重新训练分割模型。鸟屋、音箱、酒架的部件合并边界与原始整网格存在约 15%–22% 的最大边界偏差；详见 INPUT_COORDINATE_AUDIT.json。预览中的 Input 是实际送入两种方法的部件合并网格。', '', '编辑后重建：安装 CadQuery，在 scripts 目录运行 python regenerate_case.py ../cadrille/案例名（或 ../cadrecode/案例名），生成 edited_assembled.step。']
(delivery/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print('FINALIZED',delivery,flush=True)
