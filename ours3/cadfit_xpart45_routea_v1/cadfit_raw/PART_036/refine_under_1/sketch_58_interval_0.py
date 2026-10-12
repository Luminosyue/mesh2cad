import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96687, 0.2023)
loop_1 = loop_1.lineTo(0.92993, 0.20215)
loop_1 = loop_1.lineTo(0.9301, 0.15268)
loop_1 = loop_1.lineTo(0.94313, 0.14463)
loop_1 = loop_1.lineTo(0.95737, 0.14237)
loop_1 = loop_1.lineTo(0.96855, 0.14495)
loop_1 = loop_1.lineTo(0.97618, 0.17637)
loop_1 = loop_1.lineTo(0.97494, 0.2023)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_58_interval_0.stl')