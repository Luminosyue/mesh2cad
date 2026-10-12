import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18589, 0.0086)
loop_1 = loop_1.lineTo(-0.17248, 0.00467)
loop_1 = loop_1.threePointArc((-0.05565, 0.00407), (0.05618, 0.00409))
loop_1 = loop_1.lineTo(0.18175, 0.00464)
loop_1 = loop_1.threePointArc((0.18783, 0.00564), (0.19328, 0.00694))
loop_1 = loop_1.lineTo(0.23867, 0.00573)
loop_1 = loop_1.threePointArc((0.24087, -0.00528), (0.23832, -0.00804))
loop_1 = loop_1.threePointArc((0.14911, -0.0089), (0.05648, -0.00878))
loop_1 = loop_1.lineTo(-0.1759, -0.00847)
loop_1 = loop_1.threePointArc((-0.20508, -0.00852), (-0.23511, -0.00766))
loop_1 = loop_1.lineTo(-0.23981, 0.00714)
loop_1 = loop_1.lineTo(-0.20412, 0.00798)
loop_1 = loop_1.threePointArc((-0.19518, 0.0083), (-0.18622, 0.00858))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/dvd_player_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_005/PART_005.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/dvd_player_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_005/PART_005_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
