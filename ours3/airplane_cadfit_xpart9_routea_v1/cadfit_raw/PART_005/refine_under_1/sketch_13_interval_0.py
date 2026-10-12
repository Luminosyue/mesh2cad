import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05032, 0.04003, 0.03381), normal=(-0.95754, 0.07027, -0.27962), xDir=(0.07319, 0.99732, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26363, 0.11024)
loop_1 = loop_1.lineTo(0.90171, 0.11223)
loop_1 = loop_1.threePointArc((0.91639, 0.11593), (0.92651, 0.11907))
loop_1 = loop_1.lineTo(0.72298, 0.17249)
loop_1 = loop_1.lineTo(-0.10126, 0.12049)
loop_1 = loop_1.lineTo(-0.2633, 0.11027)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_13_interval_0.stl')