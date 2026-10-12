from pathlib import Path
import os,sys,json,csv,math,traceback,argparse,subprocess,copy
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import pilot_repaired as base

ROOT=base.ROOT
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
ENV=base.ENV.copy()
ENV['OPENBLAS_NUM_THREADS']='1';ENV['OMP_NUM_THREADS']='1';ENV['MKL_NUM_THREADS']='1'

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene):m=m.to_mesh()
    m.merge_vertices();m.remove_unreferenced_vertices();return m
def pca(m):
    c=m.vertices.mean(0);w,R=np.linalg.eigh(np.cov((m.vertices-c).T));R=R[:,np.argsort(w)[::-1]]
    if np.linalg.det(R)<0:R[:,-1]*=-1
    return R,c
def perimeter_resample(poly,n=24):
    poly=orient(poly,sign=1);xy=np.asarray(poly.exterior.coords[:-1])
    seg=np.linalg.norm(np.roll(xy,-1,axis=0)-xy,axis=1);cum=np.r_[0,np.cumsum(seg)];total=cum[-1]
    out=[]
    for t in np.linspace(0,total,n,endpoint=False):
        i=max(0,min(len(seg)-1,np.searchsorted(cum,t,side='right')-1));u=(t-cum[i])/max(seg[i],1e-12)
        out.append((xy[i]*(1-u)+xy[(i+1)%len(xy)]*u).tolist())
    return out
def sections(m,R,c,nsec=9,npts=24):
    y=(m.vertices-c)@R;lo,hi=y[:,2].min(),y[:,2].max();out=[]
    for f in np.linspace(.015,.985,max(nsec,21)):
        z=float(lo+(hi-lo)*f);cut=m.section(plane_origin=c+R[:,2]*z,plane_normal=R[:,2])
        if cut is None:continue
        polys=[]
        for line in cut.discrete:
            xy=((line-c)@R)[:,:2]
            if len(xy)<3:continue
            try:
                p=Polygon(xy)
                if p.is_valid and p.area>np.linalg.norm(m.extents)**2*1e-8:polys.append(p)
            except:pass
        if polys:
            p=max(polys,key=lambda q:q.area)
            out.append({'z':z,'points':perimeter_resample(p,npts),'area':float(p.area)})
    return out,lo,hi
def profile_fit_score(m,ss,lo,hi):
    if len(ss)<3:return 999.
    area=np.array([s['area'] for s in ss]);cv=float(area.std()/max(area.mean(),1e-12))
    return cv
def code(program):
    return '''import cadquery as cq
from pathlib import Path

def build_model():
    sections = %r
    origin = %r
    xdir = %r
    normal = %r
    wires=[]
    for sec in sections:
        plane=cq.Plane(origin=(origin[0]+normal[0]*sec["z"],origin[1]+normal[1]*sec["z"],origin[2]+normal[2]*sec["z"]),xDir=xdir,normal=normal)
        wires.append(cq.Workplane(plane).polyline(sec["points"]).close().val())
    body=cq.Solid.makeLoft(wires,True)
    return cq.Workplane(obj=body)

if __name__=="__main__":
    body=build_model()
    out=Path(__file__).resolve().parent
    cq.exporters.export(body,str(out/"reconstructed.step"))
    cq.exporters.export(body,str(out/"reconstructed.stl"),tolerance=%r,angularTolerance=0.10)
    print({"valid":body.val().isValid(),"solids":body.solids().size(),"faces":body.faces().size()})
'''%(program['sections'],program['origin'],program['xdir'],program['normal'],program['tolerance'])
def make_candidates(m):
    R,c=pca(m);out=[]
    for j in range(3):
        A=R.copy();A[:,[0,j]]=A[:,[j,0]] if j!=0 else A[:,[0,0]]
        if j==0:A=R
        if np.linalg.det(A)<0:A[:,-1]*=-1
        ss,lo,hi=sections(m,A,c)
        if len(ss)>=3:
            out.append({'name':'MULTI_SECTION_LOFT_AXIS_%d'%j,'sections':ss,'origin':c.tolist(),'xdir':A[:,0].tolist(),'normal':A[:,2].tolist(),'tolerance':float(np.linalg.norm(m.extents)*0.00015),'lo':lo,'hi':hi,'axis_matrix':A.tolist()})
    return out
def parse_row(path):
    m=load(ROOT/path);return m
def ident(path):
    q=Path(path);return q.parts[0],q.parent.name+'__'+q.stem
def process(path):
    rel=Path(path);case,part=ident(rel);m=load(ROOT/rel);od=OUT/'cases'/case/part;od.mkdir(parents=True,exist_ok=True)
    source=od/'source.stl'
    if not source.exists():m.export(source)
    candidates=make_candidates(m);rows=[];best=None
    for i,pr in enumerate(candidates):
        cd=od/('candidate_%d'%i);cd.mkdir(exist_ok=True);(cd/'cad.py').write_text(code(pr));base.dump(cd/'program.json',{'version':'XPART_HIGH_FIDELITY_CAD_V1','geometry_family':'MULTI_SECTION_LOFT','operations':[{'type':'SKETCH_SECTION','count':len(pr['sections']),'points_per_section':len(pr['sections'][0]['points'])},{'type':'LOFT','closed':True}],'workplane':{'origin':pr['origin'],'xdir':pr['xdir'],'normal':pr['normal']}})
        run=subprocess.run([sys.executable,'cad.py'],cwd=cd,env=ENV,capture_output=True,text=True,timeout=240);ok=run.returncode==0
        rr={'candidate':i,'name':pr['name'],'execute':'PASS' if ok else 'FAIL'}
        if ok:
            try:
                cm=load(cd/'reconstructed.stl');mm=base.metrics(m,cm,high=True);rr.update(iou128=mm['iou128'],ncd=mm['ncd'],cad_faces=len(__import__('cadquery').importers.importStep(str(cd/'reconstructed.step')).val().Faces()),stderr='');score=1-mm['iou128']+0.0002*len(pr['sections'])*len(pr['sections'][0]['points'])
                if best is None or score<best[0]:best=(score,pr,mm,cm)
            except Exception as e:rr.update(iou128=None,ncd=None,stderr=str(e)[-500:])
        else:rr['stderr']=run.stderr[-500:]
        rows.append(rr)
    base.csvwrite(od/'candidates.csv',rows)
    if best is None:raise RuntimeError('HIGH_FIDELITY_CAD_EXECUTION_FAILED')
    _,pr,mm,cm=best;(od/'cad.py').write_text(code(pr));base.dump(od/'program.json',{'version':'XPART_HIGH_FIDELITY_CAD_V1','geometry_family':'MULTI_SECTION_LOFT','operations':[{'type':'SKETCH_SECTION','count':len(pr['sections']),'points_per_section':len(pr['sections'][0]['points'])},{'type':'LOFT','closed':True}],'workplane':{'origin':pr['origin'],'xdir':pr['xdir'],'normal':pr['normal']}});base.dump(od/'parameters.json',pr);run=subprocess.run([sys.executable,'cad.py'],cwd=od,env=ENV,capture_output=True,text=True,timeout=240);cm=load(od/'reconstructed.stl')
    txt=(od/'cad.py').read_text();meshused=any(x in txt for x in ['trimesh','meshio','source.stl','OBJ','STL','PLY']);import cadquery as cq;sh=cq.importers.importStep(str(od/'reconstructed.step')).val();faces=len(sh.Faces());valid=bool(sh.isValid()) and len(sh.Solids())>=1
    quality='A_HIGH_CONFIDENCE' if mm['iou128']>=.95 else 'B_USABLE' if mm['iou128']>=.9 else 'C_NEAR_MISS' if mm['iou128']>=.8 else 'D_REJECT'
    validpair=quality in ('A_HIGH_CONFIDENCE','B_USABLE') and mm['ncd']<=.01 and mm['bbox_error']<=.03 and mm['centroid_error']<=.02 and valid and not meshused
    result={'case_id':case,'part_id':part,'source_path':path,'geometry_family':'MULTI_SECTION_LOFT','feature_sequence':'SKETCH_SECTION x%d -> LOFT'%len(pr['sections']),'cad_program_exec':'PASS' if run.returncode==0 else 'FAIL','brep_valid':valid,'step_reload':True,'mesh_import_used':meshused,'faceted_brep':faces>=.35*len(m.faces),'source_triangle_count':len(m.faces),'cad_brep_face_count':faces,'quality_level':quality,'valid_training_pair':validpair,'failure_reason':'' if validpair else 'IOU_TOO_LOW','source_free_reexecution':True,**mm}
    base.dump(od/'metrics.json',result);base.dump(od/'validation.json',{'CAD_EXECUTION':'PASS' if run.returncode==0 else 'FAIL','BREP_VALID':'YES' if valid else 'NO','SOLID_COUNT':len(sh.Solids()),'STEP_RELOAD':'PASS','MESH_IMPORT_USED':'YES' if meshused else 'NO','FACETED_BREP':'YES' if result['faceted_brep'] else 'NO','VALID_TRAINING_PAIR':'YES' if validpair else 'NO'});(od/'report.md').write_text(json.dumps(result,indent=2),encoding='utf-8');base.overlay(m,cm,od/'overlay.png',case+'/'+part);return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',default='airplane,tank');ap.add_argument('--workers',type=int,default=3);ap.add_argument('--limit',type=int,default=0);a=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    paths=[];wanted=set(a.cases.split(','))
    for case in wanted:
        for f in sorted((ROOT/case/'p3_parts').glob('*.obj')):paths.append(str(f.relative_to(ROOT)))
        for f in sorted((ROOT/case/'xpart_parts').rglob('*')):
            if f.is_file() and f.suffix.lower() in ('.obj','.stl'):paths.append(str(f.relative_to(ROOT)))
    if a.limit:paths=paths[:a.limit]
    results=[];print('START',len(paths),paths[:3],flush=True)
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fs={pool.submit(process,p):p for p in paths}
        for i,f in enumerate(as_completed(fs),1):
            try:r=f.result()
            except Exception as e:r={'source_path':fs[f],'processing_status':'FIT_FAILED','error':str(e),'quality_level':'D_REJECT','valid_training_pair':False}
            r.setdefault('processing_status','CAD_GENERATED');results.append(r);print('DONE',i,'/',len(paths),r.get('source_path'),r.get('iou128'),r.get('error',''),flush=True)
    base.dump(OUT/('summary_'+('_'.join(sorted(wanted)))+'.json'),{'cases':sorted(wanted),'total':len(results),'generated':sum(x.get('processing_status')=='CAD_GENERATED' for x in results),'valid_pairs':sum(x.get('valid_training_pair',False) for x in results),'A':sum(x.get('quality_level')=='A_HIGH_CONFIDENCE' for x in results),'B':sum(x.get('quality_level')=='B_USABLE' for x in results),'C':sum(x.get('quality_level')=='C_NEAR_MISS' for x in results),'D':sum(x.get('quality_level')=='D_REJECT' for x in results),'iou128_mean':float(np.mean([x['iou128'] for x in results if x.get('iou128') is not None]))})
if __name__=='__main__':main()
