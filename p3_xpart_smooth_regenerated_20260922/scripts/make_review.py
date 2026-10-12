"""Build an offline review gallery and an honest final inventory."""
from pathlib import Path
import json,csv,shutil,zipfile
from collections import Counter
from PIL import Image
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
out=ROOT/'review';out.mkdir(exist_ok=True);(out/'thumbs').mkdir(exist_ok=True)
rows=json.loads((ROOT/'manifest.json').read_text());summary=json.loads((ROOT/'summary.json').read_text())
records=[]
for i,r in enumerate(rows):
    od=ROOT/'cases'/r['case_id']/r['part_id'];rec={k:r.get(k) for k in ('case_id','part_id','status','method','quality','cad_faces','cad_solids','boundary_count','seam_count','artifacts_complete','error','visual_review')}
    rec['server_path']=str(od)
    audit=ROOT/'validation'/r['case_id']/(r['part_id']+'.json')
    rec['rebuild_verified']=json.loads(audit.read_text()).get('passed',False) if audit.exists() else False
    for name,key,width in [('source_vs_cad.png','comparison',1000),('surface_boundaries.png','boundaries',900)]:
        p=od/name
        if p.exists():
            dest=out/'thumbs'/f'{i:04}_{key}.jpg'
            with Image.open(p) as im:im.thumbnail((width,1000));im.convert('RGB').save(dest,quality=88,optimize=True)
            rec[key]=str(dest.relative_to(out))
    records.append(rec)
status=summary['status_counts'];audit_summary=json.loads((ROOT/'validation/summary.json').read_text()) if (ROOT/'validation/summary.json').exists() else {}
readme=f'''# X-Part 重新拟合 CAD：交付与验收说明

输入：`/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases`

完整输出：`{ROOT}`

本轮对 {summary['cases']} 个非 tank case 的 {summary['total_parts']} 个 OBJ 零件重新拟合，tank 跳过。原网格只读，逐件记录并复核 SHA-256；未将旧 CAD 复制为本轮结果，也未使用三角片缝合 B-Rep 作为兜底。

## 实际状态

{json.dumps(status,ensure_ascii=False)}

完整成果包数量：{summary['complete_artifact_count']}。独立重建审核：{audit_summary.get('passed','尚未完成')} / {audit_summary.get('total','尚未完成')}。

`ACCEPTED` 表示有效 CAD 且通过本次采样误差阈值；不是制造公差认证，也不表示所有零件都经过逐件外观验收。`NEEDS_REFINEMENT` 是有可查看的 CAD 但误差超限或已发现外观缺陷。`FAILED` / `TIMEOUT` / `INCOMPLETE` 不算交付成功。

## 生成方法

从各零件原始 OBJ 重新采样、剖切，按形状选择球面、轮廓拉伸、样条剖面旋转、周期 B 样条截面曲面或含分支及孔洞的多曲面组合。只在拟合输入过密时进行简化，最终距离仍针对完整源网格。

旋转剖面按多段构造。部分周期 NURBS 面沿参数方向分为六条面片，保留同一几何曲面，便于显示真实 B-Rep 面片边界。因此图中的部分线是建模分面边界，不代表原物体存在棱线；没有将轮廓线伪装成 B-Rep 边界。

所有成功输出均经过 STEP 回读。显示用三角网格和曲线来自该 STEP；OpenCASCADE 提取边、识别周期接缝，主图隐藏接缝。每条曲线保存 256 个点，优先等弧长采样，失败时在 JSON 中明确记录均匀参数采样。边界数量随零件变化，不固定为轮胎的 9 条。

VTK 使用正交相机、平滑法线和抗锯齿；Pillow 排版。边界图 2000×1630，源网格与 CAD 对比图 2000×860，左右采用同一坐标变换与比例。

## 验证与限制

对 STEP 回读后的网格与完整源网格分别采样 10,000 点，计算双向点到三角面的距离。距离按源包围盒对角线归一化：平均值 ≤ 0.3%，P95 ≤ 1%，采样最大值 ≤ 4%。当原网格有有效体积时，体积误差另要求 ≤ 10%。采样最大值不是精确 Hausdorff 上界，不能保证捕捉所有细小孔洞、尖角或波纹。

对非封闭源网格，体积项不适用；CAD 封口、孔洞和分支连接包含拟合推断。复杂曲面可能有波纹、细节损失或局部拓扑差异；请通过预览与报告确认使用范围。未达到条件的零件已单独列出，不计入通过数。

几何保留原始数值坐标、位置和比例。输入未提供物理单位，STEP 的单位声明不构成对真实毫米尺寸的确认。装配或加工前需要核对单位。

独立审核将 `cad.py` 单独复制到临时目录执行，不读取源网格；比较新 STEP 的有效性、面/边/实体数、包围盒、面积、体积及曲面距离，并核对边界采样与图片尺寸。若独立三角化造成采样差异，用有效曲面点的 B-Rep 距离进一步校验。详情在服务器 `validation/`。

## 文件与复现

每个零件位于 `cases/<case>/PART_###/`，包含 `cad.py`、`parameters.json`、`model.step`、`model.brep`、`model.stl`、`curves.json`、`curve_samples_256.npz`、`render_transform.json`、两张 PNG 及 `report.json`。失败条目可能没有全部文件。

在安装 CadQuery 2.6.1、NumPy 的 Python 环境中，把单个 `cad.py` 复制到新目录，然后运行 `python cad.py`，即可生成该目录中的 STEP/BREP/STL。脚本内嵌拟合参数和构造代码，不依赖原 OBJ。

批处理与渲染代码位于 `scripts/`。环境还使用 trimesh 4.11.5、SciPy、Shapely、Open3D、VTK 9.3.1、Pillow；Linux 无显示器渲染通过 `xvfb-run -a` 启动，中文字体为 `scripts/msyh.ttc`。完整重新拟合命令：`xvfb-run -a python3 scripts/regenerate_smooth.py --workers 16 --force`。该命令会更新本输出目录，请先备份需要保留的结果。

离线打开 `index.html` 查看全部零件的压缩预览；原尺寸 PNG 和 CAD 文件保存在上述服务器路径。`manifest.csv`、`manifest.json` 和 `summary.json` 提供逐件指标及汇总。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8');(out/'README.md').write_text(readme,encoding='utf-8')
for name in ('summary.json','manifest.json','delivery_receipt.json'):
    if (ROOT/name).exists():shutil.copy2(ROOT/name,out/name)
fields=['case_id','part_id','status','method','rebuild_verified','cad_faces','cad_solids','boundary_count','seam_count','artifacts_complete','mean_distance_pct_diagonal','p95_distance_pct_diagonal','sampled_max_distance_pct_diagonal','volume_error_pct','server_path']
with (out/'manifest.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
    for r in records:w.writerow({**r,**(r.get('quality') or {})})
template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X-Part CAD 重新生成预览</title>
<style>body{margin:0;background:#f1f5f8;color:#203d50;font:15px system-ui,"Microsoft YaHei",sans-serif}header,main{max-width:1480px;margin:auto;padding:24px}h1{font-size:28px;margin:0 0 14px}p{line-height:1.7}nav{display:flex;gap:12px;flex-wrap:wrap;position:sticky;top:0;background:#f1f5f8;padding:12px 0;z-index:1}select,input,button{padding:10px;border:1px solid #acbfcb;border-radius:6px;background:white;color:#203d50}input{min-width:260px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));gap:18px}.card{background:white;border:1px solid #d4e0e8;border-radius:10px;overflow:hidden}.card h2,.info{margin:14px 18px;font-size:16px;overflow-wrap:anywhere}.card img{display:block;width:100%;height:auto}.badge{display:inline-block;padding:4px 9px;border-radius:5px;background:#fff0e0;color:#995018}.ok{background:#e0f2e9;color:#256b45}.bad{background:#f8dfdf;color:#9a3434}.meta{font-size:13px;color:#536c7c;line-height:1.8}.links{display:flex;gap:20px;margin:12px 18px}a{color:#245f89}details{margin:12px 18px;overflow-wrap:anywhere}code{font-size:12px}#more{display:block;margin:24px auto}@media(max-width:600px){.grid{grid-template-columns:1fr}header,main{padding:14px}}</style>
<header><h1>X-Part · 重新拟合 CAD</h1><p id="totals"></p><p>同一个 STEP 生成曲面与 B-Rep 边界。下方对比图：左为原网格，右为新拟合 CAD。<b>“通过”指采样误差检查通过，不能代替制造公差及逐件外观验收。</b> tank 已跳过。</p><a href="README.md">生成与验证说明</a> · <a href="manifest.csv">逐件 CSV</a> · <a href="summary.json">汇总 JSON</a></header>
<main><nav><input id="search" placeholder="搜索 case / PART"><select id="case"><option value="">全部 case</option></select><select id="status"><option value="">全部状态</option><option>ACCEPTED</option><option>NEEDS_REFINEMENT</option><option>FAILED</option><option>TIMEOUT</option><option>INCOMPLETE</option></select><span id="count"></span></nav><div class="grid" id="grid"></div><button id="more">再显示 60 件</button></main>
<script>const rows=__DATA__;const summary=__SUMMARY__;const labels={ACCEPTED:'采样误差通过',NEEDS_REFINEMENT:'待改进',FAILED:'生成失败',TIMEOUT:'超时',INCOMPLETE:'成果不完整'};const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let limit=60;const el=id=>document.getElementById(id);el('totals').textContent=`${summary.cases} 个 case · ${summary.total_parts} 个零件 · ${summary.complete_artifact_count} 个完整成果包 · `+Object.entries(summary.status_counts).map(([k,v])=>`${labels[k]||k} ${v}`).join(' / ');[...new Set(rows.map(r=>r.case_id))].sort().forEach(c=>{let o=document.createElement('option');o.value=o.textContent=c;el('case').append(o)});function draw(){const term=el('search').value.toLowerCase();const selected=rows.filter(r=>(!el('case').value||r.case_id===el('case').value)&&(!el('status').value||r.status===el('status').value)&&`${r.case_id} ${r.part_id}`.toLowerCase().includes(term));el('count').textContent=`${selected.length} 件`;el('grid').innerHTML=selected.slice(0,limit).map(r=>{let q=r.quality||{};return `<article class="card"><h2>${esc(r.case_id)} / ${esc(r.part_id)}</h2><div class="info"><span class="badge ${r.status==='ACCEPTED'?'ok':r.status==='NEEDS_REFINEMENT'?'':'bad'}">${esc(labels[r.status]||r.status)}</span><div class="meta">${esc(r.method)} · P95 ${q.p95_distance_pct_diagonal?.toFixed(3)??'—'}% · ${r.boundary_count??'—'} 条边界 / ${r.seam_count??'—'} 条接缝<br>独立重建审核：${r.rebuild_verified?'通过':'未通过或未完成'}</div></div>${r.comparison?`<a href="${r.comparison}" target="_blank"><img src="${r.comparison}" loading="lazy" alt="源网格与 CAD 对比"></a>`:'<p class="info">没有完整预览</p>'}<div class="links">${r.comparison?`<a href="${r.comparison}" target="_blank">放大对比图</a>`:''}${r.boundaries?`<a href="${r.boundaries}" target="_blank">四视图与 B-Rep 边界</a>`:''}</div><details><summary>服务器文件位置与备注</summary><p><code>${esc(r.server_path)}</code></p><p>${esc(r.error||r.visual_review||'完整 CAD、原尺寸 PNG 和报告保存在此目录。')}</p></details></article>`}).join('');el('more').hidden=selected.length<=limit}['search','case','status'].forEach(id=>el(id).addEventListener('input',()=>{limit=60;draw()}));el('more').onclick=()=>{limit+=60;draw()};draw();</script></html>'''
data=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
(out/'index.html').write_text(template.replace('__DATA__',data).replace('__SUMMARY__',json.dumps(summary)),encoding='utf-8')
with zipfile.ZipFile(ROOT/'review.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(out))
print(json.dumps(dict(review=str(out),parts=len(records),archive_bytes=(ROOT/'review.zip').stat().st_size)))
