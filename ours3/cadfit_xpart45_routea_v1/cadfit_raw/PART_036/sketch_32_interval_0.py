import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.97, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07241, 0.20814)
loop_1 = loop_1.lineTo(-0.05693, 0.20107)
loop_1 = loop_1.lineTo(-0.04565, 0.19595)
loop_1 = loop_1.lineTo(-0.04178, 0.185)
loop_1 = loop_1.threePointArc((-0.04189, 0.17558), (-0.04308, 0.17269))
loop_1 = loop_1.lineTo(-0.04857, 0.16087)
loop_1 = loop_1.threePointArc((-0.05712, 0.15147), (-0.05823, 0.15076))
loop_1 = loop_1.lineTo(-0.07437, 0.1385)
loop_1 = loop_1.lineTo(-0.0922, 0.13772)
loop_1 = loop_1.lineTo(-0.10471, 0.14405)
loop_1 = loop_1.lineTo(-0.11562, 0.16091)
loop_1 = loop_1.lineTo(-0.11648, 0.17881)
loop_1 = loop_1.lineTo(-0.10923, 0.19476)
loop_1 = loop_1.lineTo(-0.09176, 0.20698)
loop_1 = loop_1.lineTo(-0.07465, 0.20842)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.93)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_32_interval_0.stl')