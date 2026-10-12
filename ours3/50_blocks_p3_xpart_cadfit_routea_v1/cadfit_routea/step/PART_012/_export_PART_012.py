import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.96), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26957, -0.00322)
loop_1 = loop_1.lineTo(-0.26852, -0.02882)
loop_1 = loop_1.threePointArc((-0.26726, -0.03974), (-0.2654, -0.04959))
loop_1 = loop_1.threePointArc((-0.25388, -0.08451), (-0.23901, -0.11602))
loop_1 = loop_1.threePointArc((-0.19593, -0.17298), (-0.1424, -0.21494))
loop_1 = loop_1.threePointArc((-0.12647, -0.22418), (-0.111, -0.23163))
loop_1 = loop_1.threePointArc((-0.08167, -0.24169), (-0.05308, -0.2478))
loop_1 = loop_1.threePointArc((-0.02697, -0.25116), (-0.00223, -0.2525))
loop_1 = loop_1.threePointArc((0.01558, -0.25318), (0.03212, -0.25221))
loop_1 = loop_1.threePointArc((0.08373, -0.24347), (0.13107, -0.22817))
loop_1 = loop_1.threePointArc((0.1424, -0.22286), (0.15229, -0.21702))
loop_1 = loop_1.threePointArc((0.16532, -0.20904), (0.17659, -0.20053))
loop_1 = loop_1.threePointArc((0.1887, -0.19113), (0.19907, -0.18143))
loop_1 = loop_1.threePointArc((0.20884, -0.17203), (0.21674, -0.16237))
loop_1 = loop_1.lineTo(0.22628, -0.151)
loop_1 = loop_1.threePointArc((0.2397, -0.12781), (0.25067, -0.10514))
loop_1 = loop_1.threePointArc((0.26101, -0.07297), (0.26717, -0.04169))
loop_1 = loop_1.threePointArc((0.26802, -0.02233), (0.26748, -0.00428))
loop_1 = loop_1.lineTo(0.26531, 0.02228)
loop_1 = loop_1.lineTo(0.26196, 0.04203)
loop_1 = loop_1.threePointArc((0.25403, 0.06679), (0.24559, 0.08972))
loop_1 = loop_1.threePointArc((0.23736, 0.10689), (0.22837, 0.12219))
loop_1 = loop_1.threePointArc((0.21859, 0.13743), (0.20863, 0.15104))
loop_1 = loop_1.threePointArc((0.1748, 0.18616), (0.13845, 0.21483))
loop_1 = loop_1.lineTo(0.11561, 0.22768)
loop_1 = loop_1.threePointArc((0.08102, 0.2417), (0.04701, 0.25114))
loop_1 = loop_1.threePointArc((0.03143, 0.25337), (0.01687, 0.25373))
loop_1 = loop_1.threePointArc((0.00065, 0.25385), (-0.01435, 0.25306))
loop_1 = loop_1.threePointArc((-0.038, 0.25013), (-0.06001, 0.24632))
loop_1 = loop_1.threePointArc((-0.0763, 0.24192), (-0.09099, 0.23653))
loop_1 = loop_1.threePointArc((-0.1077, 0.23005), (-0.12271, 0.22281))
loop_1 = loop_1.threePointArc((-0.14165, 0.2115), (-0.15851, 0.19958))
loop_1 = loop_1.threePointArc((-0.1823, 0.18105), (-0.20317, 0.16178))
loop_1 = loop_1.threePointArc((-0.22492, 0.13327), (-0.24224, 0.10418))
loop_1 = loop_1.threePointArc((-0.25352, 0.07926), (-0.26214, 0.05499))
loop_1 = loop_1.threePointArc((-0.26446, 0.04518), (-0.26621, 0.0362))
loop_1 = loop_1.threePointArc((-0.26833, 0.01612), (-0.26946, -0.0027))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.92)
result = solid_1

# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(-0.15831, -0.0212, -0.0262), normal=(0.99316, 0.11668, -0.00494), xDir=(0.11668, -0.99317, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(-0.13746, 0.97269)
loop_1 = loop_1.threePointArc((-0.12399, 0.97258), (-0.10997, 0.97207))
loop_1 = loop_1.threePointArc((-0.08366, 0.97203), (-0.06146, 0.97234))
loop_1 = loop_1.threePointArc((-0.01421, 0.97186), (0.02884, 0.97221))
loop_1 = loop_1.threePointArc((0.04693, 0.9718), (0.06099, 0.97216))
loop_1 = loop_1.threePointArc((0.08593, 0.9723), (0.10782, 0.97189))
loop_1 = loop_1.lineTo(0.16652, 0.97184)
loop_1 = loop_1.lineTo(0.17868, 0.97142)
loop_1 = loop_1.lineTo(0.19404, 0.97011)
loop_1 = loop_1.lineTo(0.2152, 0.96474)
loop_1 = loop_1.threePointArc((0.2276, 0.95695), (0.23741, 0.95009))
loop_1 = loop_1.lineTo(0.25009, 0.93327)
loop_1 = loop_1.lineTo(-0.25777, 0.93346)
loop_1 = loop_1.lineTo(-0.24942, 0.94867)
loop_1 = loop_1.lineTo(-0.23555, 0.96184)
loop_1 = loop_1.lineTo(-0.2154, 0.97051)
loop_1 = loop_1.threePointArc((-0.20313, 0.97163), (-0.19264, 0.97271))
loop_1 = loop_1.threePointArc((-0.16366, 0.9725), (-0.13898, 0.9727))
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(0.33)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_012/PART_012.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_012/PART_012_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
