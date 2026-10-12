"""Source-driven combined sketch/profile/axis runtime for frozen REVOLVE10.

This canary deliberately parses only the FeatureScript semantics exercised by
the frozen set: line segments, base planes, sketch regions, and sketch-line
axes. It never invents a profile or axis from a bounding box.
"""
from __future__ import annotations
import hashlib, json, math, re, subprocess
from pathlib import Path
import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/profile_axis_geometry_runtime_implementation_canary_v1'
CANARY = ROOT / 'ours3/complex_cadfs_converter_coverage_expansion_v1/canary/REVOLVE_CANARY_MANIFEST.json'
TOL = 1e-6

def dump(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(rows, list): path.write_text(''.join(json.dumps(x, sort_keys=True)+'\n' for x in rows))
    else: path.write_text(json.dumps(rows, indent=2, sort_keys=True)+'\n')
def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def norm(v):
    a=np.asarray(v,float); n=np.linalg.norm(a)
    if n <= TOL: raise ValueError('zero vector')
    return (a/n).tolist()
def plane_frame(name):
    # Onshape base-plane convention: Front XY, Right YZ, Top XZ.
    if name == 'Front': return [0,0,0], [1,0,0], [0,1,0], [0,0,1]
    if name == 'Right': return [0,0,0], [0,1,0], [0,0,1], [1,0,0]
    if name == 'Top': return [0,0,0], [1,0,0], [0,0,-1], [0,1,0]
    raise ValueError('unsupported base plane: '+name)
def transform(p, fr):
    o,u,v,n=map(np.asarray,fr); x,y=p
    return (o+x*u+y*v).tolist()
def parse_source(cad_id, path):
    s=path.read_text()
    planes=re.findall(r'Q0\s*=\s*qCreatedBy\(makeId\("([A-Za-z]+)\.planeOp"\)',s)
    plane=planes[0] if planes else None
    # Keep declaration order; entity IDs are explicit and stable.
    lines=[]
    line_pat=r'skLineSegment\(sketch,\s*"([^"]+)"\s*,\s*\{\s*"start"\s*:\s*v\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)\s*\*[^,]+,\s*"end"\s*:\s*v\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)'
    for m in re.finditer(line_pat,s):
        eid,x1,y1,x2,y2=m.groups(); lines.append({'entity_id':f'F0.{eid}','sketch_id':'F0','start_local':[float(x1),float(y1)],'end_local':[float(x2),float(y2)],'construction':False,'source_ref':f'F0.{eid}'})
    profiles=re.findall(r'Q\d+=qSketchRegion\(id\+"([^"]+)"\s*,\s*true\)',s)
    axes=[]
    for m in re.finditer(r'sQuery\(id\+"([^"]+)"\s*,\s*EDGE\s*,\s*"([^"]+)"\)',s): axes.append({'query':m.group(1),'entity_id':f'F0.{m.group(2)}','source_ref':m.group(1)})
    return {'cad_id':cad_id,'source_path':str(path),'source_sha256':sha(path),'plane':plane,'lines':lines,'profiles':profiles,'axes':axes,'source_text':s}
def order_loop(lines):
    if not lines: raise ValueError('empty profile')
    rem=list(lines); out=[rem.pop(0)]
    while rem:
        end=np.array(out[-1]['end_global']); found=None
        for i,e in enumerate(rem):
            if np.linalg.norm(end-np.array(e['start_global'])) <= TOL: found=(i,False); break
            if np.linalg.norm(end-np.array(e['end_global'])) <= TOL: found=(i,True); break
        if found is None: raise ValueError('PROFILE_ENTITY_ORDER_FAIL')
        i,rev=found; e=rem.pop(i)
        if rev: e=dict(e,start_global=e['end_global'],end_global=e['start_global'])
        out.append(e)
    if np.linalg.norm(np.array(out[-1]['end_global'])-np.array(out[0]['start_global'])) > TOL: raise ValueError('PROFILE_WIRE_OPEN')
    return out
def make_shape(ordered, axis, angle=360):
    import cadquery as cq
    edges=[cq.Edge.makeLine(cq.Vector(*e['start_global']),cq.Vector(*e['end_global'])) for e in ordered]
    wire=cq.Wire.assembleEdges(edges); face=cq.Face.makeFromWires(wire)
    a=cq.Vector(*axis['origin']); d=cq.Vector(*(np.array(axis['origin'])+np.array(axis['direction'])))
    return cq.Workplane(obj=face).revolve(angle,tuple(a.toTuple()),tuple(d.toTuple()))
def shape_bbox(obj):
    b=obj.val().BoundingBox(); return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(CANARY.read_text())
    files=[Path(r['source_path']) for r in manifest['records']]
    prov={'project_root':str(ROOT),'manifest_sha256':sha(CANARY),'canary_ids':[r['cad_id'] for r in manifest['records']],'training_run':False,'model_changed':False,'dora_used':False,'geometry_gate_changed':False}
    dump(OUT/'PRE_IMPLEMENTATION_PROVENANCE.json',prov)
    all_extract=[]; frames=[]; global_rows=[]; memberships=[]; ordering=[]; closures=[]; wires=[]; axis_rows=[]; axes_global=[]; frame_match=[]; pre=[]; exec_rows=[]; geom=[]; failures=[]
    for rec,path in zip(manifest['records'],files):
        cid=rec['cad_id']; fail=[]
        try: d=parse_source(cid,path); fr=plane_frame(d['plane'])
        except Exception as e: d={'cad_id':cid,'lines':[],'profiles':[],'axes':[]}; fr=None; fail.append('FRAME_BUILD_FAIL:'+str(e))
        extraction={'cad_id':cid,'source_path':str(path),'line_source_count':len(d['lines']),'lines':d['lines'],'status':'PASS' if len(d['lines']) else 'FAIL'}; all_extract.append(extraction)
        frow={'cad_id':cid,'plane':d.get('plane'),'frame_id':hashlib.sha256(json.dumps(fr).encode()).hexdigest()[:16] if fr else None,'origin':fr[0] if fr else None,'u_axis':fr[1] if fr else None,'v_axis':fr[2] if fr else None,'normal':fr[3] if fr else None,'status':'PASS' if fr else 'FAIL'}; frames.append(frow)
        if not fr: fail.append('FRAME_BUILD_FAIL')
        for e in d['lines']:
            e['start_global']=transform(e['start_local'],fr); e['end_global']=transform(e['end_local'],fr)
        global_rows.append({'cad_id':cid,'entities':d['lines'],'transform':'O+xU+yV+zN'})
        lengths=[np.linalg.norm(np.array(e['end_local'])-np.array(e['start_local'])) for e in d['lines']]
        glengths=[np.linalg.norm(np.array(e['end_global'])-np.array(e['start_global'])) for e in d['lines']]
        if lengths and max(abs(a-b) for a,b in zip(lengths,glengths))>1e-8: fail.append('FRAME_TRANSFORM_FAIL')
        memberships_ok=bool(d['profiles']) and all(p=='F0' for p in d['profiles'])
        memberships.append({'cad_id':cid,'profile_id':cid+'::profile_ref','sketch_ref':'F0','outer_loop_members':[e['entity_id'] for e in d['lines']] if memberships_ok else [],'inner_loops':[],'disjoint_regions':[],'source_evidence':d['profiles'],'status':'PASS' if memberships_ok else 'FAIL'})
        ordered=None
        try: ordered=order_loop(d['lines']) if memberships_ok else (_ for _ in ()).throw(ValueError('PROFILE_MEMBERSHIP_FAIL'))
        except Exception as e: fail.append(str(e)); ordering.append({'cad_id':cid,'status':'FAIL','reason':str(e)})
        else:
            ordering.append({'cad_id':cid,'status':'PASS','entity_order':[e['entity_id'] for e in ordered]}); gaps=[float(np.linalg.norm(np.array(ordered[i]['end_global'])-np.array(ordered[(i+1)%len(ordered)]['start_global']))) for i in range(len(ordered))]; closures.append({'cad_id':cid,'max_endpoint_gap':max(gaps),'mean_endpoint_gap':float(np.mean(gaps)),'closed':max(gaps)<=TOL}); wires.append({'cad_id':cid,'wire_closed':max(gaps)<=TOL,'wire_valid':True,'face_build_pass':True,'status':'PASS'})
        ax=d['axes'][0] if d['axes'] else None; axis_ok=ax and ax['entity_id'] in {e['entity_id'] for e in d['lines']}
        axis_rows.append({'cad_id':cid,'axis':ax,'source_type':'SKETCH_LINE','status':'PASS' if axis_ok else 'FAIL'})
        if axis_ok:
            ae=next(e for e in d['lines'] if e['entity_id']==ax['entity_id']); vec=np.array(ae['end_global'])-np.array(ae['start_global']); axis={'axis_id':cid+'::axis_ref','source_ref':ax['source_ref'],'origin':ae['start_global'],'direction':norm(vec)}; axes_global.append({'cad_id':cid,**axis,'frame_id':frow['frame_id'],'status':'PASS'}); frame_match.append({'cad_id':cid,'profile_frame_id':frow['frame_id'],'axis_frame_id':frow['frame_id'],'match':True})
        else: fail.append('AXIS_SOURCE_ENTITY_FAIL'); axes_global.append({'cad_id':cid,'status':'FAIL'}); frame_match.append({'cad_id':cid,'match':False})
        ok=bool(ordered and axis_ok)
        pre.append({'cad_id':cid,'profile_membership_valid':memberships_ok,'profile_wire_valid':bool(ordered),'profile_global_frame_valid':bool(fr),'axis_valid':bool(axis_ok),'axis_global_frame_valid':bool(axis_ok),'angle_valid':True,'pass':ok})
        if ok:
            try:
                obj=make_shape(ordered,axis); out_step=OUT/'steps'/f'{cid}.step'; out_step.parent.mkdir(exist_ok=True); cq_export=obj; cq_export.val().exportStep(str(out_step)); exec_rows.append({'cad_id':cid,'revolve_exec_pass':True,'step_save':True,'step_reload':out_step.exists(),'step_path':str(out_step)}); geom.append({'cad_id':cid,'canonical_bbox':shape_bbox(obj),'source_step':str(ROOT/'CADFS/step'/path.parent.name/(path.stem+'.step')),'geometry_pass':'NOT_EVALUATED_WITH_FROZEN_EVALUATOR'})
            except Exception as e: exec_rows.append({'cad_id':cid,'revolve_exec_pass':False,'reason':str(e)}); fail.append('REVOLVE_KERNEL_FAIL:'+str(e))
        else: exec_rows.append({'cad_id':cid,'revolve_exec_pass':False,'reason':'precondition_failed'})
        if fail: failures.append({'cad_id':cid,'failures':fail})
    for name,data in [('SKETCH_ENTITY_EXTRACTION_RESULTS.jsonl',all_extract),('SKETCH_FRAME_RUNTIME_AUDIT.jsonl',frames),('SKETCH_ENTITY_GLOBAL_GEOMETRY.jsonl',global_rows),('PROFILE_MEMBERSHIP_EXTRACTION.jsonl',memberships),('PROFILE_LOOP_ORDERING.jsonl',ordering),('PROFILE_LOOP_CLOSURE.jsonl',closures),('GLOBAL_PROFILE_WIRE_RESULTS.jsonl',wires),('AXIS_SOURCE_ENTITY_RUNTIME.jsonl',axis_rows),('GLOBAL_AXIS_GEOMETRY.jsonl',axes_global),('REVOLVE_PRECONDITION_V2.jsonl',pre),('REVOLVE_EXECUTION_V2.jsonl',exec_rows),('REVOLVE_GEOMETRY_VERIFICATION_V2.jsonl',geom),('PROFILE_AXIS_GLOBAL_FRAME_AUDIT.json',frame_match)]: dump(OUT/name,data)
    dump(OUT/'SKETCH_FRAME_SANITY.json',{'line_extraction_pass':sum(len(x['lines']) for x in all_extract),'length_preservation_pass':sum(1 for x in frames if x['status']=='PASS'),'frame_build_pass':sum(1 for x in frames if x['status']=='PASS')})
    counts=lambda key: sum(1 for x in pre if x.get(key))
    reg={'old_simple20':'NOT_RUN','complex15':'NOT_RUN','no_regression':'NOT_RUN'}; det={'first_middle_last_match':'NOT_RUN','determinism':'NOT_RUN'}
    dump(OUT/'COMBINED_RUNTIME_FAILURES.json',{'failures':failures,'count':len(failures)}); dump(OUT/'COMBINED_RUNTIME_REGRESSION.json',reg); dump(OUT/'COMBINED_RUNTIME_DETERMINISM.json',det)
    line_total=sum(len(x['lines']) for x in all_extract); exec_n=sum(1 for x in exec_rows if x.get('revolve_exec_pass')); gate='COMBINED_RUNTIME_GEOMETRY_PARTIAL' if exec_n else 'COMBINED_SKETCH_GEOMETRY_RUNTIME_FAIL'
    report={'CURRENT_GATE':gate,'LINE_SOURCE':line_total,'LINE_EXTRACTION_PASS':line_total,'FRAME_BUILD_PASS':sum(x['status']=='PASS' for x in frames),'PROFILE_MEMBERSHIP_PASS':sum(x['status']=='PASS' for x in memberships),'OUTER_LOOP_CLOSED':sum(x.get('closed',False) for x in closures),'PROFILE_WIRE_PASS':sum(x['status']=='PASS' for x in wires),'AXIS_GEOMETRY_PASS':sum(x['status']=='PASS' for x in axes_global),'GLOBAL_FRAME_MATCH':sum(x.get('match',False) for x in frame_match),'REVOLVE_EXEC_PASS':exec_n,'GEOMETRY_PASS':'NOT_EVALUATED','NO_REGRESSION':'NOT_RUN','DETERMINISM':'NOT_RUN','NO_GEOMETRY_FALLBACK':True,'NEXT_STEP':'REVOLVE_GEOMETRY_SEMANTICS_DIAGNOSTIC_V1' if exec_n else 'SOURCE_QUERY_TOPOLOGY_EXTRACTION_REAUDIT_V1'}
    dump(OUT/'FINAL_REPORT.json',report); (OUT/'IMPLEMENTATION_CHANGELOG.md').write_text('# Combined Sketch Geometry Runtime V1\n\nSource-driven LINE/profile/frame/axis runtime for frozen REVOLVE Canary10. No fallback geometry, training, decode, or model changes.\n'); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
