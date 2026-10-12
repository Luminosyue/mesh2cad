import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00566, -0.0553, 0.94341), normal=(-0.00316, 0.00117, -0.99999), xDir=(0.0, -1.0, -0.00117))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.72668, -0.29284)
loop_1 = loop_1.lineTo(0.72616, 0.31226)
loop_1 = loop_1.threePointArc((0.73503, 0.2766), (0.74267, 0.2461))
loop_1 = loop_1.lineTo(0.75227, 0.19244)
loop_1 = loop_1.lineTo(0.75955, 0.12319)
loop_1 = loop_1.threePointArc((0.76086, -0.00067), (0.75975, -0.12354))
loop_1 = loop_1.lineTo(0.75321, -0.18542)
loop_1 = loop_1.lineTo(0.74153, -0.2469)
loop_1 = loop_1.lineTo(0.7285, -0.2872)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_35_interval_0.stl')