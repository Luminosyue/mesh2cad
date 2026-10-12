import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2027, 0.43813, 0.01046), normal=(0.78594, -0.61831, -0.00022), xDir=(-0.61831, -0.78594, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25942, 0.78026)
loop_1 = loop_1.lineTo(0.16249, 0.78026)
loop_1 = loop_1.lineTo(0.17098, 0.76184)
loop_1 = loop_1.lineTo(0.19221, 0.72279)
loop_1 = loop_1.lineTo(0.20042, 0.70632)
loop_1 = loop_1.lineTo(0.21372, 0.68813)
loop_1 = loop_1.threePointArc((0.22202, 0.66913), (0.22909, 0.65354))
loop_1 = loop_1.lineTo(0.24507, 0.6115)
loop_1 = loop_1.threePointArc((0.25127, 0.59333), (0.25672, 0.57707))
loop_1 = loop_1.lineTo(0.25942, 0.77756)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_54_interval_0.stl')