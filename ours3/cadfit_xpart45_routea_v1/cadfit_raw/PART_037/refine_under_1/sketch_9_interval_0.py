import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00747, -0.00135, 0.15606), normal=(-0.00071, 0.0199, -0.9998), xDir=(0.0, -0.9998, -0.0199))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14126, -0.76473)
loop_1 = loop_1.lineTo(0.0928, -0.72081)
loop_1 = loop_1.lineTo(-0.13513, -0.77425)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_9_interval_0.stl')