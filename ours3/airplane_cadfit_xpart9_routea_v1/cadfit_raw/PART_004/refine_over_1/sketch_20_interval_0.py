import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.54285, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94, -0.01895)
loop_1 = loop_1.lineTo(0.93961, -0.05526)
loop_1 = loop_1.lineTo(0.46327, -0.05493)
loop_1 = loop_1.threePointArc((0.49275, -0.05484), (0.52308, -0.0552))
loop_1 = loop_1.threePointArc((0.53212, -0.05456), (0.54042, -0.05385))
loop_1 = loop_1.lineTo(0.56368, -0.05025)
loop_1 = loop_1.threePointArc((0.57873, -0.04843), (0.59413, -0.04769))
loop_1 = loop_1.threePointArc((0.6207, -0.04628), (0.64803, -0.04566))
loop_1 = loop_1.threePointArc((0.69191, -0.04397), (0.73367, -0.04183))
loop_1 = loop_1.lineTo(0.79939, -0.03918)
loop_1 = loop_1.threePointArc((0.83609, -0.03743), (0.87398, -0.03629))
loop_1 = loop_1.threePointArc((0.89372, -0.03561), (0.9123, -0.03433))
loop_1 = loop_1.threePointArc((0.91801, -0.03289), (0.92302, -0.03115))
loop_1 = loop_1.lineTo(0.93765, -0.02283)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_20_interval_0.stl')