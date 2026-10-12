import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.4822, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82769, 0.1425)
loop_1 = loop_1.lineTo(0.82723, -0.15064)
loop_1 = loop_1.threePointArc((0.82439, -0.13054), (0.82135, -0.11151))
loop_1 = loop_1.lineTo(0.77157, -0.06563)
loop_1 = loop_1.lineTo(0.74189, -0.00964)
loop_1 = loop_1.lineTo(0.77293, 0.02731)
loop_1 = loop_1.lineTo(0.786, 0.04497)
loop_1 = loop_1.threePointArc((0.79063, 0.05431), (0.79575, 0.06364))
loop_1 = loop_1.lineTo(0.81346, 0.09741)
loop_1 = loop_1.threePointArc((0.82103, 0.12032), (0.82764, 0.14232))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_76_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_76_interval_1.stl')