import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.5291, -0.90329, 0.04199), normal=(-0.56969, 0.82184, 0.00597), xDir=(0.82185, 0.5697, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04199, 0.17736)
loop_1 = loop_1.lineTo(0.02789, 0.14247)
loop_1 = loop_1.lineTo(0.02533, 0.08593)
loop_1 = loop_1.lineTo(0.02524, 0.03365)
loop_1 = loop_1.threePointArc((0.02718, -0.01829), (0.02844, -0.07157))
loop_1 = loop_1.lineTo(0.03268, -0.13154)
loop_1 = loop_1.lineTo(0.03829, -0.18299)
loop_1 = loop_1.lineTo(0.04197, 0.17367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_2_interval_0.stl')