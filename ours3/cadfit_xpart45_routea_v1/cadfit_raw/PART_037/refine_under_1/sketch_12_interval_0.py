import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00747, -0.00135, 0.15606), normal=(-0.00071, 0.0199, -0.9998), xDir=(0.0, -0.9998, -0.0199))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10319, -0.7269)
loop_1 = loop_1.lineTo(-0.12574, -0.78828)
loop_1 = loop_1.lineTo(0.0976, -0.71969)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_12_interval_0.stl')