import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.21903, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.87163, 0.14315)
loop_1 = loop_1.lineTo(0.87021, -0.53018)
loop_1 = loop_1.lineTo(0.85508, -0.52978)
loop_1 = loop_1.lineTo(0.86482, -0.46603)
loop_1 = loop_1.threePointArc((0.86384, -0.41244), (0.8642, -0.3571))
loop_1 = loop_1.threePointArc((0.86372, -0.30524), (0.86256, -0.25592))
loop_1 = loop_1.threePointArc((0.86362, -0.20663), (0.86497, -0.15581))
loop_1 = loop_1.lineTo(0.85907, -0.10665)
loop_1 = loop_1.lineTo(0.84048, -0.08218)
loop_1 = loop_1.threePointArc((0.83147, -0.07551), (0.82255, -0.07034))
loop_1 = loop_1.lineTo(0.79837, -0.05515)
loop_1 = loop_1.lineTo(0.7882, -0.03031)
loop_1 = loop_1.lineTo(0.77788, -0.00376)
loop_1 = loop_1.lineTo(0.79013, 0.00269)
loop_1 = loop_1.lineTo(0.83958, 0.04895)
loop_1 = loop_1.lineTo(0.86349, 0.10143)
loop_1 = loop_1.lineTo(0.87154, 0.14268)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_61_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_61_interval_1.stl')