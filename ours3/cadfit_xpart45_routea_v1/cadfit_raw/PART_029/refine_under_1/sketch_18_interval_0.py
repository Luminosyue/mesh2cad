import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00047, -0.10409, 0.1791), normal=(-0.01537, 0.37157, -0.92828), xDir=(0.0, -0.92839, -0.37162))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.026, 0.24991)
loop_1 = loop_1.threePointArc((0.02338, 0.25538), (0.02081, 0.26116))
loop_1 = loop_1.lineTo(0.01507, 0.32738)
loop_1 = loop_1.lineTo(0.01827, 0.34377)
loop_1 = loop_1.lineTo(0.02056, 0.35436)
loop_1 = loop_1.lineTo(0.03187, 0.36546)
loop_1 = loop_1.threePointArc((0.0312, 0.30325), (0.03057, 0.24352))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_18_interval_0.stl')