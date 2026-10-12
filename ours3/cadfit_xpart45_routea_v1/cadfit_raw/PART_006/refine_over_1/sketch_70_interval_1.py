import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.24059, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82454, -0.06472)
loop_1 = loop_1.lineTo(0.81169, -0.04121)
loop_1 = loop_1.lineTo(0.80651, -0.00786)
loop_1 = loop_1.threePointArc((0.8178, 0.00518), (0.82833, 0.01768))
loop_1 = loop_1.lineTo(0.84441, 0.03785)
loop_1 = loop_1.threePointArc((0.86088, 0.07027), (0.87356, 0.09655))
loop_1 = loop_1.threePointArc((0.87768, 0.11708), (0.88144, 0.13656))
loop_1 = loop_1.lineTo(0.88194, -0.16607)
loop_1 = loop_1.lineTo(0.88148, -0.17707)
loop_1 = loop_1.lineTo(0.82464, -0.06492)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_70_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_70_interval_1.stl')