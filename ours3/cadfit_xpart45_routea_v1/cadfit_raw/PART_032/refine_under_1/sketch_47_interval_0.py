import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.52, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.76151, -0.18888)
loop_1 = loop_1.lineTo(0.78778, -0.18967)
loop_1 = loop_1.lineTo(0.77713, -0.19579)
loop_1 = loop_1.lineTo(0.73554, -0.21298)
loop_1 = loop_1.lineTo(0.58178, -0.21444)
loop_1 = loop_1.lineTo(0.38657, -0.21419)
loop_1 = loop_1.lineTo(0.13364, -0.21449)
loop_1 = loop_1.threePointArc((0.05247, -0.21515), (-0.03096, -0.21453))
loop_1 = loop_1.lineTo(-0.14982, -0.21589)
loop_1 = loop_1.lineTo(-0.37335, -0.21495)
loop_1 = loop_1.lineTo(-0.59903, -0.21444)
loop_1 = loop_1.threePointArc((-0.66688, -0.21326), (-0.73638, -0.21065))
loop_1 = loop_1.lineTo(-0.7668, -0.20991)
loop_1 = loop_1.lineTo(-0.81147, -0.20161)
loop_1 = loop_1.lineTo(-0.82698, -0.18896)
loop_1 = loop_1.lineTo(0.76042, -0.18888)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_47_interval_0.stl')