#!/usr/bin/env python3
"""Read-only GT and Dora stage audit for the frozen V3 train800 cohort.

This script never changes the frozen build.  It writes a new evidence bundle
only, and measures geometry in the CAD world frame using deterministic mesh
surface samples as an inspectable finite-resolution proxy for final surface.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
BUILD = ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'
COHORT = ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
OUT_DEFAULT = ROOT/'ours3/dora_gt_and_fitting_audit_v2'
sys.path.insert(0, str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('dora_fit_v1', ROOT/'scripts/dora_fitted_curve_dataset_v1.py')
fitmod = importlib.util.module_from_spec(spec); spec.loader.exec_module(fitmod)

THRESHOLDS = (0.002, 0.005, 0.01, 0.02)
GT_SAMPLES = 64
MESH_SAMPLES = 50000

def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
def q(a):
    a=np.asarray(a,float); a=a[np.isfinite(a)]
    if not len(a): return {'n':0}
    return {'n':int(len(a)),'min':float(a.min()),'p10':float(np.percentile(a,10)),'median':float(np.median(a)),'mean':float(a.mean()),'p90':float(np.percentile(a,90)),'p95':float(np.percentile(a,95)),'max':float(a.max())}
def norm(v):
    return float(np.linalg.norm(v))
def sha(s): return hashlib.sha256(str(s).encode()).hexdigest()

def load_mesh_points(obj_path, cad_id):
    """Deterministically sample final triangular mesh surface, no rtree needed."""
    vs=[]; fs=[]
    for ln in Path(obj_path).read_text(errors='ignore').splitlines():
        x=ln.split()
        if not x: continue
        if x[0]=='v': vs.append([float(a) for a in x[1:4]])
        elif x[0]=='f': fs.append([int(a.split('/')[0])-1 for a in x[1:4]])
    v=np.asarray(vs,float); f=np.asarray(fs,int)
    lo,hi=v.min(0),v.max(0); diag=norm(hi-lo)
    if not len(f): return v,lo,hi,diag
    tri=v[f]; area=.5*np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    good=area>0; tri=tri[good]; area=area[good]
    rng=np.random.default_rng(int(sha(cad_id)[:16],16))
    n=max(4096,min(MESH_SAMPLES,max(4096,len(tri)*32)))
    ix=rng.choice(len(tri),size=n,p=area/area.sum())
    r1=np.sqrt(rng.random(n)); r2=rng.random(n)
    a,b,c=tri[ix,0],tri[ix,1],tri[ix,2]
    surf=(1-r1)[:,None]*a+(r1*(1-r2))[:,None]*b+(r1*r2)[:,None]*c
    return np.vstack((v,surf)),lo,hi,diag

def coverage(query, target_tree, diag):
    d=target_tree.query(np.asarray(query,float),workers=-1)[0]/max(diag,1e-12)
    out={'median_distance':float(np.median(d)),'p95_distance':float(np.percentile(d,95)),'max_distance':float(d.max())}
    out.update({f'coverage_{t:g}':float((d<=t).mean()) for t in THRESHOLDS})
    return out,d

def dora_points(raw, chains):
    xyz,adj,edges=fitmod.graph_from_dora(raw)
    rawp=np.vstack([raw['edge_xyz0'],raw['edge_xyz1'],(raw['edge_xyz0']+raw['edge_xyz1'])/2])
    cp=[]
    for off0,off1 in zip(chains['offsets'][:-1],chains['offsets'][1:]):
        ids=chains['vertex_indices_flat'][int(off0):int(off1)]
        pts=np.asarray([xyz[int(i)] for i in ids],float)
        if len(pts)==1: cp.append(pts[0]); continue
        # Chain geometry is the full polyline, not vertices only.  This makes
        # raw->chain an actual representation-preservation check.
        for a,b in zip(pts[:-1],pts[1:]):
            cp.extend((a, (a+b)/2, b))
    return rawp,np.asarray(cp,float),xyz

def status_from_gt(m, extent_ratio):
    # Explicit operational rule; all threshold curves remain in the evidence.
    if m['coverage_0.01']>=.95 and m['p95_distance']<=.01 and extent_ratio<=2.0: return 'GT_VALID','mesh_coverage_0.01>=.95,p95<=.01,extent_ratio<=2'
    if m['coverage_0.02']>=.50 and m['p95_distance']<=.05 and extent_ratio<=5.0: return 'GT_SUSPICIOUS','partial_mesh_support_or_extent_outlier'
    return 'GT_INVALID','insufficient_final_mesh_support'

def fit_metrics(chain_pts, f, diag):
    # Frozen JSON serialises ndarray parameters as lists; restore precisely for
    # the existing V1 sampler without changing the stored artifact.
    f=dict(f)
    for key in ('origin','direction','center','normal','x_axis','y_axis','major_axis','minor_axis'):
        if key in f: f[key]=np.asarray(f[key],float)
    if 'tck' in f: f['tck']=[np.asarray(f['tck'][0],float),np.asarray(f['tck'][1],float),int(f['tck'][2])]
    fp,_,_,flen=fitmod.sample_fit(f); ct=cKDTree(chain_pts); ft=cKDTree(fp)
    a,da=coverage(chain_pts,ft,diag); b,db=coverage(fp,ct,diag)
    cl=float(np.linalg.norm(np.diff(chain_pts,axis=0),axis=1).sum())
    ce=np.ptp(chain_pts,axis=0); fe=np.ptp(fp,axis=0)
    er=float(norm(fe)/max(norm(ce),1e-12)); lr=float(flen/max(cl,1e-12)); shift=float(norm(fp.mean(0)-chain_pts.mean(0))/max(diag,1e-12))
    catastrophic=bool(er>3 or lr>3 or b['p95_distance']>.02 or a['p95_distance']>.02)
    return fp, {'chain_to_fit':a,'fit_to_chain':b,'length_ratio':lr,'bbox_extent_ratio':er,'centroid_shift_rel':shift,'catastrophic_fit':catastrophic}

def sample_frozen_fit(f):
    """Sample a fitted-curve JSON record without mutating it."""
    f=dict(f)
    for key in ('origin','direction','center','normal','x_axis','y_axis','major_axis','minor_axis'):
        if key in f: f[key]=np.asarray(f[key],float)
    if 'tck' in f: f['tck']=[np.asarray(f['tck'][0],float),np.asarray(f['tck'][1],float),int(f['tck'][2])]
    return fitmod.sample_fit(f)

def provenance():
    return {'GT_SOURCE_TYPE':'FINAL_SOLID_BREP_EDGE','generator_script':str(ROOT/'scripts/dora_fitted_curve_dataset_v1.py'),'generator_function':'gt_samples(step) -> extract_curves_from_step(step) + TopExp.MapShapes(final STEP, TopAbs_EDGE)','extractor_script':str(ROOT/'scripts/curve_token_v1/extract_brep_curves.py'),'extractor_function':'extract_curves_from_shape(shape)','final_solid_brep':True,'sketch_history_contamination':False,'transform_applied_in_extraction':'none: STEP world coordinates sampled directly and compared to model.obj world coordinates','source_by_dataset':'same model.step -> final TopoDS_Edge code path for DeepCAD and Fusion360','unit_scaling_in_extraction':'none','extent_fix_mixing':'not introduced by this reader; frozen per-CAD model.step is authoritative','support_or_infinite_geometry_risk':'low by code provenance: TopExp.MapShapes on loaded final STEP shape only; geometry sanity measured separately'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT_DEFAULT); ap.add_argument('--limit',type=int,default=0); args=ap.parse_args()
    out=args.output; out.mkdir(parents=True,exist_ok=False)
    dump(out/'GT_PROVENANCE_AUDIT.json',provenance())
    (out/'GT_PROVENANCE_AUDIT.md').write_text('# GT B-Rep provenance audit\n\n`gt_brep_curves.json` was generated by `gt_samples()` in `scripts/dora_fitted_curve_dataset_v1.py`. It loads each frozen `model.step`, maps `TopAbs_EDGE` from the loaded final STEP shape, and samples those topological edges through `BRepAdaptor_Curve`. It does not read CAD history, sketches, construction geometry, or DSL. Both source datasets use this exact path. No coordinate transform or unit scale is applied by this extraction; this audit tests agreement with the paired `model.obj` in the same frozen asset record.\n')
    rows=[json.loads(x) for x in COHORT.read_text().splitlines() if x.strip() and json.loads(x)['split']=='train800']
    rows=sorted(rows,key=lambda x:x['cad_id']);
    # Restrict to existing paired build, never backfill it.
    rows=[r for r in rows if (BUILD/r['cad_id']/'gt_brep_curves.json').exists()]
    if args.limit: rows=rows[:args.limit]
    all_curves=[]; cad_rows=[]; fit_rows=[]; stage_rows=[]; by_source=defaultdict(list)
    for ni,r in enumerate(rows,1):
        cid=r['cad_id']; b=BUILD/cid; raw=np.load(r['assets']['dora_salient_edges']['path']); chains=np.load(b/'dora/chains.npz'); fits=json.loads((b/'dora/fitted_curves.json').read_text())['curves']
        mesh,lo,hi,diag=load_mesh_points(r['assets']['model_obj']['path'],cid); mt=cKDTree(mesh)
        _,gts=fitmod.gt_samples(r['assets']['model_step']['path'])
        rawp,chainp,xyz=dora_points(raw,chains); rt,ct=cKDTree(rawp),cKDTree(chainp)
        trusted=[]; gtm=[]
        for g in gts:
            pts=np.asarray(g['points'],float); gm,_=coverage(pts,mt,diag); ext=np.ptp(pts,axis=0); er=norm(ext)/max(diag,1e-12); st,reason=status_from_gt(gm,er)
            rec={'cad_id':cid,'dataset':r['dataset'],'gt_curve_id':int(g['gt_id']),'curve_type':g['type'],'gt_mesh_coverage':gm,'median_mesh_distance':gm['median_distance'],'p95_mesh_distance':gm['p95_distance'],'max_mesh_distance':gm['max_distance'],'curve_bbox_extent':ext.tolist(),'object_bbox_extent':(hi-lo).tolist(),'extent_ratio':er,'curve_centroid':pts.mean(0).tolist(),'distance_to_object_bbox':float(np.maximum(np.maximum(lo-pts.mean(0),pts.mean(0)-hi),0).max()/max(diag,1e-12)),'status':st,'reason':reason}
            all_curves.append(rec); gtm.append((g,rec))
            if st=='GT_VALID': trusted.append((g,rec))
        # GT->raw/chain/fitted only for trusted reference points.
        for g,gr in trusted:
            rawm,_=coverage(g['points'],rt,diag); chainm,_=coverage(g['points'],ct,diag)
            # no forced correspondence: union of all fitted support answers representation coverage.
            fpoints=[]
            for f in fits:
                try:fpoints.append(sample_frozen_fit(f)[0])
                except Exception:pass
            fittree=cKDTree(np.vstack(fpoints)) if fpoints else None
            fitm,_=coverage(g['points'],fittree,diag) if fittree else ({'coverage_0.01':0.,'coverage_0.02':0.,'median_distance':float('inf'),'p95_distance':float('inf'),'max_distance':float('inf')},None)
            stage_rows.append({'cad_id':cid,'dataset':r['dataset'],'gt_curve_id':int(g['gt_id']),'curve_type':g['type'],'raw':rawm,'chain':chainm,'fitted':fitm,'raw_to_chain_drop_0.01':chainm['coverage_0.01']-rawm['coverage_0.01'],'chain_to_fitted_drop_0.01':fitm['coverage_0.01']-chainm['coverage_0.01']})
        # fit quality independent of GT. Reconstruct each chain in the locked ordering.
        offs=chains['offsets']; flat=chains['vertex_indices_flat']; fby={int(f['chain_id']):f for f in fits}
        for ci,(a,z) in enumerate(zip(offs[:-1],offs[1:])):
            if ci not in fby:continue
            pts=np.asarray([xyz[int(x)] for x in flat[int(a):int(z)]],float); f=fby[ci]
            if len(pts)<2:continue
            _,fm=fit_metrics(pts,f,diag); fm.update({'cad_id':cid,'dataset':r['dataset'],'chain_id':ci,'fit_type':f['type'],'closed_loop':bool(f.get('closed_loop',False)),'fitter_normalized_residual':float(f.get('normalized_residual',np.nan))});fit_rows.append(fm)
        cr=Counter(x['status'] for _,x in gtm); cad_rows.append({'cad_id':cid,'dataset':r['dataset'],'gt_curve_count':len(gts),'valid_gt_curve_count':cr['GT_VALID'],'suspicious_gt_curve_count':cr['GT_SUSPICIOUS'],'invalid_gt_curve_count':cr['GT_INVALID'],'median_gt_mesh_coverage_0.01':float(np.median([x['gt_mesh_coverage']['coverage_0.01'] for _,x in gtm])) if gtm else None})
        print(f'{ni}/{len(rows)} {cid} gt={len(gts)} trusted={len(trusted)} fits={len(fits)}',flush=True)
    def jlines(path,x): Path(path).write_text(''.join(json.dumps(a,sort_keys=True)+'\n' for a in x))
    jlines(out/'GT_TRUSTED_CURVE_MANIFEST.jsonl',all_curves); jlines(out/'FIT_CHAIN_DIAGNOSTICS.jsonl',fit_rows); jlines(out/'TRUSTED_GT_STAGE_COVERAGE.jsonl',stage_rows)
    dump(out/'GT_TRUSTED_CAD_MANIFEST.json',cad_rows)
    # summaries segmented by source/type, plus current strict correspondence measured without reclassification.
    summ={'cad_count':len(cad_rows),'gt_curve_count':len(all_curves),'operational_status_rule':'VALID coverage_0.01>=.95 AND p95<=.01 AND extent_ratio<=2; SUSPICIOUS coverage_0.02>=.50 AND p95<=.05 AND extent_ratio<=5; otherwise INVALID','thresholds_normalized':list(THRESHOLDS),'source':{},'fit':{},'stage':{}}
    for ds in ('DeepCAD','Fusion360','ALL'):
        cc=[x for x in all_curves if ds=='ALL' or x['dataset']==ds]; summ['source'][ds]={'n':len(cc),'valid_rate':float(sum(x['status']=='GT_VALID' for x in cc)/max(len(cc),1)),'status_counts':dict(Counter(x['status'] for x in cc)),'coverage_0.01':q([x['gt_mesh_coverage']['coverage_0.01'] for x in cc]),'median_distance':q([x['median_mesh_distance'] for x in cc]),'p95_distance':q([x['p95_mesh_distance'] for x in cc]),'extent_ratio':q([x['extent_ratio'] for x in cc])}
    for typ in sorted(set(x['fit_type'] for x in fit_rows)):
        z=[x for x in fit_rows if x['fit_type']==typ]; summ['fit'][typ]={'n':len(z),'catastrophic_n':sum(x['catastrophic_fit'] for x in z),'catastrophic_rate':float(sum(x['catastrophic_fit'] for x in z)/len(z)),'bbox_extent_ratio':q([x['bbox_extent_ratio'] for x in z]),'length_ratio':q([x['length_ratio'] for x in z]),'fit_to_chain_p95':q([x['fit_to_chain']['p95_distance'] for x in z])}
    for k in ('raw','chain','fitted'):
        summ['stage'][k]={'coverage_0.01':q([x[k]['coverage_0.01'] for x in stage_rows]),'coverage_0.02':q([x[k]['coverage_0.02'] for x in stage_rows])}
    # Original strict correspondence comes only from frozen record classifications.
    cls=Counter()
    for r in rows: cls.update(x['classification'] for x in json.loads((BUILD/r['cad_id']/'correspondence.json').read_text())['records'])
    summ['strict_original_correspondence']=dict(cls); summ['strict_original_1to1_ratio']=float(cls['MATCHED_1_TO_1']/max(sum(cls.values()),1))
    # Trusted analogue: only retain frozen matches whose GT edge has valid status (not a new match decision).
    valid={(x['cad_id'],x['gt_curve_id']) for x in all_curves if x['status']=='GT_VALID'}; trusted_cls=Counter()
    for r in rows:
        for x in json.loads((BUILD/r['cad_id']/'correspondence.json').read_text())['records']:
            if x['gt_curve_id'] is not None and (r['cad_id'],int(x['gt_curve_id'])) in valid: trusted_cls[x['classification']]+=1
    summ['strict_trusted_subset_existing_classifications']=dict(trusted_cls); summ['strict_trusted_1to1_ratio']=float(trusted_cls['MATCHED_1_TO_1']/max(sum(trusted_cls.values()),1))
    dump(out/'SUMMARY.json',summ)
    # Code decision path is frozen as textual evidence.
    (out/'FITTER_CODE_AUDIT.md').write_text('''# Fitter decision path (read-only source audit)\n\nSource: `scripts/dora_fitted_curve_dataset_v1.py`, `process()`. Each maximal chain from `extract_chains()` is fitted as one primitive:\n\n1. `linefit(p)` is always attempted.\n2. If line RMS / object diagonal > `FIT_TOL_REL=0.005` and >=4 points: `circlefit(p, closed_loop)`.\n3. If still failing and >=6 points: `ellipsefit(p, closed_loop)`.\n4. If still failing: `splinefit(p, closed_loop, diag)`.\n\n`extract_chains()` stops a walk only at degree != 2 vertices; any degree-2 sequence is retained as one chain. The primitive acceptance is only RMS / object diagonal. There is no explicit radius/extent limit, no fitted-to-chain unsupported-region guard, no sweep-support check, and no semantic guard for a chain that crosses an unobserved geometric boundary. Thus a large circle/ellipse can be accepted when its sparse ordered input points have small residual under the algebraic fit, even though much of the sampled primitive has no chain support. This report does not modify those rules.\n''')
    print(json.dumps(summ,indent=2))
if __name__=='__main__': main()
