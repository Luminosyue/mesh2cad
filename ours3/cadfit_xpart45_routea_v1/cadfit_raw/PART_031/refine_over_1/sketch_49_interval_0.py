import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04389, -0.71476, 0.20213), normal=(-1e-05, 0.71702, 0.69705), xDir=(1.0, 1e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98404, 0.75562)
loop_1 = loop_1.threePointArc((0.98685, 0.71415), (0.9903, 0.67441))
loop_1 = loop_1.threePointArc((0.99181, 0.55572), (0.98156, 0.43603))
loop_1 = loop_1.threePointArc((0.96221, 0.2819), (0.92658, 0.13341))
loop_1 = loop_1.threePointArc((0.91395, 0.0849), (0.90131, 0.04348))
loop_1 = loop_1.lineTo(0.90094, 0.06085)
loop_1 = loop_1.lineTo(0.88968, 0.02324)
loop_1 = loop_1.threePointArc((0.86372, -0.05845), (0.82791, -0.13596))
loop_1 = loop_1.lineTo(0.80972, -0.13569)
loop_1 = loop_1.lineTo(0.82033, -0.12667)
loop_1 = loop_1.lineTo(0.83693, -0.1)
loop_1 = loop_1.lineTo(0.84806, -0.07832)
loop_1 = loop_1.lineTo(0.86169, -0.05388)
loop_1 = loop_1.lineTo(0.86975, -0.03544)
loop_1 = loop_1.lineTo(0.88705, 0.01557)
loop_1 = loop_1.lineTo(0.94441, 0.46462)
loop_1 = loop_1.lineTo(0.983, 0.74736)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_49_interval_0.stl')