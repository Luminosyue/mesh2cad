import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.09417, 0.1287, -0.03913), normal=(-0.02892, 0.96262, -0.26931), xDir=(0.99955, 0.03002, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.85893, -0.10778)
loop_1 = loop_1.lineTo(-0.81147, -0.1053)
loop_1 = loop_1.lineTo(-0.79724, -0.10456)
loop_1 = loop_1.lineTo(0.65201, -0.02887)
loop_1 = loop_1.lineTo(0.66918, -0.04544)
loop_1 = loop_1.lineTo(0.66225, 0.09369)
loop_1 = loop_1.lineTo(0.64124, 0.09247)
loop_1 = loop_1.lineTo(-0.88801, 0.00372)
loop_1 = loop_1.lineTo(-0.87957, -0.12913)
loop_1 = loop_1.lineTo(-0.87861, -0.09447)
loop_1 = loop_1.lineTo(-0.85893, -0.10778)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_2_interval_0.stl')