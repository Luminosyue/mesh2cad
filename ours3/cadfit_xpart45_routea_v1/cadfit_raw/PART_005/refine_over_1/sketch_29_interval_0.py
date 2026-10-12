import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.86918, 0.27731, -0.00609), normal=(-0.95581, 0.29398, 5e-05), xDir=(0.29398, 0.95581, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24794, 0.51373)
loop_1 = loop_1.lineTo(0.28979, 0.51373)
loop_1 = loop_1.lineTo(0.28983, 0.27488)
loop_1 = loop_1.lineTo(0.28659, 0.30116)
loop_1 = loop_1.threePointArc((0.2854, 0.32787), (0.28452, 0.35299))
loop_1 = loop_1.lineTo(0.28585, 0.37868)
loop_1 = loop_1.lineTo(0.28656, 0.40483)
loop_1 = loop_1.threePointArc((0.28451, 0.43152), (0.28289, 0.45666))
loop_1 = loop_1.threePointArc((0.27084, 0.48218), (0.26004, 0.50422))
loop_1 = loop_1.lineTo(0.24794, 0.51373)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_29_interval_0.stl')