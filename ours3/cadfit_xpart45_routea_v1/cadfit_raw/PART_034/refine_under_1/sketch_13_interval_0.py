import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04613, -0.94415, 0.02556), normal=(-0.06485, 0.99785, -0.00971), xDir=(0.99789, 0.06485, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31419, -0.20918)
loop_1 = loop_1.lineTo(0.28966, -0.20918)
loop_1 = loop_1.lineTo(0.29002, 0.18084)
loop_1 = loop_1.lineTo(-0.31382, 0.18084)
loop_1 = loop_1.lineTo(-0.31419, -0.20645)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_13_interval_0.stl')