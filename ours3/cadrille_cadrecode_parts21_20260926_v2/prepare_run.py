from pathlib import Path
import ast, json, hashlib, shutil
import numpy as np
import trimesh

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
RUN=ROOT/'ours3/cadrille_cadrecode_parts21_20260926_v2'
ORDER=['2_of_jenga_classic_game','3d_dollhouse_sofa','android_figure_orange','aroma_stainless_steel_milk_frother_2_cup','assorted_vegetable_set','baby_car','birdhouse','cube','dvd_player','fire_truck','mini_excavator','mini_fire_engine','paintmaker','pottery_large','pressure_cooker','robot','speaker_big','tank','toaster','winerack','airplane']

def fps(points,k=256):
    selected=np.empty(k,dtype=int); distances=np.full(len(points),np.inf); idx=0
    for i in range(k):
        selected[i]=idx
        distances=np.minimum(distances,((points-points[idx])**2).sum(-1))
        idx=int(distances.argmax())
    return points[selected]

def main():
    RUN.mkdir(exist_ok=True)
    originals={x['OBJECT_ID']:x for x in json.loads((ROOT/'ours3/full20_object_mesh_to_cad_assembly_v1/manifests/FULL20_OBJECT_MANIFEST.json').read_text())}
    baseline=Path('/var/tmp/cuiyuehan_full20_completion_20260925/cadfit_baseline_full20/MANIFEST.json')
    base={x['object']:x for x in json.loads(baseline.read_text())['cases']}
    rows=[]
    for case in ORDER:
        if case=='airplane':
            sources={p.parent.name:str(p) for p in sorted((ROOT/'p3_xpart_open_cases/airplane/xpart_parts').glob('PART_*/complete_part_*.obj'))}
            full=next((ROOT/'p3_xpart_open_cases/airplane/source').glob('*.obj'))
        else:
            sources=base[case]['source_by_part']; full=Path(originals[case]['FULL_MESH_PATH'])
            assert len(sources)==originals[case]['PART_N']
        parts=[]
        for part,source in sorted(sources.items()):
            source=Path(source); assert source.is_file(),source
            out=RUN/'inputs'/case/part;out.mkdir(parents=True,exist_ok=True)
            mesh=trimesh.load(source,force='mesh',process=False)
            if isinstance(mesh,trimesh.Scene):mesh=mesh.dump(concatenate=True)
            assert len(mesh.faces)>0
            center=mesh.bounds.mean(axis=0);extent=float(max(mesh.extents));assert extent>0
            mesh.export(out/'source.stl')
            normalized=mesh.copy();normalized.vertices=(normalized.vertices-center)*2/extent
            for attempt in range(3):
                np.random.seed(20260926+attempt)
                points,_=trimesh.sample.sample_surface(normalized,8192)
                np.save(out/f'points_{attempt}.npy',fps(points).astype(np.float32))
            d=dict(case=case,part=part,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),input_stl=str(out/'source.stl'),center=center.tolist(),extent=extent,world_scale=extent/200.0,world_translation=center.tolist(),points=[str(out/f'points_{i}.npy') for i in range(3)])
            (out/'transform.json').write_text(json.dumps(d,indent=2));parts.append(d)
        rows.append(dict(case=case,required_parts=len(parts),full_mesh=str(full),parts=parts))
        print(case,len(parts),flush=True)
    (RUN/'MANIFEST.json').write_text(json.dumps(dict(cases=rows,total_parts=sum(x['required_parts'] for x in rows),protocol='Same X-Part input parts for both methods; centered uniform normalization; inverse x_world=x_cad*extent/200+center; no predicted-bbox fitting; three deterministic surface resamplings only on failed parts'),indent=2))
    notebook=json.loads(Path('/tmp/cad-recode-official/demo.ipynb').read_text())
    definitions=[]
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        source=''.join(cell['source'])
        if 'class CADRecode' in source:
            tree=ast.parse(source)
            definitions=[ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.ClassDef)]
    header='import torch\nfrom torch import nn\nfrom transformers import Qwen2ForCausalLM,Qwen2Model,PreTrainedModel\nfrom transformers.modeling_outputs import CausalLMOutputWithPast\n'
    (RUN/'cadrecode_model.py').write_text(header+'\n\n'.join(definitions))
    print('PREPARED',sum(x['required_parts'] for x in rows),flush=True)

if __name__=='__main__':main()
