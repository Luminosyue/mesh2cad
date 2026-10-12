import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.81917, -0.104, -0.58077), normal=(-0.85276, 0.00011, 0.52231), xDir=(0.00013, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.62365, 0.26753)
loop_1 = loop_1.lineTo(0.82635, 0.26555)
loop_1 = loop_1.lineTo(0.82638, -0.21671)
loop_1 = loop_1.lineTo(0.82362, -0.25076)
loop_1 = loop_1.lineTo(0.82639, -0.28812)
loop_1 = loop_1.lineTo(-0.62361, -0.28613)
loop_1 = loop_1.lineTo(-0.62365, 0.24765)
loop_1 = loop_1.lineTo(-0.62365, 0.26753)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_38_interval_0.stl')