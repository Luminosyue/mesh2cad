import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03597, 0.08764, 0.97595), normal=(-0.00132, -0.00278, -1.0), xDir=(0.0, -1.0, 0.00278))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.81519, 0.19768)
loop_1 = loop_1.lineTo(-0.63481, 0.21861)
loop_1 = loop_1.lineTo(-0.63481, -0.2717)
loop_1 = loop_1.lineTo(0.81519, -0.24736)
loop_1 = loop_1.lineTo(0.81519, 0.17944)
loop_1 = loop_1.lineTo(0.81519, 0.19768)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_5_interval_0.stl')