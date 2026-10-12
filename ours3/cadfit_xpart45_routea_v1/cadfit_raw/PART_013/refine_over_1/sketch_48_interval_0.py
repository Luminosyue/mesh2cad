import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.90162, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.75523, 0.1688)
loop_1 = loop_1.lineTo(0.75327, 0.21258)
loop_1 = loop_1.lineTo(-0.26659, 0.20328)
loop_1 = loop_1.lineTo(0.22096, 0.20455)
loop_1 = loop_1.lineTo(0.72004, 0.19138)
loop_1 = loop_1.threePointArc((0.73174, 0.18656), (0.74223, 0.17992))
loop_1 = loop_1.lineTo(0.7552, 0.16883)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_48_interval_0.stl')