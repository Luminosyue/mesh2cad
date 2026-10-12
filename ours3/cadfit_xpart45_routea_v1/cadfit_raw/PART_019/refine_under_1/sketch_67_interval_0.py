import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.58), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.72763, 0.81851)
loop_1 = loop_1.lineTo(0.72237, 0.81201)
loop_1 = loop_1.lineTo(0.71828, -0.80746)
loop_1 = loop_1.lineTo(0.72237, -0.87596)
loop_1 = loop_1.lineTo(-0.72763, -0.87135)
loop_1 = loop_1.lineTo(-0.72763, 0.81641)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_67_interval_0.stl')