import json
from pathlib import Path
import cadquery as cq
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts')
asm=root.parent/'assemblies';asm.mkdir(exist_ok=True)
parts=[]
for p in sorted(root.glob('PART_*')):
 st=p/'reconstructed.step'
 if st.exists():
  sh=cq.importers.importStep(str(st)).val();parts.append((p.name,sh))
a=cq.Assembly(name='airplane_xpart_smooth_assembly')
for n,s in parts:a.add(s,name=n)
ap=asm/'airplane_xpart_smooth_assembly.step';a.save(str(ap))
cp=asm/'airplane_xpart_smooth_compound.step';cq.exporters.export(cq.Workplane(obj=cq.Compound.makeCompound([s for _,s in parts])),str(cp))
m={'case':'airplane','parts':len(parts),'smooth_parts':len(parts),'assembly_step':str(ap),'compound_step':str(cp),'assembly_valid':bool(cq.importers.importStep(str(ap)).val().isValid()),'assembly_solids':len(cq.importers.importStep(str(ap)).val().Solids()),'surface_definition':'periodic B-spline section loft; PART_008 uses non-periodic closure due periodic self-intersection'}
(asm/'assembly_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2))

