import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.97), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06765, 0.04703)
loop_1 = loop_1.lineTo(-0.06741, -0.16594)
loop_1 = loop_1.lineTo(-0.05849, -0.20526)
loop_1 = loop_1.lineTo(-0.04588, -0.21748)
loop_1 = loop_1.lineTo(-0.00676, -0.22167)
loop_1 = loop_1.lineTo(0.02773, -0.22151)
loop_1 = loop_1.lineTo(0.05707, -0.20443)
loop_1 = loop_1.lineTo(0.06416, -0.18434)
loop_1 = loop_1.lineTo(0.06766, -0.16702)
loop_1 = loop_1.lineTo(0.06749, -0.03065)
loop_1 = loop_1.threePointArc((0.06723, 0.01635), (0.06758, 0.06492))
loop_1 = loop_1.lineTo(0.06666, 0.16587)
loop_1 = loop_1.lineTo(0.06348, 0.19899)
loop_1 = loop_1.lineTo(0.02639, 0.22313)
loop_1 = loop_1.lineTo(-0.01242, 0.22231)
loop_1 = loop_1.lineTo(-0.04647, 0.21785)
loop_1 = loop_1.lineTo(-0.06365, 0.19826)
loop_1 = loop_1.lineTo(-0.06755, 0.15914)
loop_1 = loop_1.threePointArc((-0.06754, 0.10422), (-0.06764, 0.04738))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_035/PART_035.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_035/PART_035_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
