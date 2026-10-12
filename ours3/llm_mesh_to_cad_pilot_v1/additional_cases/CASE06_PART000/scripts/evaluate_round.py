#!/usr/bin/env python3
import argparse, ast, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
import cadquery as cq

def render_points(src, rec, out, overlay=False):
    im=Image.new('RGB',(900,900),'white'); d=ImageDraw.Draw(im); az,el=math.radians(35),math.radians(25)
    view=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]); up=np.array([0.,0.,1.]); right=np.cross(view,up); right/=np.linalg.norm(right); up=np.cross(right,view)
    allv=np.vstack([src.vertices,rec.vertices]); c=(allv.min(0)+allv.max(0))/2; span=max(np.ptp(allv@right),np.ptp(allv@up),1e-12); scale=760/span
    sets=[(src,(30,100,220)),(rec,(225,70,45))] if overlay else [(rec,(225,70,45))]
    if not overlay: sets=[(src,(30,100,220))] if 'source' in out.name else sets
    for mesh,col in sets:
        pts=mesh.sample(min(22000,len(mesh.faces)*2)); q=pts-c; xy=np.column_stack((q@right,q@up))*scale+450
        for x,y in xy[::2]: d.ellipse((x-1,y-1,x+1,y+1),fill=col)
    im.save(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('case'); ap.add_argument('version'); ap.add_argument('--samples',type=int,default=50000); a=ap.parse_args()
    root=Path(a.root); code=root/'cad_code'/f'{a.case}_{a.version}.py'; log=root/'logs'/f'{a.case}_{a.version}.log'; step=root/'step'/f'{a.case}_{a.version}.step'; stl=root/'recon_mesh'/f'{a.case}_{a.version}.stl'
    status={'cad_parse':False,'cad_execute':False,'solid_valid':False,'step_export':False,'step_reload':False,'tessellation':False,'sample_count':a.samples}
    lines=[]
    try: ast.parse(code.read_text()); status['cad_parse']=True; lines.append('CAD_PARSE=PASS')
    except Exception as e: lines.append('CAD_PARSE=FAIL '+repr(e))
    if status['cad_parse']:
        p=subprocess.run([sys.executable,str(code)],cwd=root,text=True,capture_output=True); lines += [p.stdout,p.stderr]; status['cad_execute']=p.returncode==0; lines.append('CAD_EXECUTION='+('PASS' if status['cad_execute'] else 'FAIL'))
    status['step_export']=step.exists() and step.stat().st_size>100; status['solid_valid']=status['cad_execute'] and status['step_export']; lines.append('SOLID_VALID='+('PASS' if status['solid_valid'] else 'FAIL')); lines.append('STEP_EXPORT='+('PASS' if status['step_export'] else 'FAIL'))
    if status['step_export']:
        try:
            obj=cq.importers.importStep(str(step)); status['step_reload']=obj.val() is not None and obj.val().isValid() and obj.val().Volume()>0
        except Exception as e: lines.append('STEP_RELOAD_ERROR='+repr(e))
    lines.append('STEP_RELOAD='+('PASS' if status['step_reload'] else 'FAIL'))
    if not status['step_reload']:
        log.write_text('\n'.join(lines)); (root/'metrics'/f'{a.case}_{a.version}.json').write_text(json.dumps(status,indent=2)); raise SystemExit(2)
    try: rec=trimesh.load(stl,force='mesh',process=False); status['tessellation']=len(rec.faces)>0
    except Exception as e: lines.append('TESSELLATION_ERROR='+repr(e)); rec=None
    lines.append('TESSELLATION='+('PASS' if status['tessellation'] else 'FAIL'))
    src=trimesh.load(root/'inputs'/f'{a.case}_source.obj',force='mesh',process=False)
    np.random.seed(20260918); sp,sfi=trimesh.sample.sample_surface(src,a.samples); rp,rfi=trimesh.sample.sample_surface(rec,a.samples)
    ts,tr=cKDTree(sp),cKDTree(rp); ds,ii=tr.query(sp,k=1); dr,jj=ts.query(rp,k=1)
    scale=max(src.extents); status['chamfer_l1']=float((ds.mean()+dr.mean())/(2*scale)); status['chamfer_l2']=float((np.mean(ds**2)+np.mean(dr**2))/(2*scale**2))
    sn=src.face_normals[sfi]; rn=rec.face_normals[rfi]; nc1=np.abs(np.sum(sn*rec.face_normals[rfi[ii]],axis=1)).mean(); nc2=np.abs(np.sum(rn*src.face_normals[sfi[jj]],axis=1)).mean(); status['normal_consistency']=float((nc1+nc2)/2)
    status['bbox_relative_error']=float(np.mean(np.abs(rec.extents-src.extents)/np.maximum(src.extents,1e-12))); status['surface_area_ratio']=float(rec.area/src.area); status['volume_ratio']=float(abs(rec.volume)/abs(src.volume)) if src.is_watertight and rec.is_watertight else None
    # Common-grid occupancy; pitch balances smoke-test cost and stability.
    try:
        pitch=scale/96; sv=src.voxelized(pitch).fill(); rv=rec.voxelized(pitch).fill(); origin=np.minimum(sv.bounds[0],rv.bounds[0]); si=np.round((sv.points-origin)/pitch).astype(int); ri=np.round((rv.points-origin)/pitch).astype(int); S={tuple(x) for x in si}; R={tuple(x) for x in ri}; status['iou']=len(S&R)/max(1,len(S|R))
    except Exception as e: status['iou']=None; lines.append('IOU_ERROR='+repr(e))
    for suffix in ['source','recon','overlay']: render_points(src,rec,root/'renders'/f'{a.case}_{a.version}_{suffix}.png',overlay=suffix=='overlay')
    (root/'metrics'/f'{a.case}_{a.version}.json').write_text(json.dumps(status,indent=2)); lines.append(json.dumps(status,indent=2)); log.write_text('\n'.join(lines)); print(json.dumps(status))
if __name__=='__main__': main()
