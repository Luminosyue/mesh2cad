import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58696, -0.06657, 0.5113), normal=(-0.52153, 0.01849, 0.85303), xDir=(0.03543, 0.99937, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01505, -0.15423)
loop_1 = loop_1.lineTo(-0.03149, -0.15876)
loop_1 = loop_1.lineTo(-0.05663, -0.16533)
loop_1 = loop_1.lineTo(-0.08385, -0.17245)
loop_1 = loop_1.lineTo(-0.09651, -0.17575)
loop_1 = loop_1.lineTo(0.15599, 0.10003)
loop_1 = loop_1.lineTo(0.16766, -0.1802)
loop_1 = loop_1.lineTo(0.04071, -0.18081)
loop_1 = loop_1.threePointArc((0.04502, -0.15777), (0.04903, -0.13641))
loop_1 = loop_1.lineTo(0.03205, -0.14144)
loop_1 = loop_1.lineTo(-0.00948, -0.15267)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_9_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_9_interval_1.stl')