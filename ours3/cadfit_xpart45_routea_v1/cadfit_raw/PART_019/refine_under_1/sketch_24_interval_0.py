import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.79359, -0.104, -0.5651), normal=(-0.85276, 0.00011, 0.52231), xDir=(0.00013, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89366, 0.21776)
loop_1 = loop_1.lineTo(0.8931, -0.18725)
loop_1 = loop_1.lineTo(0.89944, -0.1542)
loop_1 = loop_1.lineTo(0.90071, -0.14032)
loop_1 = loop_1.lineTo(0.90177, -0.07265)
loop_1 = loop_1.lineTo(0.90975, -0.02106)
loop_1 = loop_1.lineTo(0.90909, -0.00032)
loop_1 = loop_1.lineTo(0.91225, 0.03247)
loop_1 = loop_1.lineTo(0.90873, 0.07202)
loop_1 = loop_1.lineTo(0.9086, 0.08779)
loop_1 = loop_1.lineTo(0.91039, 0.09853)
loop_1 = loop_1.lineTo(0.90586, 0.14436)
loop_1 = loop_1.lineTo(0.8942, 0.2167)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_24_interval_0.stl')