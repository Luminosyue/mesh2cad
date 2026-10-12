import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05675, -0.26337, 0.0049), normal=(-0.26995, -0.52965, -0.80411), xDir=(-0.89096, 0.45409, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99654, 0.18705)
loop_1 = loop_1.lineTo(0.74213, 0.18705)
loop_1 = loop_1.threePointArc((0.75665, 0.17848), (0.76952, 0.17058))
loop_1 = loop_1.lineTo(0.82564, 0.17576)
loop_1 = loop_1.threePointArc((0.8369, 0.17712), (0.84526, 0.17818))
loop_1 = loop_1.threePointArc((0.87135, 0.18016), (0.89383, 0.18228))
loop_1 = loop_1.lineTo(0.92015, 0.18371)
loop_1 = loop_1.lineTo(0.94194, 0.18521)
loop_1 = loop_1.lineTo(0.96536, 0.18473)
loop_1 = loop_1.lineTo(0.99637, 0.18609)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_interval_0.stl')