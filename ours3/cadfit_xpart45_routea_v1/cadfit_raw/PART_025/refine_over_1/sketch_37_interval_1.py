import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08495, -0.03588, -0.00022), normal=(0.46126, 0.88727, -7e-05), xDir=(0.88727, -0.46126, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08296, -0.18176)
loop_1 = loop_1.threePointArc((0.0888, -0.18134), (0.09487, -0.18093))
loop_1 = loop_1.lineTo(0.14449, -0.14541)
loop_1 = loop_1.threePointArc((0.14297, -0.15177), (0.14169, -0.1571))
loop_1 = loop_1.lineTo(0.15729, -0.17419)
loop_1 = loop_1.lineTo(0.17038, -0.18013)
loop_1 = loop_1.lineTo(0.15104, -0.18279)
loop_1 = loop_1.threePointArc((0.13769, -0.18275), (0.12796, -0.18278))
loop_1 = loop_1.lineTo(0.11575, -0.1821)
loop_1 = loop_1.lineTo(0.1027, -0.18214)
loop_1 = loop_1.lineTo(0.08413, -0.18178)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_37_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_37_interval_1.stl')