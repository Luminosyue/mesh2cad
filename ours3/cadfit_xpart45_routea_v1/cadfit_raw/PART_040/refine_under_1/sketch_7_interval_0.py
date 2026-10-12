import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.79853, 0.33457, 0.01139), normal=(0.38034, -0.92485, -2e-05), xDir=(-0.92485, -0.38034, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17058, 0.14246)
loop_1 = loop_1.threePointArc((0.16903, 0.1276), (0.16696, 0.11218))
loop_1 = loop_1.lineTo(0.17064, 0.09166)
loop_1 = loop_1.lineTo(0.16978, 0.07467)
loop_1 = loop_1.lineTo(0.17007, 0.06229)
loop_1 = loop_1.threePointArc((0.16975, 0.04377), (0.16906, 0.02901))
loop_1 = loop_1.lineTo(0.16889, 0.00759)
loop_1 = loop_1.lineTo(0.16931, -0.0209)
loop_1 = loop_1.lineTo(0.16991, -0.03754)
loop_1 = loop_1.lineTo(0.16985, -0.05428)
loop_1 = loop_1.lineTo(0.16754, -0.06577)
loop_1 = loop_1.lineTo(0.16527, -0.08721)
loop_1 = loop_1.lineTo(0.16533, -0.09907)
loop_1 = loop_1.lineTo(0.1642, -0.10977)
loop_1 = loop_1.lineTo(0.1642, 0.17915)
loop_1 = loop_1.lineTo(0.17058, 0.14246)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_7_interval_0.stl')