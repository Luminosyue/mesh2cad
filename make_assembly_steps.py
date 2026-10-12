from pathlib import Path
import json
import cadquery as cq

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
OUT=ROOT/'assemblies'
OUT.mkdir(parents=True,exist_ok=True)

def main():
    report={}
    for case in ('airplane','tank'):
        parts=[]
        for mp in sorted((ROOT/'cases'/case).glob('*/metrics.json')):
            d=json.loads(mp.read_text())
            if '/xpart_parts/' not in d.get('source_path',''): continue
            st=mp.parent/'reconstructed.step'
            if st.exists(): parts.append((d['part_id'],st))
        assy=cq.Assembly(name=f'{case}_xpart_assembly')
        shapes=[]
        for pid,st in parts:
            sh=cq.importers.importStep(str(st)).val()
            shapes.append(sh)
            assy.add(sh,name=pid)
        assembly_step=OUT/f'{case}_xpart_assembly.step'
        compound_step=OUT/f'{case}_xpart_compound.step'
        assy.save(str(assembly_step))
        comp=cq.Compound.makeCompound(shapes)
        cq.exporters.export(cq.Workplane(obj=comp),str(compound_step))
        # Read back both files and count solids.
        ar=cq.importers.importStep(str(assembly_step)).val()
        cr=cq.importers.importStep(str(compound_step)).val()
        report[case]={
          'parts':len(parts),
          'assembly_step':str(assembly_step),
          'compound_step':str(compound_step),
          'assembly_valid':bool(ar.isValid()),
          'assembly_solids':len(ar.Solids()),
          'compound_valid':bool(cr.isValid()),
          'compound_solids':len(cr.Solids())
        }
    (OUT/'assembly_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()

