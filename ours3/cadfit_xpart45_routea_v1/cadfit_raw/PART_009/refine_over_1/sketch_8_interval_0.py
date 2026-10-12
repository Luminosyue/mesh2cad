import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.96418, -0.09752, 0.05583), normal=(-0.99351, 0.11375, 0.00032), xDir=(0.11375, 0.99351, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08996, 0.06891)
loop_1 = loop_1.lineTo(-0.05832, 0.06877)
loop_1 = loop_1.threePointArc((-0.03158, 0.07002), (-0.01026, 0.07155))
loop_1 = loop_1.lineTo(0.01418, 0.07291)
loop_1 = loop_1.lineTo(0.04543, 0.07691)
loop_1 = loop_1.lineTo(0.06652, 0.07807)
loop_1 = loop_1.lineTo(0.09535, 0.08265)
loop_1 = loop_1.lineTo(0.11885, 0.08554)
loop_1 = loop_1.lineTo(0.15945, 0.09434)
loop_1 = loop_1.lineTo(0.17118, 0.09623)
loop_1 = loop_1.lineTo(0.18705, 0.10091)
loop_1 = loop_1.lineTo(0.2012, 0.106)
loop_1 = loop_1.lineTo(0.22351, 0.12014)
loop_1 = loop_1.lineTo(0.27584, 0.15625)
loop_1 = loop_1.lineTo(-0.05457, 0.06983)
loop_1 = loop_1.lineTo(-0.08601, 0.06889)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_8_interval_0.stl')