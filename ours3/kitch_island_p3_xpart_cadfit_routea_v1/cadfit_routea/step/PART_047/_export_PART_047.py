import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05774, 0.02238)
loop_1 = loop_1.lineTo(-0.06851, 0.02125)
loop_1 = loop_1.lineTo(-0.06358, 0.0077)
loop_1 = loop_1.lineTo(-0.05854, -0.00293)
loop_1 = loop_1.lineTo(-0.0573, -0.01327)
loop_1 = loop_1.lineTo(-0.04703, -0.02225)
loop_1 = loop_1.threePointArc((-0.0198, -0.0219), (0.00845, -0.02195))
loop_1 = loop_1.lineTo(0.04843, -0.02177)
loop_1 = loop_1.lineTo(0.05895, -0.01536)
loop_1 = loop_1.lineTo(0.06158, -0.00228)
loop_1 = loop_1.lineTo(0.06633, 0.00856)
loop_1 = loop_1.lineTo(0.06922, 0.02082)
loop_1 = loop_1.lineTo(0.05808, 0.02202)
loop_1 = loop_1.lineTo(-0.05062, 0.02232)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_047/PART_047.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_047/PART_047_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
