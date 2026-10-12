import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00405, 0.1688, 0.10917), normal=(0.11346, 0.00134, -0.99354), xDir=(0.0, -1.0, -0.00135))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.93387, -0.00255)
loop_1 = loop_1.lineTo(0.93311, -0.01788)
loop_1 = loop_1.lineTo(0.9301, -0.03401)
loop_1 = loop_1.lineTo(0.83769, -0.0142)
loop_1 = loop_1.lineTo(0.8169, -0.01435)
loop_1 = loop_1.lineTo(0.80473, -0.01144)
loop_1 = loop_1.threePointArc((0.79947, -0.00476), (0.79634, -0.0004))
loop_1 = loop_1.lineTo(0.81715, 0.01681)
loop_1 = loop_1.threePointArc((0.82642, 0.01703), (0.83607, 0.01718))
loop_1 = loop_1.lineTo(0.93387, -0.00255)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_7_interval_0.stl')