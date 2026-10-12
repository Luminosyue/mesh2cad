import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31526, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18345, 0.19546)
loop_1 = loop_1.lineTo(0.11316, 0.01258)
loop_1 = loop_1.threePointArc((0.10869, 0.00413), (0.10392, -0.00443))
loop_1 = loop_1.lineTo(0.18345, -0.00428)
loop_1 = loop_1.lineTo(0.18345, 0.1953)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.93)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_32_interval_0.stl')