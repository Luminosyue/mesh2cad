import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0442, -0.28432, -0.0002), normal=(0.46126, 0.88727, -7e-05), xDir=(0.88727, -0.46126, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08296, -0.18176)
loop_1 = loop_1.threePointArc((0.0888, -0.18134), (0.09487, -0.18093))
loop_1 = loop_1.lineTo(0.11575, -0.1821)
loop_1 = loop_1.lineTo(0.14886, -0.11769)
loop_1 = loop_1.lineTo(0.17544, -0.11999)
loop_1 = loop_1.lineTo(0.18896, -0.12325)
loop_1 = loop_1.lineTo(0.17742, -0.12381)
loop_1 = loop_1.lineTo(0.16734, -0.12466)
loop_1 = loop_1.lineTo(0.14496, -0.14344)
loop_1 = loop_1.threePointArc((0.14313, -0.15109), (0.14169, -0.1571))
loop_1 = loop_1.lineTo(0.15729, -0.17419)
loop_1 = loop_1.lineTo(0.17038, -0.18013)
loop_1 = loop_1.lineTo(0.15104, -0.18279)
loop_1 = loop_1.threePointArc((0.13731, -0.18275), (0.12796, -0.18278))
loop_1 = loop_1.lineTo(0.11405, -0.1821)
loop_1 = loop_1.threePointArc((0.10309, -0.18213), (0.09167, -0.18191))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_33_interval_0.stl')