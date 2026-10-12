import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.6247, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68031, -0.62745)
loop_1 = loop_1.lineTo(0.68568, -0.64712)
loop_1 = loop_1.lineTo(0.70708, -0.6537)
loop_1 = loop_1.lineTo(0.71713, -0.659)
loop_1 = loop_1.lineTo(0.73399, -0.66018)
loop_1 = loop_1.lineTo(0.74992, -0.66486)
loop_1 = loop_1.lineTo(0.77117, -0.68908)
loop_1 = loop_1.lineTo(0.77442, -0.71571)
loop_1 = loop_1.lineTo(0.76471, -0.734)
loop_1 = loop_1.lineTo(0.75461, -0.74594)
loop_1 = loop_1.lineTo(0.74315, -0.75267)
loop_1 = loop_1.lineTo(0.73014, -0.75524)
loop_1 = loop_1.lineTo(0.71406, -0.75622)
loop_1 = loop_1.lineTo(0.69019, -0.76391)
loop_1 = loop_1.lineTo(0.68099, -0.77713)
loop_1 = loop_1.threePointArc((0.67993, -0.78824), (0.67869, -0.79964))
loop_1 = loop_1.lineTo(0.67861, -0.62358)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_47_interval_0.stl')