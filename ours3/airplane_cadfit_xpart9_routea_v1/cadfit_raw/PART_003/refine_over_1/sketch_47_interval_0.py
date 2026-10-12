import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.12916, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.64658, -0.10325)
loop_1 = loop_1.lineTo(0.71281, -0.07164)
loop_1 = loop_1.lineTo(0.75268, -0.05248)
loop_1 = loop_1.lineTo(0.38283, -0.20909)
loop_1 = loop_1.lineTo(0.43483, -0.19093)
loop_1 = loop_1.threePointArc((0.4589, -0.18273), (0.48159, -0.1745))
loop_1 = loop_1.lineTo(0.52976, -0.15514)
loop_1 = loop_1.threePointArc((0.56743, -0.13909), (0.60313, -0.12329))
loop_1 = loop_1.threePointArc((0.62434, -0.11334), (0.6463, -0.10339))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_47_interval_0.stl')