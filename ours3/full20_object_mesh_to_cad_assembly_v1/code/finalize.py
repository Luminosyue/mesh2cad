import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,csv,sys,time,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1')
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(fontpath,n)
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def short(s):
 return {'aroma_stainless_steel_milk_frother_2_cup':'Milk frother','3d_dollhouse_sofa':'Dollhouse sofa','android_figure_orange':'Android figure','2_of_jenga_classic_game':'Jenga','assorted_vegetable_set':'Vegetable set'}.get(s,s.replace('_',' ').title())
def paste(im,p,box):
 x,y,w,h=box;a=Image.open(p).convert('RGB');a=ImageOps.contain(a,(w,h),Image.Resampling.LANCZOS);im.paste(a,(x+(w-a.width)//2,y+(h-a.height)//2))
def finalize():
 manifest=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text());rs=[];prs=[]
 for c in manifest:
  d=O/'objects'/c['OBJECT_ID'];p=d/'OBJECT_RESULT.json';r=json.loads(p.read_text()) if p.exists() else dict(OBJECT_ID=c['OBJECT_ID'],PART_N=c['PART_N'],FULL_ASSEMBLY_PASS=False,FAILURE_REASON='NOT_COMPLETED')
  rs.append(r)
  for p in sorted((d/'cad_parts').glob('*/result.json')):prs.append(json.loads(p.read_text()))
 successes=[r for r in rs if r.get('FULL_ASSEMBLY_PASS')];n=len(successes);totalparts=sum(c['PART_N'] for c in manifest);gallery=O/'paper_demo';gallery.mkdir(exist_ok=True)
 for pair,filename in ([] if '--preview' in sys.argv else [(False,'FULL20_ASSEMBLED_CAD_GALLERY.png'),(True,'FULL20_MESH_TO_CAD_GALLERY.png')]):
  cw,ch=1000,840;im=Image.new('RGB',(cw*4,ch*5+170),'#f7f9fc');dr=ImageDraw.Draw(im);dr.text((42,30),'FULL OBJECT MESH TO CAD ASSEMBLY',font=font(47),fill='#182738');dr.text((44,97),f'{n}/20 complete assemblies | {totalparts} expected parts | Failures retained',font=font(30),fill='#4c5b6a')
  for i,(c,r) in enumerate(zip(manifest,rs)):
   x=i%4*cw;y=i//4*ch+170;d=O/'objects'/c['OBJECT_ID']/'renders';dr.rounded_rectangle((x+12,y+12,x+cw-12,y+ch-12),radius=18,fill='white')
   if r.get('FULL_ASSEMBLY_PASS'):
    if pair:
     paste(im,d/'full_mesh.png',(x+20,y+85,470,600));paste(im,d/'assembled_cad.png',(x+510,y+85,470,600));dr.text((x+50,y+45),'INPUT MESH',font=font(24),fill='#66717c');dr.text((x+540,y+45),'ASSEMBLED CAD',font=font(24),fill='#66717c')
    else:paste(im,d/'assembled_cad.png',(x+20,y+35,960,665))
   else:
    dr.text((x+65,y+300),'INCOMPLETE - NO FULL DEMO',font=font(34),fill='#a14d40');dr.text((x+65,y+365),'See complete part-level failure report',font=font(27),fill='#6f777e')
   dr.text((x+35,y+725),short(c['OBJECT_ID']),font=font(31),fill='#172b40');dr.text((x+35,y+774),f"{c['PART_N']} parts | "+('PASS' if r.get('FULL_ASSEMBLY_PASS') else 'FAILED'),font=font(25),fill='#506477')
  im.save(gallery/filename)
 preferred=['tank','airplane','robot','toaster','fire_truck','mini_excavator','android_figure_orange','pottery_large','aroma_stainless_steel_milk_frother_2_cup','baby_car','pressure_cooker','cube']
 order=sorted(successes,key=lambda r:(r.get('CD',99)>.03,preferred.index(r['OBJECT_ID']) if r['OBJECT_ID'] in preferred else 99,r.get('CD',99)))[:6]
 if order:
  cw,rh=820,660;im=Image.new('RGB',(cw*4,rh*len(order)+150),'white');dr=ImageDraw.Draw(im)
  for j,t in enumerate(['Full mesh','CAD parts','Assembled CAD','Overlay']):dr.text((j*cw+32,45),t,font=font(40),fill='#173047')
  for i,r in enumerate(order):
   for j,f in enumerate(['full_mesh.png','cad_parts.png','assembled_cad.png','overlay.png']):paste(im,O/'objects'/r['OBJECT_ID']/'renders'/f,(j*cw,i*rh+130,cw,rh-75))
   dr.text((25,i*rh+rh+60),short(r['OBJECT_ID'])+f" | {r['PART_N']} parts | CD {r['CD']:.5f} | surface IoU64 {r['IOU']:.3f}",font=font(25),fill='#173047')
  im.save(gallery/'PAPER_MAIN_FULL_OBJECT_DEMO.png')
 tank=next(r for r in rs if r['OBJECT_ID']=='tank')
 if tank.get('FULL_ASSEMBLY_PASS'):
  im=Image.new('RGB',(3200,780),'white');dr=ImageDraw.Draw(im)
  for j,(title,f) in enumerate(zip(['Full Tank Mesh','All CAD Parts','Assembled Tank CAD','Overlay'],['full_mesh.png','cad_parts.png','assembled_cad.png','overlay.png'])):
   dr.text((j*800+25,25),title,font=font(31),fill='#173047');paste(im,O/'objects/tank/renders'/f,(j*800,100,800,650))
  im.save(gallery/'TANK_FULL_DEMO.png');shutil.copy2(O/'objects/tank/renders/exploded.png',gallery/'TANK_EXPLODED.png');shutil.copy2(O/'objects/tank/renders/part_id_view.png',gallery/'TANK_PART029_HIGHLIGHT.png')
 if '--preview' in sys.argv:print('EARLY_COMPLETE_DEMOS',[(r['OBJECT_ID'],r['PART_N']) for r in order]);return
 totals=dict(REQUESTED_OBJECT_N=20,FULL_ASSEMBLY_PASS_N=n,FAILED_OBJECT_N=20-n,TOTAL_PART_N=sum(c['PART_N'] for c in manifest),VALID_PART_CAD_N=sum(p.get('PASS',False) for p in prs),Q14_PASS_N=sum(p.get('Q14_PASS',False) for p in prs),V3_PASS_N=sum(p.get('V3_PASS',False) for p in prs),REUSED_PART_N=sum(p.get('RAW_CAD_PASS',False) for p in prs),NEW_GENERATED_CAD_N=0,STRICT_MODEL_GENERATED_N=sum(p.get('STRICT_MODEL_GENERATED',False) for p in prs),FULL20_OBJECT_CAD_ASSEMBLY_PASS=n==20,FULL20_MODEL_GENERATION_PASS=False,FREE_DISK_GB=shutil.disk_usage('/data').free/1e9,PAPER_MAIN_OBJECTS=[r['OBJECT_ID'] for r in order])
 correction=json.loads((O/'reports/INVENTORY_CORRECTION.json').read_text());totals.update(FULL_INPUT_GATE_PASS_N=correction['FULL_INPUT_GATE_PASS_N'],MISSING_XPART_N=correction['MISSING_XPART_N'],INITIAL_AUDIT_INVALIDATED=True)
 dump(O/'reports/FINAL_GATES.json',totals)
 lines=['# FULL20 Object Mesh to CAD Assembly — Final Report','',f'ROOT: `{O}`','',f'**Complete full assemblies: {n}/20. FULL20_OBJECT_CAD_ASSEMBLY_PASS = {str(n==20).upper()}.**','',f'Frozen selection contains 20 full source meshes and all {totals["TOTAL_PART_N"]} X-Part parts. No failed object was replaced and no part was deleted.','',f'Existing CAD reused/read back: {totals["REUSED_PART_N"]}/{totals["TOTAL_PART_N"]}; new CAD programs generated: 0. New work completes common-frame q14/V3 artifacts, compilation, assembly and rendering.','',f'Valid complete part chain: {totals["VALID_PART_CAD_N"]}/{totals["TOTAL_PART_N"]}; q14: {totals["Q14_PASS_N"]}/{totals["TOTAL_PART_N"]}; V3: {totals["V3_PASS_N"]}/{totals["TOTAL_PART_N"]}.','',f'Tank: 45 parts; complete assembly: {tank.get("FULL_ASSEMBLY_PASS",False)}; assembly type: {tank.get("ASSEMBLY_TYPE","NOT_ASSEMBLED")}. PART_029 reuses the exact frozen generated q stream and STEP; source SHA256 checks preserved. Only that part is marked strict model-generated.','', '## Objects','', '| Object | Parts | Valid parts | Full assembly | CD | Surface IoU64 | Failure |','|---|---:|---:|---|---:|---:|---|']
 for c,r in zip(manifest,rs):lines.append(f"| {c['OBJECT_ID']} | {c['PART_N']} | {r.get('VALID_CAD_PART_N',0)} | {r.get('FULL_ASSEMBLY_PASS',False)} | {r.get('CD')} | {r.get('IOU')} | {r.get('FAILURE_REASON','')} |")
 lines+=['','## Initial completeness audit correction','','The initial audit incorrectly used successful X-Part count instead of original P3 part count. The 20 object identities were retained; counts were explicitly corrected, the initial manifest/hash preserved, and no failed object was replaced. Only 15/20 selected objects satisfy the full input gate. The selected objects require 304 parts, of which 50 X-Part meshes are absent across five objects. Historical object-specific folders were searched without recovering those assets. Initial partial Winerack PASS was invalidated. See INVENTORY_CORRECTION.json and MISSING_XPART_HISTORY_SEARCH.json.']
 lines+=['','## Evaluation and provenance','','CD uses the existing unified CAD benchmark: 20,000 area-weighted surface samples, seed 0, symmetric mean Euclidean nearest-neighbor distance divided by full source mesh bbox diagonal. The existing P3 surface voxel IoU at resolution 64 is reported explicitly as surface IoU64. It must not be interpreted as solid Boolean volume IoU. Open full meshes have undefined volume error. No ICP or prediction-derived alignment was used.','','Part geometry gates compare original reconstructed CAD against q14/V3 CAD; tolerance values were recorded in EXECUTION_CONTRACT.json before the production batch. Historical reconstruction NEEDS_REFINEMENT flags are retained. Passing execution/assembly is not a claim of exact source-mesh reconstruction.','','Compact IR V3 in this project relies on the source semantic parameter template and compiler. The V3 file is delivered with its q14 metadata, source program/template, compiler and transform metadata. No V4 or new grammar was introduced.','','All new q14 parts use the same full-object normalization matrix and inverse. Historical q14 artifacts retain their original frames and explicit inverse mapping. STEP is a compound of all part solids, with part identities and body counts retained in assembly_manifest.json; no boolean union.','','Tank generated output includes a tokenizer <|eot_id|> suffix after the grammar E. It is removed only at the parser input transport boundary; the frozen file and q stream remain byte-identical.','','## Paper demo selection','',', '.join(r['OBJECT_ID'] for r in order) if order else 'No object passes the complete demo gate.','',f'Tank main figure: {"generated" if tank.get("FULL_ASSEMBLY_PASS") else "not generated because the full-object gate failed"}. Galleries retain every frozen object; incomplete objects have explicit failure cards.','', '## Failed parts','']
 lines += [f"- {p['OBJECT_ID']}/{p['PART_ID']}: {p.get('FAILURE_REASON','')}" for p in prs if not p.get('PASS')]
 lines+=['','## Reproduction','','Run `xvfb-run -a python3 code/pipeline.py run` to resume. Existing terminal part results and DONE objects are reused. Individual part repair histories are in cad_parts/<part>/repairs.json. No model training was launched.','', '## Deliverables','']
 for p in ['manifests/FULL20_OBJECT_MANIFEST.csv','tables/FULL20_OBJECT_RESULTS.csv','tables/FULL20_ALL_PART_RESULTS.csv','reports/FULL20_OBJECT_MESH_TO_CAD_ASSEMBLY_FINAL.md','paper_demo/FULL20_ASSEMBLED_CAD_GALLERY.png','paper_demo/FULL20_MESH_TO_CAD_GALLERY.png','paper_demo/PAPER_MAIN_FULL_OBJECT_DEMO.png','paper_demo/TANK_FULL_DEMO.png']:lines.append(f'- `{O/p}`'+(' (not produced: full-object gate failed)' if not (O/p).exists() and not p.endswith('_FINAL.md') else ''))
 (O/'reports/FULL20_OBJECT_MESH_TO_CAD_ASSEMBLY_FINAL.md').write_text('\n'.join(lines)+'\n');print(json.dumps(totals,indent=2))
if __name__=='__main__':
 if '--watch' in sys.argv:
  expected=sum(c['PART_N'] for c in json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text()))
  while len(list((O/'objects').glob('*/OBJECT_RESULT.json')))<20 or len(list((O/'objects').glob('*/cad_parts/*/result.json')))<expected:time.sleep(20)
 finalize()
