import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.53912, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0016, -0.09403)
loop_1 = loop_1.lineTo(0.94, -0.09657)
loop_1 = loop_1.lineTo(0.93973, -0.12566)
loop_1 = loop_1.threePointArc((0.93325, -0.12456), (0.92762, -0.12529))
loop_1 = loop_1.threePointArc((0.91355, -0.12567), (0.89961, -0.12525))
loop_1 = loop_1.threePointArc((0.86468, -0.12515), (0.829, -0.12372))
loop_1 = loop_1.lineTo(0.60458, -0.11727)
loop_1 = loop_1.threePointArc((0.53626, -0.11474), (0.46579, -0.1113))
loop_1 = loop_1.threePointArc((0.39872, -0.10953), (0.32956, -0.10653))
loop_1 = loop_1.threePointArc((0.16871, -0.10116), (0.00187, -0.09379))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_18_interval_0.stl')