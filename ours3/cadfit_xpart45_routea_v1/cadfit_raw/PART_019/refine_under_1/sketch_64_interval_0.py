import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.78, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.49471, -0.89887)
loop_1 = loop_1.lineTo(0.44382, -0.90085)
loop_1 = loop_1.threePointArc((0.42514, -0.90953), (0.40546, -0.91619))
loop_1 = loop_1.threePointArc((0.35894, -0.93226), (0.31078, -0.9477))
loop_1 = loop_1.threePointArc((0.27211, -0.95864), (0.2323, -0.96916))
loop_1 = loop_1.threePointArc((0.20057, -0.97574), (0.17092, -0.9828))
loop_1 = loop_1.lineTo(0.11192, -0.99335)
loop_1 = loop_1.threePointArc((0.08142, -0.99687), (0.05024, -0.99966))
loop_1 = loop_1.lineTo(-0.01971, -0.99959)
loop_1 = loop_1.threePointArc((-0.07613, -0.99831), (-0.1342, -0.99611))
loop_1 = loop_1.lineTo(-0.19718, -0.98988)
loop_1 = loop_1.lineTo(-0.25811, -0.97966)
loop_1 = loop_1.lineTo(-0.32155, -0.96494)
loop_1 = loop_1.lineTo(-0.38433, -0.94627)
loop_1 = loop_1.threePointArc((-0.41314, -0.9361), (-0.4423, -0.92512))
loop_1 = loop_1.threePointArc((-0.46803, -0.91233), (-0.49414, -0.89917))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_64_interval_0.stl')