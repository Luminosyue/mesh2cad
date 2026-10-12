import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.6147, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.67861, 0.80644)
loop_1 = loop_1.lineTo(0.68932, 0.797)
loop_1 = loop_1.lineTo(0.72448, 0.79018)
loop_1 = loop_1.threePointArc((0.73278, 0.7835), (0.73495, 0.78273))
loop_1 = loop_1.lineTo(0.74792, 0.7775)
loop_1 = loop_1.lineTo(0.76837, 0.75619)
loop_1 = loop_1.threePointArc((0.77042, 0.74431), (0.77214, 0.73205))
loop_1 = loop_1.lineTo(0.76535, 0.71953)
loop_1 = loop_1.lineTo(0.75874, 0.70544)
loop_1 = loop_1.lineTo(0.74496, 0.69237)
loop_1 = loop_1.lineTo(0.7289, 0.68706)
loop_1 = loop_1.lineTo(0.7127, 0.67922)
loop_1 = loop_1.lineTo(0.69535, 0.67017)
loop_1 = loop_1.lineTo(0.68515, 0.66273)
loop_1 = loop_1.lineTo(0.68482, 0.64796)
loop_1 = loop_1.lineTo(0.67861, 0.62453)
loop_1 = loop_1.lineTo(0.67861, 0.80628)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_46_interval_0.stl')