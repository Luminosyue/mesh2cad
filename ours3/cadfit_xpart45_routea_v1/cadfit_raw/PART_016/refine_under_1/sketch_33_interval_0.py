import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.70215, 0.29077, -0.06839), normal=(-0.93113, -0.36469, 0.00075), xDir=(-0.36469, 0.93113, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30006, 0.16373)
loop_1 = loop_1.lineTo(0.29941, -0.17627)
loop_1 = loop_1.lineTo(-0.29988, -0.17627)
loop_1 = loop_1.lineTo(-0.3008, 0.16373)
loop_1 = loop_1.lineTo(0.29034, 0.16373)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.49)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_33_interval_0.stl')