#!/usr/bin/env python3
import hashlib, json, os, sys, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
ROOT = REPO / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1"

def evaluate(job):
    cad_id, pred_hash, prediction, gt_mesh_s = job
    key = hashlib.sha256((cad_id+"\0"+pred_hash).encode()).hexdigest()
    out = ROOT/"geometry_cache"/key
    out.mkdir(parents=True, exist_ok=True)
    rec={"cad_id":cad_id,"prediction_sha256":pred_hash,"parsed":False,"step_ok":False,"step_reload":False,"geometry":{}}
    try:
        sys.path.insert(0,str(REPO/"scripts/geometry_pack_v2_mesh2cad/placement_v3"))
        from cad_dsl import extract_dsl_code, parse_dsl, execute_dsl
        code=extract_dsl_code(prediction)
        parse_dsl(code); rec["parsed"]=True
        (out/"pred.dsl").write_text(code if code.endswith("\n") else code+"\n")
        execute_dsl(code,out/"pred.step",out/"pred.stl")
        rec["step_ok"]=(out/"pred.step").exists() and (out/"pred.step").stat().st_size>0
        if rec["step_ok"]:
            import cadquery as cq
            cq.importers.importStep(str(out/"pred.step")); rec["step_reload"]=True
        if rec["step_reload"] and (out/"pred.stl").exists():
            import trimesh
            from scipy.spatial import cKDTree
            a=trimesh.load(gt_mesh_s,force="mesh"); b=trimesh.load(str(out/"pred.stl"),force="mesh")
            if isinstance(a,trimesh.Scene): a=a.dump(concatenate=True)
            if isinstance(b,trimesh.Scene): b=b.dump(concatenate=True)
            diag=float(np.linalg.norm(a.bounds[1]-a.bounds[0]))
            if diag>1e-12:
                pa,_=trimesh.sample.sample_surface(a,5000,seed=20260828)
                pb,_=trimesh.sample.sample_surface(b,5000,seed=20260829)
                ab=cKDTree(pb).query(pa,k=1)[0]; ba=cKDTree(pa).query(pb,k=1)[0]
                rec["geometry"]={"chamfer_norm":float((ab.mean()+ba.mean())/2/diag),"hausdorff95_norm":float(np.percentile(np.r_[ab,ba],95)/diag)}
    except Exception as e:
        rec["error"]=f"{type(e).__name__}: {e}"[-1000:]
    (out/"result.json").write_text(json.dumps(rec,indent=2)+"\n")
    return key,rec

def main():
    cohort=json.loads((ROOT/"data/phase_d_50.json").read_text())
    mesh={r["cad_id"]:str(Path(r["surface_input"]).parent/"mesh.obj") for r in cohort["records"]}
    variants={}
    jobs={}
    for p in sorted((ROOT/"runs").glob("*/predictions.jsonl")):
        rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        if len(rows)!=50: continue
        variants[p.parent.name]=rows
        for r in rows:
            ph=hashlib.sha256(r.get("prediction","").encode()).hexdigest()
            key=hashlib.sha256((r["cad_id"]+"\0"+ph).encode()).hexdigest()
            jobs[key]=(r["cad_id"],ph,r.get("prediction",""),mesh[r["cad_id"]])
    cache={}
    pending=[]
    for key,j in jobs.items():
        p=ROOT/"geometry_cache"/key/"result.json"
        if p.exists(): cache[key]=json.loads(p.read_text())
        else: pending.append(j)
    with ProcessPoolExecutor(max_workers=min(12,os.cpu_count() or 4)) as ex:
        fs=[ex.submit(evaluate,j) for j in pending]
        for i,f in enumerate(as_completed(fs),1):
            key,rec=f.result(); cache[key]=rec
            if i%25==0: print(f"geometry {i}/{len(pending)}",flush=True)
    summaries=[]; per=[]
    for name,rows in variants.items():
        enriched=[]
        for r in rows:
            ph=hashlib.sha256(r.get("prediction","").encode()).hexdigest()
            key=hashlib.sha256((r["cad_id"]+"\0"+ph).encode()).hexdigest()
            q={"variant":name,"cad_id":r["cad_id"],**cache[key]}; enriched.append(q); per.append(q)
        cham=[x["geometry"]["chamfer_norm"] for x in enriched if "chamfer_norm" in x.get("geometry",{})]
        summaries.append({"variant":name,"n":50,"parsed_n":sum(x["parsed"] for x in enriched),"step_ok_n":sum(x["step_ok"] for x in enriched),"step_reload_n":sum(x["step_reload"] for x in enriched),"geometry_valid_n":len(cham),"mean_chamfer_norm":float(np.mean(cham)) if cham else None,"median_chamfer_norm":float(np.median(cham)) if cham else None})
    (ROOT/"PHASE_D_GEOMETRY_PER_CAD.jsonl").write_text("".join(json.dumps(x)+"\n" for x in per))
    report={"status":"PASS","unique_geometry_jobs":len(jobs),"variants":len(summaries),"official_test_read":False,"training_started":False,"summary":summaries}
    (ROOT/"PHASE_D_GEOMETRY_SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__": main()
