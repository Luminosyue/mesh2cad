import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45952, 0.0908, 0.26553), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26636, 0.11472)
loop_1 = loop_1.lineTo(0.22272, 0.08746)
loop_1 = loop_1.threePointArc((0.21577, 0.08882), (0.20908, 0.09002))
loop_1 = loop_1.lineTo(0.21018, 0.17129)
loop_1 = loop_1.threePointArc((0.21699, 0.17155), (0.22408, 0.1718))
loop_1 = loop_1.threePointArc((0.23474, 0.16979), (0.23915, 0.16892))
loop_1 = loop_1.lineTo(0.25222, 0.16138)
loop_1 = loop_1.lineTo(0.2657, 0.14169)
loop_1 = loop_1.threePointArc((0.26713, 0.13535), (0.2686, 0.12929))
loop_1 = loop_1.lineTo(0.26636, 0.11472)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_22_interval_0.stl')