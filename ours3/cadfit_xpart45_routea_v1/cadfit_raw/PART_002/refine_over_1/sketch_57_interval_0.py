import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30885, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21827, 0.76999)
loop_1 = loop_1.threePointArc((-0.22916, 0.74305), (-0.23914, 0.71701))
loop_1 = loop_1.lineTo(-0.24568, 0.67432)
loop_1 = loop_1.lineTo(-0.24816, 0.6373)
loop_1 = loop_1.lineTo(-0.2516, 0.60123)
loop_1 = loop_1.lineTo(-0.25672, 0.56428)
loop_1 = loop_1.lineTo(-0.26463, 0.52776)
loop_1 = loop_1.lineTo(-0.27539, 0.49)
loop_1 = loop_1.threePointArc((-0.27925, 0.47142), (-0.28259, 0.45374))
loop_1 = loop_1.lineTo(-0.28185, 0.77)
loop_1 = loop_1.lineTo(-0.21854, 0.77)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_57_interval_0.stl')