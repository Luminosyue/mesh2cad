import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35852, 0.23183, 0.02676), normal=(-0.00567, 0.87903, 0.47673), xDir=(0.99998, 0.00645, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15052, 0.19512)
loop_1 = loop_1.lineTo(0.57416, 0.19508)
loop_1 = loop_1.lineTo(0.42078, 0.07599)
loop_1 = loop_1.lineTo(0.40788, 0.09465)
loop_1 = loop_1.lineTo(0.383, 0.11574)
loop_1 = loop_1.lineTo(0.34466, 0.13965)
loop_1 = loop_1.lineTo(0.28928, 0.14734)
loop_1 = loop_1.lineTo(0.23991, 0.15211)
loop_1 = loop_1.threePointArc((0.18596, 0.15543), (0.13105, 0.15956))
loop_1 = loop_1.lineTo(0.06583, 0.16107)
loop_1 = loop_1.lineTo(0.00588, 0.16039)
loop_1 = loop_1.lineTo(-0.07725, 0.16412)
loop_1 = loop_1.lineTo(-0.10759, 0.16749)
loop_1 = loop_1.lineTo(-0.13486, 0.1775)
loop_1 = loop_1.threePointArc((-0.14265, 0.18663), (-0.15049, 0.19509))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_18_interval_0.stl')