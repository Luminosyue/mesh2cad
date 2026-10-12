import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1684, -0.11352)
loop_1 = loop_1.lineTo(-0.15385, -0.11415)
loop_1 = loop_1.lineTo(-0.1399, -0.16453)
loop_1 = loop_1.threePointArc((-0.14672, -0.16752), (-0.15318, -0.1706))
loop_1 = loop_1.threePointArc((-0.16123, -0.17084), (-0.16859, -0.17061))
loop_1 = loop_1.lineTo(-0.19578, -0.14438)
loop_1 = loop_1.lineTo(-0.19523, -0.13011)
loop_1 = loop_1.lineTo(-0.18253, -0.11764)
loop_1 = loop_1.lineTo(-0.1684, -0.11352)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_20_interval_0.stl')