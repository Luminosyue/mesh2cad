import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05383, 0.16774, 0.00173), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.80975, 0.03557)
loop_1 = loop_1.lineTo(-0.79713, -0.0313)
loop_1 = loop_1.threePointArc((-0.80691, -0.03345), (-0.80975, -0.03356))
loop_1 = loop_1.lineTo(-0.82695, -0.01916)
loop_1 = loop_1.lineTo(-0.82998, -0.00102)
loop_1 = loop_1.threePointArc((-0.82949, 0.00452), (-0.82917, 0.00986))
loop_1 = loop_1.lineTo(-0.80975, 0.03557)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)
plane_2 = cq.Plane(origin=(-0.02, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.98658, 0.0477)
loop_1 = loop_1.threePointArc((-0.99703, 0.03602), (-0.99952, 0.02117))
loop_1 = loop_1.threePointArc((-0.99987, -0.00812), (-0.99831, -0.03419))
loop_1 = loop_1.threePointArc((-0.98298, -0.04765), (-0.96606, -0.04562))
loop_1 = loop_1.threePointArc((-0.95267, -0.04104), (-0.94275, -0.03519))
loop_1 = loop_1.threePointArc((-0.92286, -0.03373), (-0.9044, -0.03445))
loop_1 = loop_1.lineTo(0.30301, -0.03572)
loop_1 = loop_1.lineTo(0.99719, -0.03311)
loop_1 = loop_1.lineTo(0.98829, -0.01111)
loop_1 = loop_1.lineTo(-0.14279, -0.00917)
loop_1 = loop_1.lineTo(-0.14259, 0.00686)
loop_1 = loop_1.lineTo(0.99336, 0.01179)
loop_1 = loop_1.threePointArc((0.99912, 0.02448), (0.99597, 0.03086))
loop_1 = loop_1.lineTo(-0.16438, 0.03411)
loop_1 = loop_1.lineTo(-0.36457, 0.03514)
loop_1 = loop_1.threePointArc((-0.37833, 0.03813), (-0.3898, 0.0375))
loop_1 = loop_1.lineTo(-0.93372, 0.03669)
loop_1 = loop_1.threePointArc((-0.94555, 0.0373), (-0.95476, 0.04174))
loop_1 = loop_1.lineTo(-0.97545, 0.04809)
loop_1 = loop_1.lineTo(-0.98658, 0.0477)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.02)
plane_3 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_3 = cq.Workplane(plane_3)
loop_1 = sketch_3.moveTo(-0.00675, -0.00189)
loop_1 = loop_1.circle(0.03385)
sketch_3=sketch_3.add(loop_1)
solid_3 = sketch_3.extrude(1.95)

result = solid_1
result = result.add(solid_2)
result = result.add(solid_3)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_011/PART_011.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_011/PART_011_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
