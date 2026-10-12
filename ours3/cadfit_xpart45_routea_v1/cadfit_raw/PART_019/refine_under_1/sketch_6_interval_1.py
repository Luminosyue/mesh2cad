import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.13304, 0.00021, 0.30924), normal=(-0.51315, -0.0004, 0.8583), xDir=(-0.00078, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.70103, 0.38279)
loop_1 = loop_1.lineTo(0.64675, 0.37606)
loop_1 = loop_1.threePointArc((0.6093, 0.37137), (0.57947, 0.36795))
loop_1 = loop_1.lineTo(0.71958, 0.36801)
loop_1 = loop_1.lineTo(0.70103, 0.38279)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_6_interval_1.stl')