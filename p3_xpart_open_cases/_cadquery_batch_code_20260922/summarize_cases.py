from pathlib import Path
import json,html,shutil,zipfile,collections
from PIL import Image,ImageDraw,ImageFont
from rebuild_cases import ROOT,RUN,dump

def summarize():
    manifest=json.loads((RUN/'task_manifest.json').read_text());cases={};parts=[];validation=collections.Counter();termination=collections.Counter()
    for name,pid in manifest['tasks']:
        folder=ROOT/name/'xpart_parts_cadquery_features'/pid
        if (folder/'job_status.json').exists():r=json.loads((folder/'job_status.json').read_text())
        else:r=dict(case=name,part=pid,status='PENDING')
        if (folder/'rebuild_validation.json').exists():v=json.loads((folder/'rebuild_validation.json').read_text());r['validation']=v['status'];validation[v['status']]+=1
        else:r['validation']='PENDING'
        termination[r.get('termination','pending')]+=1;parts.append(r);cases.setdefault(name,[]).append(r)
    rows=[]
    for name,rs in cases.items():
        ar=ROOT/name/'xpart_parts_cadquery_assembly'/'assembly_report.json'
        assembly=json.loads(ar.read_text()) if ar.exists() else {}
        counts=collections.Counter(r['status'] for r in rs)
        row=dict(case=name,parts=len(rs),accepted=counts['APPROXIMATION_ACCEPTED'],needs_refinement=counts['NEEDS_REFINEMENT'],failed=counts['FAILED'],pending=counts['PENDING'],verified=sum(r['validation']=='VERIFIED' for r in rs),assembly_complete=assembly.get('complete_assembly',False),solids=assembly.get('solid_count',0))
        rows.append(row)
    summary=dict(cases=len(rows),parts=len(parts),counts=dict(collections.Counter(r['status'] for r in parts)),validation=dict(validation),termination=dict(termination),complete_assemblies=sum(r['assembly_complete'] for r in rows),case_results=rows,part_results=parts)
    dump(RUN/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['case_results','part_results']},indent=2))
    issue=[dict(case=r['case'],part=r['part'],status=r['status'],validation=r['validation'],method=r.get('method'),quality=r.get('quality'),termination=r.get('termination')) for r in parts if r['status']!='APPROXIMATION_ACCEPTED' or r['validation']!='VERIFIED']
    dump(RUN/'needs_review.json',issue)
    previews=RUN/'previews';previews.mkdir(exist_ok=True)
    cards=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    pages=[]
    for page_start in range(0,len(rows),20):
        page=Image.new('RGB',(1800,5*330+80),'#f2f7fa');draw=ImageDraw.Draw(page);draw.text((25,20),f'CadQuery case overview | {page_start+1}-{min(page_start+20,len(rows))} / {len(rows)}',font=font,fill='#203c50')
        for ix,r in enumerate(rows[page_start:page_start+20]):
            name=r['case'];a=ROOT/name/'xpart_parts_cadquery_assembly';png=a/f'{name}_assembly.png';x=ix%4*450;y=ix//4*330+65
            if png.exists():
                im=Image.open(png);im.thumbnail((450,265));page.paste(im,(x+(450-im.width)//2,y));shutil.copy2(png,previews/png.name)
            draw.text((x+12,y+267),name[:39],font=font,fill='#203c50');draw.text((x+12,y+292),f"{r['accepted']} pass / {r['needs_refinement']} review / {r['failed']} fail",font=font,fill='#576b79')
        fn=f'gallery_{page_start//20+1}.jpg';page.save(RUN/fn,quality=90);pages.append(fn)
    for r in rows:
        name=r['case'];safe=html.escape(name);base='../'+name+'/xpart_parts_cadquery_assembly/';links=' · '.join(f'<a href="{base}{name}{suffix}">{label}</a>' for suffix,label in [('_viewer.html','交互装配/爆炸'),('_assembly.step','STEP'),('_comparison.png','原网格对比'),('_multiview.png','四视图')])
        cards.append(f'<article data-name="{safe}"><img loading="lazy" src="previews/{safe}_assembly.png"><h2>{safe}</h2><p>{r["parts"]} 件 · {r["accepted"]} 通过筛选 · {r["needs_refinement"]} 待细化 · {r["failed"]} 失败<br>{r["verified"]} 件代码复建已验证</p><p>{links}</p></article>')
    doc='<!doctype html><html lang="zh"><meta charset="utf-8"><title>CadQuery cases</title><style>body{font:15px system-ui;background:#eff4f8;color:#18384d;margin:30px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}article{background:white;padding:18px;border-radius:12px}img{width:100%;aspect-ratio:1.375;object-fit:contain}h2{font-size:17px;overflow-wrap:anywhere}a{color:#25638b}input{padding:12px;margin:20px 0;width:300px}p{line-height:1.7}</style>'
    doc+=f'<h1>{len(rows)} 个 case · {len(parts)} 个零件</h1><p>标准操作 CadQuery 近似重建：拉伸、旋转、放样、少量轮廓凸台。并非原设计特征树。<br>筛选阈值：P95 距离 ≤ 包围盒对角线 1%，采样最大距离 ≤ 4%，体积误差 ≤ 10%。不代表制造公差。</p><p><a href="summary.json">完整统计</a> · <a href="needs_review.json">待检查清单</a></p><input id="q" placeholder="按 case 名称搜索"><main>'+''.join(cards)+'</main><script>q.oninput=()=>document.querySelectorAll("article").forEach(a=>a.hidden=!a.dataset.name.includes(q.value.toLowerCase()))</script></html>'
    (RUN/'index.html').write_text(doc,encoding='utf-8')
    lines=['# Other cases CadQuery reconstruction','',f'Cases: {len(rows)}; parts: {len(parts)}.',f'Status counts: {summary["counts"]}',f'Independent rebuild validation: {dict(validation)}','', 'All input source files are preserved. Coordinates retain the input numeric scale; physical units are unknown.', 'Each case contains xpart_parts_cadquery_features (standalone scripts, STEP, parameters, quality reports) and xpart_parts_cadquery_assembly (assembly STEP, PNG, offline viewer with explosion slider).','', 'APPROXIMATION_ACCEPTED means exploratory shape screening passed, not engineering tolerance or original feature-history recovery. NEEDS_REFINEMENT remains a valid approximate CAD model. Loft sketches can contain many spline points. Multiple solids are reported explicitly. Explosion is illustrative, not an inferred disassembly sequence.','', '| Case | Parts | Accepted | Review | Failed | Verified |','|---|---:|---:|---:|---:|---:|']
    lines += [f'| {r["case"]} | {r["parts"]} | {r["accepted"]} | {r["needs_refinement"]} | {r["failed"]} | {r["verified"]} |' for r in rows]
    (RUN/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    with zipfile.ZipFile(RUN/'case_overview.zip','w',zipfile.ZIP_DEFLATED) as z:
        for fn in ['README.md','summary.json','needs_review.json',*pages]:z.write(RUN/fn,fn)
        for f in previews.iterdir():z.write(f,'previews/'+f.name)
    return summary
if __name__=='__main__':summarize()
