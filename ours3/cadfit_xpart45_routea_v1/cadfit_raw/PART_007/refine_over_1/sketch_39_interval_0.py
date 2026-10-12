import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33423, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99, -0.4434)
loop_1 = loop_1.lineTo(0.98932, -0.54165)
loop_1 = loop_1.lineTo(0.1377, -0.54098)
loop_1 = loop_1.lineTo(0.22206, -0.54111)
loop_1 = loop_1.threePointArc((0.25511, -0.54086), (0.28881, -0.54168))
loop_1 = loop_1.threePointArc((0.32712, -0.54012), (0.36632, -0.54065))
loop_1 = loop_1.threePointArc((0.41149, -0.54053), (0.4542, -0.53992))
loop_1 = loop_1.threePointArc((0.48578, -0.5381), (0.518, -0.53871))
loop_1 = loop_1.threePointArc((0.61465, -0.53718), (0.71461, -0.5373))
loop_1 = loop_1.lineTo(0.77538, -0.53735)
loop_1 = loop_1.lineTo(0.86883, -0.53999)
loop_1 = loop_1.threePointArc((0.88729, -0.5403), (0.90423, -0.53829))
loop_1 = loop_1.threePointArc((0.91595, -0.53727), (0.92645, -0.53567))
loop_1 = loop_1.lineTo(0.96662, -0.50517)
loop_1 = loop_1.lineTo(0.98428, -0.46359)
loop_1 = loop_1.threePointArc((0.98557, -0.453), (0.98613, -0.4434))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_39_interval_0.stl')