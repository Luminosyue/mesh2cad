import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02764, 0.21193)
loop_1 = loop_1.lineTo(0.04524, 0.20898)
loop_1 = loop_1.lineTo(0.0623, 0.19574)
loop_1 = loop_1.lineTo(0.07087, 0.17838)
loop_1 = loop_1.lineTo(0.06876, 0.16098)
loop_1 = loop_1.lineTo(0.05308, 0.14357)
loop_1 = loop_1.lineTo(0.02743, 0.13953)
loop_1 = loop_1.lineTo(0.00988, 0.14915)
loop_1 = loop_1.lineTo(-0.00283, 0.16133)
loop_1 = loop_1.lineTo(-0.00634, 0.17874)
loop_1 = loop_1.lineTo(0.00275, 0.19621)
loop_1 = loop_1.lineTo(0.02756, 0.21189)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_36_interval_0.stl')