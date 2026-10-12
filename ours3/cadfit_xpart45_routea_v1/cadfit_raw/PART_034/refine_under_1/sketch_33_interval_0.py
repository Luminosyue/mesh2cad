import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87816, -0.01823, 0.01004), normal=(0.99411, -0.10841, -0.0005), xDir=(-0.10841, -0.99411, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30135, 0.11379)
loop_1 = loop_1.lineTo(0.30547, 0.08616)
loop_1 = loop_1.lineTo(0.30739, 0.06783)
loop_1 = loop_1.threePointArc((0.30765, 0.02869), (0.30786, -0.00937))
loop_1 = loop_1.threePointArc((0.30661, -0.03408), (0.30601, -0.05533))
loop_1 = loop_1.lineTo(0.30605, -0.07905)
loop_1 = loop_1.threePointArc((0.30491, -0.10437), (0.30373, -0.12801))
loop_1 = loop_1.lineTo(0.30179, -0.14304)
loop_1 = loop_1.lineTo(0.30135, 0.11119)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_33_interval_0.stl')