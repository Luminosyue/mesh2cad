import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64395, 0.12672, 0.41272), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01264, 0.05594)
loop_1 = loop_1.threePointArc((-0.00845, 0.05045), (-0.00416, 0.04468))
loop_1 = loop_1.lineTo(0.02038, 0.01342)
loop_1 = loop_1.lineTo(0.02376, -0.00731)
loop_1 = loop_1.lineTo(-0.01133, -0.00015)
loop_1 = loop_1.lineTo(-0.02121, 0.03231)
loop_1 = loop_1.lineTo(-0.01293, 0.05513)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_9_interval_0.stl')