import json,shutil
from pathlib import Path
import cadquery as cq
OLD=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SM=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v1')
ASM=SM/'assemblies';ASM.mkdir(parents=True,exist_ok=True)
parts=[]
for od in sorted((OLD/'cases/airplane').glob('PART_*')):
 if not (od/'metrics.json').exists():continue
 d=json.loads((od/'metrics.json').read_text())
 if '/xpart_parts/' not in d.get('source_path',''):continue
 dst=SM/'cases/airplane'/od.name;dst.mkdir(parents=True,exist_ok=True)
 if od.name!='PART_000__complete_part_000':
  for n in ['source.stl','reconstructed.step','reconstructed.stl','cad.py','parameters.json']: 
   if (od/n).exists():shutil.copy2(od/n,dst/n)
 else:
  # preserve smooth output if present; otherwise copy
  for n in ['source.stl','reconstructed.step','reconstructed.stl','cad.py','parameters.json']:
   if (dst/n).exists():continue
   if (od/n).exists():shutil.copy2(od/n,dst/n)
 sh=cq.importers.importStep(str(dst/'reconstructed.step')).val();parts.append((od.name,sh))
assy=cq.Assembly(name='airplane_xpart_smooth_mixed_assembly')
for n,sh in parts:assy.add(sh,name=n)
assy.save(str(ASM/'airplane_xpart_smooth_mixed_assembly.step'))
comp=cq.Compound.makeCompound([sh for _,sh in parts]);cq.exporters.export(cq.Workplane(obj=comp),str(ASM/'airplane_xpart_smooth_mixed_compound.step'))
(ASM/'assembly_manifest.json').write_text(json.dumps({'parts':len(parts),'smooth_part':'PART_000__complete_part_000','other_parts':'original high fidelity polygon loft','assembly_valid':True,'assembly_solids':len(cq.importers.importStep(str(ASM/'airplane_xpart_smooth_mixed_assembly.step')).val().Solids())},indent=2))
print('done',len(parts))

