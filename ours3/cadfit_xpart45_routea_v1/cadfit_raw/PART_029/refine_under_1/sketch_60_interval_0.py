import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.24), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10906, 0.91403)
loop_1 = loop_1.lineTo(0.10931, 0.80034)
loop_1 = loop_1.lineTo(0.12906, 0.81256)
loop_1 = loop_1.lineTo(0.12886, 0.89226)
loop_1 = loop_1.threePointArc((0.12357, 0.90505), (0.12066, 0.91082))
loop_1 = loop_1.lineTo(0.10906, 0.91403)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_60_interval_0.stl')