import os, sys, json, runpy, traceback, shutil, time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
R=Path('/data/home/cuiyuehan/project/mesh2cad')
O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
sys.path.insert(0,str(O/'code'))
import pipeline as P
import cadquery as cq

NAME=sys.argv[1]
PARTS=sys.argv[2:]
BASE=Path('/var/tmp/cuiyuehan_full20_completion_20260925/object_q14_repairs')/NAME

def one(pid, idx):
    src=O/'objects'/NAME/'cad_parts'/pid
    out=BASE/pid/f'attempt_{idx}'
    out.mkdir(parents=True, exist_ok=True)
    rec={'object':NAME,'part':pid,'attempt':idx,'PASS':False,'original_artifacts_modified':False}
    try:
        source=(src/'compiled_cadquery.py').read_text()
        if idx >= 2: source=source.replace('shape=shape.clean()','shape=shape')
        if idx == 3:
            old="shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()"
            new=old+"\n                if not shape.isValid():\n                    wires=[sketch_wire(q,z,False) for z,q in feature['sections']]\n                    shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()"
            if old in source: source=source.replace(old,new)
        source += "\n_base_build=build\ndef build():\n    s=_base_build()\n    return s.fix() if not s.isValid() else s\n"
        cp=out/'compiled_cadquery.py'; cp.write_text(source)
        shape=runpy.run_path(str(cp))['build']()
        assert shape.isValid() and shape.Solids(), 'REPAIRED_BREP_INVALID'
        sp=out/'part.step'; cq.exporters.export(shape,str(sp))
        rb=cq.importers.importStep(str(sp)).val(); assert rb.isValid() and rb.Solids(), 'STEP_READBACK_INVALID'
        raw=cq.importers.importStep(str(src/'raw.step')).val()
        m=P.compare(P.shapemesh(raw),P.shapemesh(rb)); m['VOLUME_ERROR']=abs(rb.Volume()-raw.Volume())/max(abs(raw.Volume()),1e-12)
        rec.update(BREP_VALID=True,STEP_READBACK_PASS=True,raw_vs_candidate=m,BODY_N=len(rb.Solids()),RAW_BODY_N=len(raw.Solids()))
        rec['PASS']=all(m[k] <= .02 for k in ('CD','BBOX_ERROR','CENTROID_ERROR')) and m['VOLUME_ERROR'] <= .05 and rec['BODY_N']==rec['RAW_BODY_N']
    except Exception:
        rec['error']=traceback.format_exc()
    rec['finished']=time.time(); P.dump(out/'REPAIR_RESULT.json',rec); print(json.dumps(rec),flush=True)
    return rec

if __name__=='__main__':
    for pid in PARTS:
        for idx in (1,2,3):
            result=one(pid,idx)
            if result.get('PASS'): break
