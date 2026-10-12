import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.7852, -0.11794, -0.5159), normal=(0.83379, 0.00102, 0.55208), xDir=(0.00123, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66595, 0.16838)
loop_1 = loop_1.lineTo(0.66588, -0.20196)
loop_1 = loop_1.lineTo(0.67127, -0.17581)
loop_1 = loop_1.lineTo(0.6824, -0.10183)
loop_1 = loop_1.lineTo(0.67523, -0.07745)
loop_1 = loop_1.lineTo(0.67479, -0.02785)
loop_1 = loop_1.lineTo(0.67728, 0.00849)
loop_1 = loop_1.lineTo(0.67739, 0.04614)
loop_1 = loop_1.lineTo(0.68127, 0.12021)
loop_1 = loop_1.lineTo(0.67219, 0.14437)
loop_1 = loop_1.lineTo(0.66677, 0.16523)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.9)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_34_interval_0.stl')