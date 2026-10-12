import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86539, -0.31851)
loop_1 = loop_1.lineTo(-0.71436, -0.53388)
loop_1 = loop_1.lineTo(-0.7718, -0.54182)
loop_1 = loop_1.lineTo(-0.77151, -0.46696)
loop_1 = loop_1.lineTo(-0.74154, -0.50492)
loop_1 = loop_1.lineTo(-0.73057, -0.51738)
loop_1 = loop_1.lineTo(-0.74197, -0.4999)
loop_1 = loop_1.lineTo(-0.86525, -0.31871)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_43_interval_0.stl')