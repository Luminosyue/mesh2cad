"""Assemble the reconstructed STEP parts in their original coordinates.
Usage: python rebuild_assembly.py --parts ../tank_cadquery_features
"""
from pathlib import Path
import argparse
import cadquery as cq

def assemble(parts):
    result=cq.Assembly(name='Tank_CadQuery_Assembly')
    for i in range(45):
        name=f'PART_{i:03d}'
        shape=cq.importers.importStep(str(parts/name/(name+'.step'))).val()
        result.add(shape,name=name)
    return result

if __name__=='__main__':
    parent=Path(__file__).resolve().parent.parent
    default=next((parent/name for name in ['tank_cadquery_features','xpart_parts_cadquery_features'] if (parent/name).is_dir()),parent/'tank_cadquery_features')
    parser=argparse.ArgumentParser();parser.add_argument('--parts',type=Path,default=default);args=parser.parse_args()
    assemble(args.parts).export(str(Path(__file__).with_name('tank_assembly.step')))
