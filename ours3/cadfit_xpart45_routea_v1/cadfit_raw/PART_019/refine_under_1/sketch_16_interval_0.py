import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8199, -0.04135, -0.47717), normal=(0.86333, -0.00027, 0.50464), xDir=(-0.00031, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.45656, -0.25703)
loop_1 = loop_1.lineTo(-0.39022, -0.25841)
loop_1 = loop_1.threePointArc((-0.34628, -0.2609), (-0.311, -0.26231))
loop_1 = loop_1.lineTo(-0.24025, -0.26291)
loop_1 = loop_1.lineTo(-0.18763, -0.26477)
loop_1 = loop_1.lineTo(-0.10803, -0.26461)
loop_1 = loop_1.lineTo(-0.00257, -0.26599)
loop_1 = loop_1.threePointArc((0.06024, -0.26608), (0.11206, -0.26605))
loop_1 = loop_1.threePointArc((0.15228, -0.26689), (0.18249, -0.26703))
loop_1 = loop_1.lineTo(0.23709, -0.26413)
loop_1 = loop_1.lineTo(0.30587, -0.26456)
loop_1 = loop_1.lineTo(0.37604, -0.2602)
loop_1 = loop_1.threePointArc((0.42124, -0.25874), (0.45646, -0.257))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_16_interval_0.stl')