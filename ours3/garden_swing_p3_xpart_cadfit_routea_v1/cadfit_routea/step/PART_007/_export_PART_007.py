import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0023, 0.06501)
loop_1 = loop_1.lineTo(0.00885, 0.0641)
loop_1 = loop_1.lineTo(0.02749, 0.05895)
loop_1 = loop_1.threePointArc((0.03323, 0.05565), (0.03911, 0.05205))
loop_1 = loop_1.lineTo(0.05153, 0.04048)
loop_1 = loop_1.lineTo(0.05756, 0.02995)
loop_1 = loop_1.lineTo(0.06266, 0.01083)
loop_1 = loop_1.lineTo(0.06404, -0.007)
loop_1 = loop_1.lineTo(0.05602, -0.03412)
loop_1 = loop_1.threePointArc((0.0498, -0.04256), (0.04264, -0.0508))
loop_1 = loop_1.threePointArc((0.03145, -0.05895), (0.02312, -0.06272))
loop_1 = loop_1.lineTo(0.00875, -0.06724)
loop_1 = loop_1.threePointArc((-0.0028, -0.06716), (-0.01482, -0.06691))
loop_1 = loop_1.threePointArc((-0.02606, -0.06446), (-0.03055, -0.0626))
loop_1 = loop_1.threePointArc((-0.03972, -0.05762), (-0.04888, -0.05205))
loop_1 = loop_1.threePointArc((-0.06018, -0.04087), (-0.06174, -0.03797))
loop_1 = loop_1.threePointArc((-0.06356, -0.03259), (-0.06504, -0.02701))
loop_1 = loop_1.threePointArc((-0.06739, -0.01356), (-0.06826, -0.00541))
loop_1 = loop_1.threePointArc((-0.06589, 0.01202), (-0.06375, 0.02177))
loop_1 = loop_1.lineTo(-0.05489, 0.03782)
loop_1 = loop_1.lineTo(-0.04214, 0.05046)
loop_1 = loop_1.threePointArc((-0.02713, 0.05931), (-0.01853, 0.06244))
loop_1 = loop_1.threePointArc((-0.00947, 0.06477), (-0.00722, 0.065))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/garden_swing_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/garden_swing_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
