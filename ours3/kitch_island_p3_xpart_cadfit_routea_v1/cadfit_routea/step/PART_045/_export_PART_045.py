import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.04925, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98813, 0.04448)
loop_1 = loop_1.lineTo(0.99417, 0.03776)
loop_1 = loop_1.lineTo(0.99807, -0.03445)
loop_1 = loop_1.lineTo(-0.99244, -0.03743)
loop_1 = loop_1.threePointArc((-0.99999, 0.001), (-0.99886, 0.03517))
loop_1 = loop_1.lineTo(-0.98813, 0.04448)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.03228), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.05331, -0.99643)
loop_1 = loop_1.threePointArc((-0.04278, -0.99985), (-0.03215, -0.99951))
loop_1 = loop_1.lineTo(0.05057, -0.99896)
loop_1 = loop_1.lineTo(0.05833, -0.98743)
loop_1 = loop_1.lineTo(0.05434, 0.99344)
loop_1 = loop_1.lineTo(-0.0468, 0.99891)
loop_1 = loop_1.threePointArc((-0.05779, 0.98651), (-0.05739, 0.97923))
loop_1 = loop_1.lineTo(-0.05842, -0.9844)
loop_1 = loop_1.lineTo(-0.05331, -0.99643)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.07)

result = solid_1
result = result.add(solid_2)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_045/PART_045.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_045/PART_045_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
