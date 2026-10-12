from pathlib import Path
import json,csv,hashlib,collections,time
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/partsam')
SRC=ROOT/'PartObjaverse-Tiny_instance_stl'
OUT=ROOT/'PartObjaverse-Tiny_instance_cad'
def main():
    files=sorted(SRC.rglob('*.stl'));records=[];problems=[]
    inventory={r['relative']:r for r in json.loads((OUT/'input_inventory.json').read_text())}
    counts=collections.Counter();kinds=collections.Counter();degenerate_total=0;degenerate_files=0;subtolerance_total=0;subtolerance_files=0
    roundtrip_max=0.0;bounds_max=0.0;output_bytes=0
    for source in files:
        relative=str(source.relative_to(SRC));folder=OUT/source.relative_to(SRC).parent
        report_path=folder/(source.stem+'_report.json')
        if not report_path.is_file():problems.append({'relative_path':relative,'error':'missing report'});continue
        r=json.loads(report_path.read_text());records.append(r);counts[r['status']]+=1
        current_hash=hashlib.sha256(source.read_bytes()).hexdigest()
        if current_hash!=inventory[relative]['sha256']:problems.append({'relative_path':relative,'error':'source changed since inventory'})
        if r['status']!='SUCCESS':continue
        if r['source_sha256']!=current_hash:problems.append({'relative_path':relative,'error':'output refers to different source content'})
        for suffix in ['_cad.py','.step','.brep']:
            p=folder/(source.stem+suffix)
            if not p.is_file() or p.stat().st_size==0:problems.append({'relative_path':relative,'error':'missing '+suffix})
            else:output_bytes+=p.stat().st_size
        if not r['cad']['valid'] or not r['step_reimport']['valid']:problems.append({'relative_path':relative,'error':'CAD or STEP invalid'})
        skipped=len(r.get('degenerate_faces_skipped',[]));degenerate_total+=skipped;degenerate_files+=int(skipped>0)
        tiny=len(r.get('subtolerance_faces_skipped',[]));subtolerance_total+=tiny;subtolerance_files+=int(tiny>0)
        expected=r['input_faces']-skipped-tiny
        if expected!=r['cad']['faces']:problems.append({'relative_path':relative,'error':'source versus CAD face count mismatch','expected':expected,'actual':r['cad']['faces']})
        kinds[r['representation']]+=1
        roundtrip_max=max(roundtrip_max,r['roundtrip_bounds_max_error'])
        bounds_max=max(bounds_max,float(np.max(np.abs(np.asarray(r['cad']['bounds'])-np.asarray(r['input_bounds'])))))
    summary={'total_stl':len(files),'source_folders':len({p.parent for p in files}),
             'reports':len(records),'status_counts':dict(counts),'representation_counts':dict(kinds),
             'source_hashes_unchanged':not any('source' in p['error'] for p in problems),
             'integrity_problem_count':len(problems),'integrity_problems':problems,
             'degenerate_triangles_skipped':degenerate_total,'files_with_degenerate_triangles':degenerate_files,
             'subtolerance_triangles_skipped':subtolerance_total,'files_with_subtolerance_triangles':subtolerance_files,
             'max_step_roundtrip_bounds_error':roundtrip_max,'max_source_to_cad_bounds_error':bounds_max,
             'cad_and_code_size_gb':output_bytes/1e9,
             'all_converted':len(records)==len(files) and counts['SUCCESS']==len(files) and not problems}
    (OUT/'FINAL_AUDIT.json').write_text(json.dumps(summary,indent=2))
    text=['# 批量 CAD 转换结果','',f"输入文件夹：{summary['source_folders']}",f"STL 总数：{len(files)}",f"成功：{counts['SUCCESS']}；失败：{counts['FAILED']}",
          f"类型：{dict(kinds)}",f"原始文件 SHA-256 保持一致：{summary['source_hashes_unchanged']}",f"完整性异常：{len(problems)}",f"代码和 CAD 文件共约 {output_bytes/1e9:.3f} GB",'',
          '输出目录：`'+str(OUT)+'`','',
          '每个源文件对应独立建模代码（内嵌网格数据）、STEP、BREP、验证报告。',
          '开放输入保留为 CAD 曲面；闭合输入转为实体。几何由三角平面构成，未推断原始设计特征。',
          '所有成功 STEP 已重新导入检查；源文件未覆盖。STL 单位未知，保留原始数值和坐标。',
          f'零面积退化三角面跳过 {degenerate_total} 个，涉及 {degenerate_files} 个文件，详见每件报告。',
          f'另外跳过内核精度以下的狭长三角面 {subtolerance_total} 个，涉及 {subtolerance_files} 个文件；最小高阈值 1e-7（原始数值单位），所有索引记录在每件报告中。']
    (OUT/'FINAL_REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
