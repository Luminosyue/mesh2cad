import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08188, -0.37446, 0.0013), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12374, -0.18231)
loop_1 = loop_1.lineTo(0.10585, -0.17963)
loop_1 = loop_1.lineTo(0.08428, -0.17135)
loop_1 = loop_1.threePointArc((0.07753, -0.15939), (0.07573, -0.15636))
loop_1 = loop_1.threePointArc((0.07564, -0.14812), (0.07555, -0.14081))
loop_1 = loop_1.lineTo(0.08252, -0.12947)
loop_1 = loop_1.lineTo(0.09354, -0.12557)
loop_1 = loop_1.lineTo(0.18153, 0.06729)
loop_1 = loop_1.lineTo(0.18835, 0.08267)
loop_1 = loop_1.lineTo(0.18084, 0.05156)
loop_1 = loop_1.lineTo(0.14492, -0.11079)
loop_1 = loop_1.lineTo(0.12373, -0.1823)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_12_interval_0.stl')