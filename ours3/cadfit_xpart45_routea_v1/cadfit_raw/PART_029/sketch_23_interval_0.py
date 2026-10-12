import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.14094, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96704, -0.10447)
loop_1 = loop_1.lineTo(0.95576, -0.10463)
loop_1 = loop_1.lineTo(0.94213, -0.11206)
loop_1 = loop_1.lineTo(0.92914, -0.12623)
loop_1 = loop_1.lineTo(0.9246, -0.14477)
loop_1 = loop_1.lineTo(0.93259, -0.15915)
loop_1 = loop_1.lineTo(0.94272, -0.16381)
loop_1 = loop_1.lineTo(0.95288, -0.16922)
loop_1 = loop_1.threePointArc((0.95989, -0.16977), (0.9671, -0.17044))
loop_1 = loop_1.lineTo(0.98152, -0.16671)
loop_1 = loop_1.lineTo(0.99476, -0.14735)
loop_1 = loop_1.lineTo(0.99071, -0.12548)
loop_1 = loop_1.lineTo(0.98147, -0.11193)
loop_1 = loop_1.lineTo(0.97042, -0.10598)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/sketch_23_interval_0.stl')