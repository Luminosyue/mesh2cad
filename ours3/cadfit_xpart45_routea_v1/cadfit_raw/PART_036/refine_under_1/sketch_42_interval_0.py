import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47724, 0.0711, 0.03495), normal=(0.01988, -0.75052, -0.66054), xDir=(-0.99965, -0.02649, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.75059, 0.01276)
loop_1 = loop_1.lineTo(0.71229, 0.013)
loop_1 = loop_1.lineTo(0.71213, -0.01616)
loop_1 = loop_1.threePointArc((0.71233, -0.02191), (0.7125, -0.027))
loop_1 = loop_1.lineTo(0.75805, -0.02729)
loop_1 = loop_1.lineTo(0.75594, -0.00958)
loop_1 = loop_1.lineTo(0.75059, 0.01276)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_42_interval_0.stl')