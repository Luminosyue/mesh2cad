import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.13, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.76797, -0.15904)
loop_1 = loop_1.lineTo(0.75257, -0.16005)
loop_1 = loop_1.threePointArc((0.74419, -0.16136), (0.73555, -0.16259))
loop_1 = loop_1.lineTo(0.72554, -0.16396)
loop_1 = loop_1.lineTo(0.73754, -0.16742)
loop_1 = loop_1.threePointArc((0.74904, -0.17185), (0.7542, -0.17373))
loop_1 = loop_1.threePointArc((0.76092, -0.17564), (0.76733, -0.17725))
loop_1 = loop_1.lineTo(0.78928, -0.18152)
loop_1 = loop_1.threePointArc((0.80245, -0.1839), (0.80923, -0.18523))
loop_1 = loop_1.threePointArc((0.82734, -0.18716), (0.83563, -0.18793))
loop_1 = loop_1.threePointArc((0.84648, -0.18797), (0.85224, -0.18798))
loop_1 = loop_1.threePointArc((0.85974, -0.18404), (0.86676, -0.18022))
loop_1 = loop_1.lineTo(0.84523, -0.17665)
loop_1 = loop_1.lineTo(0.83289, -0.17725)
loop_1 = loop_1.lineTo(0.81931, -0.17469)
loop_1 = loop_1.lineTo(0.78167, -0.16079)
loop_1 = loop_1.lineTo(0.76807, -0.15906)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_54_interval_0.stl')