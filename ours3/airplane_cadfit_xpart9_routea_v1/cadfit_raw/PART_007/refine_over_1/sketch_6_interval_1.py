import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02859, 0.22409, -0.12349), normal=(-0.20029, -0.97542, -0.09191), xDir=(-0.97956, 0.20114, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.93203, -0.05329)
loop_1 = loop_1.threePointArc((-0.93311, -0.09159), (-0.93256, -0.12838))
loop_1 = loop_1.lineTo(0.23349, -0.03946)
loop_1 = loop_1.lineTo(-0.92787, -0.04826)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_6_interval_1.stl')