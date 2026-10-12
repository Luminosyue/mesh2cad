import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.57, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.74186, 0.19341)
loop_1 = loop_1.threePointArc((0.74472, 0.16367), (0.74601, 0.13862))
loop_1 = loop_1.threePointArc((0.74586, 0.11288), (0.74618, 0.08839))
loop_1 = loop_1.threePointArc((0.74558, 0.04174), (0.74442, -0.0066))
loop_1 = loop_1.lineTo(0.74552, -0.05497)
loop_1 = loop_1.threePointArc((0.74535, -0.10129), (0.746, -0.14553))
loop_1 = loop_1.lineTo(0.74189, -0.15775)
loop_1 = loop_1.lineTo(0.74189, 0.19319)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_63_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_63_interval_0.stl')