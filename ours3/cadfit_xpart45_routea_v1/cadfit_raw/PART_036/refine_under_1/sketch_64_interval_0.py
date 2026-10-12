import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.21322, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16401, 0.23496)
loop_1 = loop_1.threePointArc((-0.15508, 0.2338), (-0.1465, 0.23283))
loop_1 = loop_1.threePointArc((-0.13786, 0.22719), (-0.12901, 0.22134))
loop_1 = loop_1.lineTo(-0.12183, 0.20268)
loop_1 = loop_1.lineTo(-0.26142, 0.20295)
loop_1 = loop_1.lineTo(-0.25085, 0.22313)
loop_1 = loop_1.lineTo(-0.23615, 0.23136)
loop_1 = loop_1.threePointArc((-0.22817, 0.23325), (-0.22269, 0.23377))
loop_1 = loop_1.threePointArc((-0.20829, 0.23456), (-0.20104, 0.23443))
loop_1 = loop_1.threePointArc((-0.19098, 0.23462), (-0.18144, 0.23498))
loop_1 = loop_1.threePointArc((-0.17255, 0.23494), (-0.16412, 0.23496))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_64_interval_0.stl')