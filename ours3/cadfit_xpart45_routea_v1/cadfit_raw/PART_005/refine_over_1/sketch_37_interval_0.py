import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05512, -0.49, 0.11488), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94025, 0.6347)
loop_1 = loop_1.lineTo(0.91283, 0.70732)
loop_1 = loop_1.lineTo(0.85015, 0.70683)
loop_1 = loop_1.lineTo(0.86305, 0.70534)
loop_1 = loop_1.lineTo(0.89544, 0.69334)
loop_1 = loop_1.lineTo(0.9139, 0.68129)
loop_1 = loop_1.lineTo(0.9242, 0.66185)
loop_1 = loop_1.lineTo(0.94265, 0.62945)
loop_1 = loop_1.threePointArc((0.94667, 0.60468), (0.95052, 0.58281))
loop_1 = loop_1.lineTo(0.95115, 0.6347)
loop_1 = loop_1.lineTo(0.94025, 0.6347)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.92)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_37_interval_0.stl')