import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.85941, 0.02055, 0.06457), normal=(-0.99056, -0.13708, 0.00122), xDir=(-0.13708, 0.99056, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30501, 0.22025)
loop_1 = loop_1.lineTo(0.30615, -0.16975)
loop_1 = loop_1.lineTo(-0.28843, -0.16975)
loop_1 = loop_1.lineTo(-0.29378, 0.22025)
loop_1 = loop_1.lineTo(0.29363, 0.22025)
loop_1 = loop_1.lineTo(0.30501, 0.22025)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_43_interval_0.stl')