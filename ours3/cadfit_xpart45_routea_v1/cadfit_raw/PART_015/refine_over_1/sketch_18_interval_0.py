import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.81263, -0.21945, -0.02967), normal=(0.95324, -0.30222, 0.00027), xDir=(-0.30222, -0.95324, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3054, 0.0713)
loop_1 = loop_1.lineTo(0.30559, -0.19644)
loop_1 = loop_1.lineTo(0.2717, -0.19644)
loop_1 = loop_1.lineTo(0.29453, -0.18158)
loop_1 = loop_1.lineTo(0.30238, -0.15031)
loop_1 = loop_1.lineTo(0.30518, -0.13344)
loop_1 = loop_1.lineTo(0.30285, -0.0989)
loop_1 = loop_1.threePointArc((0.30237, -0.08251), (0.30238, -0.06827))
loop_1 = loop_1.lineTo(0.30213, -0.00033)
loop_1 = loop_1.lineTo(0.30188, 0.01099)
loop_1 = loop_1.threePointArc((0.30309, 0.03102), (0.30433, 0.04874))
loop_1 = loop_1.lineTo(0.3054, 0.0713)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_18_interval_0.stl')