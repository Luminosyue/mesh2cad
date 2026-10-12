#!/usr/bin/env python3
import csv, json, math, os, shutil, subprocess, sys, traceback
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFont

import cadquery as cq

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT/'ours3/p1_val1000_qualitative_visualization_v1'
CLOSURE = ROOT/'ours3/p1_operation_aware_formal_closure_v1'
ARM_DIR = {
    'A1': ROOT/'ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1',
    'A3': ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3',
    'P1': ROOT/'ours3/p1_exact9998_val1000_eval_v2',
}
DSL2OCC = ROOT/'scripts/deepcad/dsl_to_occ.py'
PY_CAD = '/data/miniconda3/envs/cadfit-env/bin/python'

def load_rows(d):
    ans={}
    for p in sorted(d.glob('*/row.json')):
        try: ans[p.parent.name]=json.loads(p.read_text())
        except Exception: pass
    return ans

def b(v, default=False):
    if isinstance(v,bool): return v
    if v is None: return default
    return str(v).strip().lower() in ('1','true','yes','pass')

def f(v, default=None):
    try:
        x=float(v)
        return x if math.isfinite(x) else default
    except Exception:return default

def geom(r,k): return f((r.get('geometry') or {}).get(k))
def reload_pass(arm,cid,rows,reload_map):
    return reload_map.get(arm,{}).get(cid, b(rows[arm][cid].get('step_ok')))

def read_reload(name):
    p=CLOSURE/'step_reload'/f'{name}_STEP_RELOAD_AUDIT.csv'
    out={}
    with p.open(newline='') as z:
        for r in csv.DictReader(z): out[r['cad_id']]=b(r.get('reload_pass'))
    return out

def root_causes():
    p=CLOSURE/'geometry_outliers/P1_CHAMFER_TOP20_ROOT_CAUSE.csv'; out={}
    with p.open(newline='') as z:
        for r in csv.DictReader(z): out[r['cad_id']]={'category':r['category'],'evidence':r['evidence']}
    return out

def infer_root(rp, ra):
    if rp.get('op_f1',0)<0.8: return 'OPERATION_STRUCTURE_ERROR'
    hp=geom(rp,'hausdorff_95_norm'); cp=geom(rp,'chamfer_norm')
    if hp is not None and hp>0.25: return 'LOCAL_PARAMETER_ERROR'
    if cp is not None and cp>0.25: return 'SCALE_ERROR'
    return 'UNRESOLVED'

def select(rows,reloads,roots):
    ids=sorted(set(rows['A1'])&set(rows['A3'])&set(rows['P1']))
    def delta(cid): return f(rows['P1'][cid].get('op_f1'),0)-f(rows['A3'][cid].get('op_f1'),0)
    op=[c for c in ids if reload_pass('P1',c,rows,reloads) and delta(c)>0 and any(x in rows['P1'][c].get('gt_ops',[]) for x in ('Box','Extrude'))]
    op=sorted(op,key=lambda c:(-delta(c),c))[:4]
    step=[c for c in ids if not reload_pass('A3',c,rows,reloads) and reload_pass('P1',c,rows,reloads) and b(rows['P1'][c].get('parsed'))]
    step=sorted(step,key=lambda c:(-f(rows['P1'][c].get('op_f1'),0),c))[:3]
    def genbad(r): return r.get('stop_reason')=='MAX_LENGTH' or b(r.get('under_generation')) or r.get('stop_reason')!='EOS'
    gen=[c for c in ids if genbad(rows['A3'][c]) and not genbad(rows['P1'][c])]
    gen=sorted(gen,key=lambda c:(-delta(c),c))[:3]
    geo=[]
    for c in ids:
        a,p=rows['A3'][c],rows['P1'][c]; ah=geom(a,'hausdorff_95_norm'); ph=geom(p,'hausdorff_95_norm')
        if ah is not None and ph is not None and reload_pass('A3',c,rows,reloads) and reload_pass('P1',c,rows,reloads): geo.append(c)
    geo=sorted(geo,key=lambda c:(-(geom(rows['A3'][c],'hausdorff_95_norm')-geom(rows['P1'][c],'hausdorff_95_norm')),c))[:4]
    outlier=[c for c in roots if c in ids]
    outlier=sorted(outlier,key=lambda c:(-max(geom(rows['P1'][c],'chamfer_norm') or -1,geom(rows['P1'][c],'hausdorff_95_norm') or -1),c))[:3]
    placement=[c for c in outlier if roots[c]['category'] in ('ORIGIN_TRANSLATION_ERROR','SCALE_ERROR','EXTENT_ERROR','MULTIPLE') and f(rows['P1'][c].get('op_f1'),0)>=.8 and reload_pass('P1',c,rows,reloads)]
    if len(placement)<3:
        more=[c for c in ids if c not in placement and f(rows['P1'][c].get('op_f1'),0)>=.8 and reload_pass('P1',c,rows,reloads) and (geom(rows['P1'][c],'hausdorff_95_norm') or 0)>.2]
        placement += sorted(more,key=lambda c:(-(geom(rows['P1'][c],'hausdorff_95_norm') or 0),c))[:3-len(placement)]
    lim=[c for c in ids if any(x in rows['P1'][c].get('gt_ops',[]) for x in ('Cut','Union')) and f(rows['A3'][c].get('op_f1'),0)>f(rows['P1'][c].get('op_f1'),0)]
    lim=sorted(lim,key=lambda c:(-delta(c)*-1,c))[:3]
    return {'OPERATION_RESCUE':op,'STEP_RESCUE':step,'GENERATION_RESCUE':gen,'GEOMETRY_RESCUE':geo,'P1_OUTLIER':outlier,'PLACEMENT_FAILURE':placement[:3],'CUT_UNION_LIMITATION':lim}

def step_mesh(path,tol):
    wp=cq.importers.importStep(str(path)); shape=wp.val()
    vv,tt=shape.tessellate(tol,0.5)
    verts=[[q.x,q.y,q.z] for q in vv]; faces=[list(t) for t in tt]
    if not faces: raise RuntimeError('EMPTY BREP')
    return np.asarray(verts,float),np.asarray(faces,int)

def ensure_gt_step(cid):
    d=OUT/'selected_cases'/cid; d.mkdir(parents=True,exist_ok=True)
    step=d/'gt.step'; stl=d/'gt_unused.stl'
    if not step.exists():
        src=ARM_DIR['P1']/cid/'gt.dsl'
        subprocess.run([PY_CAD,str(DSL2OCC),'--dsl',str(src),'--step',str(step),'--stl',str(stl)],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
    return step

def render_panel(cid,label,step,transform,tol,row,outpng):
    fig=plt.figure(figsize=(3.0,3.0),dpi=180); ax=fig.add_subplot(111,projection='3d'); ax.set_proj_type('ortho'); ax.set_facecolor('white'); fig.patch.set_facecolor('white')
    status='PASS'
    try:
        v,fa=step_mesh(step,tol); v=(v-transform['center'])/transform['scale']
        poly=Poly3DCollection(v[fa],facecolor='#d9dee5',edgecolor='#4d5966',linewidth=.16,alpha=1.0)
        ax.add_collection3d(poly)
    except Exception as e:
        status='PARSE FAIL' if not b(row.get('parsed'),True) else ('STEP FAIL' if not step.exists() else 'INVALID BREP')
        ax.text2D(.5,.52,status,transform=ax.transAxes,ha='center',va='center',fontsize=14,color='#9b2c2c',weight='bold')
    ax.set_xlim(-.72,.72); ax.set_ylim(-.72,.72); ax.set_zlim(-.72,.72); ax.view_init(elev=24,azim=-42); ax.set_box_aspect((1,1,1)); ax.set_axis_off()
    op=f(row.get('op_f1')); cd=geom(row,'chamfer_norm'); h=geom(row,'hausdorff_95_norm'); rp=b(row.get('_reload',row.get('step_ok')))
    title=label
    if label!='GT':
        cds=f'{cd:.3f}' if cd is not None else 'NA'; hs=f'{h:.3f}' if h is not None else 'NA'
        title=f"{label}  Op-F1 {op:.2f}\nSTEP {'PASS' if rp else 'FAIL'}  CD {cds}  H95 {hs}"
    ax.set_title(title,fontsize=8,pad=1)
    plt.subplots_adjust(0,0,.99,.90); fig.savefig(outpng,bbox_inches='tight',pad_inches=.03); plt.close(fig)
    return status

def font(size,bold=False):
    paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    try:return ImageFont.truetype(paths[0],size)
    except:return ImageFont.load_default()

def gallery(rowspec,outpath,title):
    cellw=560; cellh=520; margin=80; header=120
    im=Image.new('RGB',(margin+cellw*len(rowspec[0][1]),header+cellh*len(rowspec)),'white'); d=ImageDraw.Draw(im)
    d.text((30,25),title,fill='#17202a',font=font(34,True))
    for ri,(label,panels) in enumerate(rowspec):
        d.text((10,header+ri*cellh+12),label,fill='#2c3e50',font=font(18,True))
        for ci,p in enumerate(panels):
            x=margin+ci*cellw; y=header+ri*cellh
            q=Image.open(p).convert('RGB'); q.thumbnail((cellw-16,cellh-55)); im.paste(q,(x+(cellw-q.width)//2,y+38))
            if ri==0:d.text((x+cellw//2-25,header-35),p.stem.split('__')[-1],fill='#111',font=font(20,True))
    im.save(outpath,dpi=(300,300))
    try: im.save(outpath.with_suffix('.pdf'),resolution=300)
    except Exception: pass

def main():
    for sub in ('protocol','selected_cases','renders','galleries','metadata','reports','integrity'): (OUT/sub).mkdir(parents=True,exist_ok=True)
    rows={a:load_rows(d) for a,d in ARM_DIR.items()}; reloads={a:read_reload(a) for a in ('A1','A3','P1')}; roots=root_causes()
    for a in rows:
        for c,r in rows[a].items(): r['_reload']=reloads[a].get(c,b(r.get('step_ok')))
    sel=select(rows,reloads,roots); allids=sorted(set(sum(sel.values(),[])))
    rules={
      'OPERATION_RESCUE':'max P1 Op-F1 minus A3 Op-F1; GT contains Box/Extrude; P1 reload pass',
      'STEP_RESCUE':'A3 reload fail and P1 reload pass; P1 parse pass; P1 Op-F1 descending',
      'GENERATION_RESCUE':'A3 max-length/under-generation/non-EOS to P1 EOS and not under-generated; Op-F1 gain descending',
      'GEOMETRY_RESCUE':'A3/P1 geometry valid; H95(A3)-H95(P1) descending',
      'P1_OUTLIER':'formal closure P1_CHAMFER_TOP20; max(P1 Chamfer,P1 H95) descending',
      'PLACEMENT_FAILURE':'P1 high Op-F1 and reload pass with large H95; audited cause preferred',
      'CUT_UNION_LIMITATION':'GT contains Cut/Union and A3 Op-F1 greater than P1',
    }
    protocol={'scope':'EXACT9998 frozen VAL1000 only','selection_rules':{},'tie_break':'cad_id lexical ascending','TEST_CASE_USED_N':0}
    for k,v in sel.items(): protocol['selection_rules'][k]={'rule':rules[k],'candidate_N':len(v),'N_selected':len(v),'selected':v}
    (OUT/'protocol/P1_QUALITATIVE_SELECTION_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
    render_protocol={'SOURCE':'STEP for GT/A1/A3/P1','TESSELLATION':'OCC BRepMesh_IncrementalMesh','TESSELLATION_TOLERANCE':'per-case GT bbox diagonal * 0.001, same absolute value for all models','SHARED_GT_TRANSFORM':True,'CAMERA':{'projection':'orthographic','azimuth_deg':-42,'elevation_deg':24,'axis_limits':[-.72,.72]},'PER_MODEL_AUTOFIT':False,'PER_MODEL_RECENTER':False,'PER_MODEL_RESCALE':False}
    (OUT/'protocol/P1_RENDER_PROTOCOL.json').write_text(json.dumps(render_protocol,indent=2)+'\n')
    manifest=[]; panel={}; bbox_audit={}
    for ix,cid in enumerate(allids,1):
        print(f'[{ix}/{len(allids)}] {cid}',flush=True); gt=ensure_gt_step(cid)
        gv,gf=step_mesh(gt,1e-3); mn=gv.min(0); mx=gv.max(0); center=(mn+mx)/2; scale=max(np.linalg.norm(mx-mn),1e-8); tol=max(scale*.001,1e-6)
        tr={'center':center,'scale':scale}; bbox_audit[cid]={'GT':{'min':mn.tolist(),'max':mx.tolist()},'tolerance':tol}
        panel[cid]={}
        gtrow={'op_f1':1,'parsed':True,'step_ok':True,'_reload':True,'geometry':{}}
        sources={'GT':(gt,gtrow),**{a:(ARM_DIR[a]/cid/'pred.step',rows[a][cid]) for a in ('A1','A3','P1')}}
        for label,(sp,r) in sources.items():
            out=OUT/'renders'/f'{cid}__{label}.png'; status=render_panel(cid,label,sp,tr,tol,r,out); panel[cid][label]=out
            try:
                vv,_=step_mesh(sp,tol); bbox_audit[cid][label]={'min':vv.min(0).tolist(),'max':vv.max(0).tolist(),'status':status}
            except Exception as e:bbox_audit[cid][label]={'status':status,'error':str(e)}
        cats=[k for k,v in sel.items() if cid in v]; p=rows['P1'][cid]; a3=rows['A3'][cid]; rc=roots.get(cid,{'category':infer_root(p,a3),'evidence':''})
        manifest.append({'category':'|'.join(cats),'rank':'|'.join(str(sel[k].index(cid)+1) for k in cats),'cad_id':cid,'source':p.get('dataset'),'K':p.get('gt_op_count'),'GT_ops':' > '.join(p.get('gt_ops',[])),'A1_ops':' > '.join(rows['A1'][cid].get('pred_ops',[])),'A3_ops':' > '.join(a3.get('pred_ops',[])),'P1_ops':' > '.join(p.get('pred_ops',[])),'A1_OpF1':rows['A1'][cid].get('op_f1'),'A3_OpF1':a3.get('op_f1'),'P1_OpF1':p.get('op_f1'),'A1_STEP':reload_pass('A1',cid,rows,reloads),'A3_STEP':reload_pass('A3',cid,rows,reloads),'P1_STEP':reload_pass('P1',cid,rows,reloads),'A3_CD':geom(a3,'chamfer_norm'),'P1_CD':geom(p,'chamfer_norm'),'A3_H95':geom(a3,'hausdorff_95_norm'),'P1_H95':geom(p,'hausdorff_95_norm'),'A3_Volume':geom(a3,'volume_error'),'P1_Volume':geom(p,'volume_error'),'root_cause':rc['category'],'evidence':rc['evidence']})
    fields=list(manifest[0]);
    with (OUT/'metadata/P1_QUALITATIVE_CASES.csv').open('w',newline='') as z:
        w=csv.DictWriter(z,fieldnames=fields);w.writeheader();w.writerows(manifest)
    (OUT/'integrity/GEOMETRY_SCALE_AUDIT.json').write_text(json.dumps(bbox_audit,indent=2)+'\n')
    def panels(cid,labels): return [panel[cid][x] for x in labels]
    maincats=['OPERATION_RESCUE','STEP_RESCUE','GEOMETRY_RESCUE','P1_OUTLIER']; mainrows=[]
    for k in maincats:
        if sel[k]: mainrows.append((k.replace('_',' ').title(),panels(sel[k][0],['GT','A1','A3','P1'])))
    gallery(mainrows,OUT/'galleries/P1_MAIN_QUALITATIVE_GALLERY.png','P1 VAL1000: qualitative summary')
    ops=[('Operation rescue',panels(c,['GT','A3','P1'])) for c in sel['OPERATION_RESCUE']]
    if ops:gallery(ops,OUT/'galleries/P1_OPERATION_RESCUE_GALLERY.png','Box / Extrude operation rescue')
    gp=[]
    for k,label in [('GEOMETRY_RESCUE','Geometry improvement'),('PLACEMENT_FAILURE','Placement failure')]:
        for c in sel[k][:2]:gp.append((label,panels(c,['GT','A3','P1'])))
    if gp:gallery(gp,OUT/'galleries/P1_GEOMETRY_AND_PLACEMENT_GALLERY.png','Geometry improvement and placement failure')
    fl=[]
    for k,label in [('CUT_UNION_LIMITATION','Cut / Union limitation'),('PLACEMENT_FAILURE','Origin / scale failure'),('P1_OUTLIER','Large geometry outlier')]:
        for c in sel[k][:2]:fl.append((label,panels(c,['GT','A3','P1'])))
    if fl:gallery(fl,OUT/'galleries/P1_FAILURE_AND_LIMITATION_GALLERY.png','P1 failures and limitations')
    caps=['# P1 VAL1000 Qualitative Captions','', 'All examples were selected automatically from the frozen validation set. GT, A1, A3, and P1 are tessellated from STEP with the same per-case absolute tolerance, GT-derived coordinate transform, orthographic camera, and zoom. No per-model fitting, recentering, or rescaling is used.']
    for m in manifest:
        caps += ['',f"## {m['cad_id']} ({m['category']})",f"P1 changes operation F1 from {f(m['A3_OpF1'],0):.2f} to {f(m['P1_OpF1'],0):.2f}; A3/P1 STEP reload are {m['A3_STEP']}/{m['P1_STEP']}. Root-cause label: {m['root_cause']}. {m['evidence']}"]
    (OUT/'reports/P1_QUALITATIVE_CAPTIONS.md').write_text('\n'.join(caps)+'\n')
    integrity={'GT_FROM_STEP':True,'A1_FROM_STEP':True,'A3_FROM_STEP':True,'P1_FROM_STEP':True,'SAME_TESSELLATION':True,'GT_SHARED_TRANSFORM':True,'SAME_CAMERA':True,'ORTHOGRAPHIC':True,'PER_MODEL_AUTOFIT':False,'PER_MODEL_RECENTER':False,'PER_MODEL_RESCALE':False,'TEST_CASE_USED_N':0,'TEST_TOUCHED':False,'PREDICTIONS_CHANGED':False,'MODEL_CHANGED':False,'EVALUATOR_CHANGED':False,'EDGE_OVERLAY':'DEFERRED'}
    (OUT/'integrity/VISUAL_INTEGRITY_AUDIT.json').write_text(json.dumps(integrity,indent=2)+'\n')
    summary={'CURRENT_GATE':'COMPLETE','TEST_TOUCHED':'NO','SELECTION':{k:len(v) for k,v in sel.items()},'VISUAL_PROTOCOL':integrity,'OUTPUT':{p.name:str(p) for p in sorted((OUT/'galleries').glob('*.png'))},'INTERPRETATION':{'P1_VISUAL_STRENGTH':'operation, STEP/execution, generation-completeness, and selected H95 rescue','P1_VISUAL_FAILURE_PATTERN':'local parameter, origin/translation, direction, scale/extent; Cut/Union regressions where available','P1_PLACEMENT_FAILURE_CONFIRMED':bool(sel['PLACEMENT_FAILURE']),'CUT_UNION_LIMITATION_VISIBLE':bool(sel['CUT_UNION_LIMITATION'])},'INTEGRITY':{'TEST_CASE_USED_N':0,'PREDICTIONS_CHANGED':'NO','MODEL_CHANGED':'NO','EVALUATOR_CHANGED':'NO'}}
    (OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
    md=['# P1 VAL1000 Qualitative Visualization V1','',f"CURRENT_GATE = {summary['CURRENT_GATE']}",'','TEST_TOUCHED = NO','','## Selection']+[f'- {k} = {len(v)}' for k,v in sel.items()]+['','## Visual protocol','- All geometry is re-tessellated from STEP with identical per-case tolerance.','- One GT-derived center and scale is shared across GT/A1/A3/P1.','- Camera, orthographic projection, zoom, clipping, and resolution are shared.','- Per-model auto-fit/recenter/rescale are disabled.','','## Interpretation',f"- P1 visual strength: {summary['INTERPRETATION']['P1_VISUAL_STRENGTH']}",f"- Failure pattern: {summary['INTERPRETATION']['P1_VISUAL_FAILURE_PATTERN']}",'','## Integrity','- TEST_CASE_USED_N = 0','- PREDICTIONS_CHANGED = NO','- MODEL_CHANGED = NO','- EVALUATOR_CHANGED = NO']
    (OUT/'reports/FINAL_REPORT.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__': main()
