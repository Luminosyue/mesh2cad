import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.56542, 0.32194, 0.7231), normal=(-0.00014, 0.01073, -0.99994), xDir=(0.0, -0.99994, -0.01073))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.69629, 0.31189)
loop_1 = loop_1.lineTo(0.63012, 0.31026)
loop_1 = loop_1.lineTo(0.61139, 0.30536)
loop_1 = loop_1.lineTo(0.59368, 0.29988)
loop_1 = loop_1.lineTo(0.57456, 0.28639)
loop_1 = loop_1.lineTo(0.55948, 0.27652)
loop_1 = loop_1.threePointArc((0.53997, 0.25326), (0.52749, 0.23671))
loop_1 = loop_1.lineTo(0.5188, 0.21752)
loop_1 = loop_1.lineTo(0.50742, 0.20029)
loop_1 = loop_1.lineTo(0.49544, 0.18381)
loop_1 = loop_1.lineTo(0.48437, 0.17461)
loop_1 = loop_1.threePointArc((0.46654, 0.17244), (0.44794, 0.17044))
loop_1 = loop_1.lineTo(0.44604, 0.31322)
loop_1 = loop_1.lineTo(0.69285, 0.31191)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_27_interval_0.stl')