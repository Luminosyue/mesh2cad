import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02464, -0.94184, 0.09644), normal=(-7e-05, 0.99999, -0.00529), xDir=(1.0, 7e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26988, -0.17924)
loop_1 = loop_1.lineTo(0.34267, -0.18385)
loop_1 = loop_1.lineTo(0.31569, -0.19195)
loop_1 = loop_1.lineTo(0.26641, -0.2086)
loop_1 = loop_1.lineTo(0.21712, -0.20998)
loop_1 = loop_1.lineTo(0.16783, -0.20723)
loop_1 = loop_1.lineTo(0.11269, -0.21431)
loop_1 = loop_1.threePointArc((0.08818, -0.21829), (0.06868, -0.22098))
loop_1 = loop_1.lineTo(0.01937, -0.22556)
loop_1 = loop_1.lineTo(-0.0299, -0.22424)
loop_1 = loop_1.lineTo(-0.05551, -0.21903)
loop_1 = loop_1.lineTo(-0.0786, -0.21247)
loop_1 = loop_1.lineTo(-0.12789, -0.20385)
loop_1 = loop_1.lineTo(-0.17717, -0.21298)
loop_1 = loop_1.lineTo(-0.22646, -0.20804)
loop_1 = loop_1.lineTo(-0.26501, -0.18247)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_20_interval_0.stl')