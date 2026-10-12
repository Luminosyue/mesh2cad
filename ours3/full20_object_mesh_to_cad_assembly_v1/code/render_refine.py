import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import sys,csv,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import pipeline as p
def render(name):
 import cadquery as cq
 d=p.O/'objects'/name;rs=list(csv.DictReader((d/'PART_MANIFEST.csv').open()));frame=json.loads((d/'OBJECT_FRAME.json').read_text());assert json.loads((d/'OBJECT_RESULT.json').read_text())['FULL_ASSEMBLY_PASS'];s=d/'assembly/assembled.step';before=p.sha(s);full=p.mesh(next(d.glob('full_mesh.*')));meshes=[p.mesh(r['PART_MESH_PATH']) for r in rs];cads=[p.shapemesh(cq.importers.importStep(str(d/'cad_parts'/r['PART_ID']/'part.step')).val()) for r in rs]
 p.render_object(name,full,meshes,cads,frame,rs);assert before==p.sha(s);print('CAMERA_REFINED',name,flush=True)
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as ex:list(ex.map(render,['fire_truck','mini_excavator','android_figure_orange','baby_car','aroma_stainless_steel_milk_frother_2_cup']))
