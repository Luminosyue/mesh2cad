import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.53697, -0.04861, 0.05597), normal=(-0.99351, 0.11375, 0.00032), xDir=(0.11375, 0.99351, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34521, -0.26982)
loop_1 = loop_1.lineTo(-0.34503, -0.31699)
loop_1 = loop_1.lineTo(-0.34225, -0.36445)
loop_1 = loop_1.lineTo(-0.34109, -0.41393)
loop_1 = loop_1.threePointArc((-0.32899, -0.43937), (-0.31806, -0.46142))
loop_1 = loop_1.lineTo(-0.29979, -0.47239)
loop_1 = loop_1.lineTo(-0.34613, -0.47334)
loop_1 = loop_1.lineTo(-0.34593, -0.25429)
loop_1 = loop_1.lineTo(-0.34521, -0.26982)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_21_interval_0.stl')