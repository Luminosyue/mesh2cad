import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04496, -0.07286, 0.02), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15355, 0.98704)
loop_1 = loop_1.lineTo(0.1064, 0.84825)
loop_1 = loop_1.lineTo(0.11014, 0.87261)
loop_1 = loop_1.lineTo(0.11167, 0.88328)
loop_1 = loop_1.lineTo(0.11545, 0.90308)
loop_1 = loop_1.lineTo(0.11688, 0.91527)
loop_1 = loop_1.lineTo(0.12426, 0.93659)
loop_1 = loop_1.lineTo(0.12631, 0.94879)
loop_1 = loop_1.lineTo(0.13447, 0.96496)
loop_1 = loop_1.lineTo(0.14793, 0.9823)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_10_interval_0.stl')