from pathlib import Path
import json,ast,collections,sys
import numpy as np
import cadquery as cq
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
CAD=ROOT/'partsam/PartObjaverse-Tiny_instance_cad'
OUT=ROOT/'partsam/p1_pair_readiness_audit'
OPS={'Box','Cylinder','Circle','Sketch','Extrude','ExtrudePolygon','Union','Cut','Revolve','PolygonProfile','Axis','TrueRevolve','Fillet','Chamfer'}

def main():
    OUT.mkdir(exist_ok=True)
    data=ROOT/'ours3/exact9998_v1'
    example=json.loads((data/'exact9998_train.json').read_text())[0]
    registry=json.loads((data/'EXACT9998_ASSET_REGISTRY_V1.jsonl').open().readline())
    target=Path(registry['target_path']).read_text()
    surface=np.load(registry['surface_path'],mmap_mode='r')
    token_registry=ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'
    token_row=next(json.loads(line) for line in token_registry.open() if json.loads(line)['cad_id']==registry['cad_id'])
    token=np.load(token_row['curve_token_path'],mmap_mode='r')
    output={'actual_p1':'ours3/p1_operation_aware_structure_loss_v1',
            'training_data':'ours3/exact9998_v1','training_example':example,
            'reference_cad_id':registry['cad_id'],'reference_surface_shape':list(surface.shape),
            'reference_curve_token_shape':list(token.shape),'reference_program_head':target[:2400],
            'operation_vocabulary':sorted(OPS),'reference_registry_keys':list(registry),
            'curve_token_protocol':json.loads((ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/C2_TOKEN_EXPORT_PROTOCOL.json').read_text()),
            'pair_conversion_audit':json.loads((CAD/'FINAL_AUDIT.json').read_text())}
    programs=list(CAD.glob('*/part_*_cad.py'))
    supported_programs=0;calls=collections.Counter()
    for p in programs:
        tree=ast.parse(p.read_text());found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in OPS:found.append(node.func.id)
        supported_programs+=bool(found);calls.update(found)
    output['generated_program_audit']={'programs':len(programs),'programs_containing_p1_dsl_operation_calls':supported_programs,
                                       'operation_calls':dict(calls),'canonical_dsl_files':len(list(CAD.glob('*/program_canonical.dsl'))),
                                       'note':'This checks the current P1 DSL call vocabulary; it does not imply the generated faceted CAD scripts cannot execute.'}
    inventory=json.loads((CAD/'input_inventory.json').read_text())
    ordinary=sorted([r for r in inventory if 100<=r['faces']<=4000],key=lambda r:r['faces'])
    picks=[ordinary[0],ordinary[len(ordinary)//2],min((r for r in inventory if r['watertight']),key=lambda r:r['faces'])]
    samples=[]
    for row in picks:
        step=CAD/Path(row['relative']).with_suffix('.step')
        shape=cq.importers.importStep(str(step)).val()
        record={'relative_path':row['relative'],'input_faces':row['faces'],'cad_faces':len(shape.Faces()),
                'cad_solids':len(shape.Solids()),'valid':shape.isValid(),
                'edge_types':dict(collections.Counter(e.geomType() for e in shape.Edges())),
                'face_types':dict(collections.Counter(f.geomType() for f in shape.Faces()))}
        samples.append(record);print('CAD_SAMPLE',json.dumps(record),flush=True)
    output['cad_topology_sample_audit']=samples
    output['decision']={'same_file_schema_feasible':True,'current_pairs_directly_ready_for_actual_p1':False,
                       'current_p1_ready_confirmed':0,'primary_blockers':['missing canonical operation-program targets','faceted BREP edges encode triangulation, not recovered analytic design curves','missing current C2 sharp-only token registry and surface assets','missing label/operation-mask/context and mesh-to-program geometric validation'],
                       'data_provenance_required':'reconstructed or pseudo CAD supervision; not original CAD design history',
                       'split_unit':'original object folder; keep sibling parts in the same split'}
    (OUT/'p1_pair_readiness_audit.json').write_text(json.dumps(output,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in output.items() if k not in ('training_example','reference_registry_keys')},indent=2,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
