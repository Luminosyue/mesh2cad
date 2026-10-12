import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.62444), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05613, -0.89232)
loop_1 = loop_1.lineTo(-0.0545, -0.98841)
loop_1 = loop_1.threePointArc((-0.03595, -0.99906), (-0.02396, -0.99857))
loop_1 = loop_1.lineTo(0.04106, -0.99804)
loop_1 = loop_1.threePointArc((0.04889, -0.9937), (0.05273, -0.98756))
loop_1 = loop_1.threePointArc((0.05435, -0.0933), (0.0567, 0.83709))
loop_1 = loop_1.lineTo(0.0545, 0.98928)
loop_1 = loop_1.threePointArc((0.0348, 0.9998), (0.02148, 0.9992))
loop_1 = loop_1.lineTo(-0.0437, 0.99865)
loop_1 = loop_1.lineTo(-0.05544, 0.98488)
loop_1 = loop_1.lineTo(-0.05613, -0.89089)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.25)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_009/PART_009.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_009/PART_009_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
