import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.4291), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28504, -0.63223)
loop_1 = loop_1.lineTo(-0.10835, -0.6317)
loop_1 = loop_1.lineTo(-0.10873, -0.57629)
loop_1 = loop_1.lineTo(-0.15078, -0.57682)
loop_1 = loop_1.threePointArc((-0.1682, -0.57922), (-0.18623, -0.5814))
loop_1 = loop_1.threePointArc((-0.20009, -0.58896), (-0.21315, -0.59632))
loop_1 = loop_1.threePointArc((-0.22486, -0.6029), (-0.23578, -0.60951))
loop_1 = loop_1.lineTo(-0.25348, -0.61995)
loop_1 = loop_1.lineTo(-0.28491, -0.63218)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_46_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_46_interval_1.stl')