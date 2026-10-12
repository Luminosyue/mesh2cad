import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.18678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56443, 0.15268)
loop_1 = loop_1.lineTo(0.54785, 0.14754)
loop_1 = loop_1.lineTo(0.53249, 0.14528)
loop_1 = loop_1.lineTo(0.51791, 0.15255)
loop_1 = loop_1.lineTo(0.51818, 0.2013)
loop_1 = loop_1.lineTo(0.56415, 0.20119)
loop_1 = loop_1.lineTo(0.56443, 0.15274)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_50_interval_0.stl')