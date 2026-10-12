import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87196, -0.01108, 0.06777), normal=(-0.99256, 0.12159, -0.00648), xDir=(0.12159, 0.99258, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32068, -0.25961)
loop_1 = loop_1.lineTo(0.32292, -0.38763)
loop_1 = loop_1.lineTo(0.26395, -0.38763)
loop_1 = loop_1.lineTo(0.29237, -0.37862)
loop_1 = loop_1.lineTo(0.29816, -0.3686)
loop_1 = loop_1.lineTo(0.30827, -0.35286)
loop_1 = loop_1.threePointArc((0.31477, -0.33983), (0.32017, -0.32883))
loop_1 = loop_1.lineTo(0.31903, -0.28966)
loop_1 = loop_1.threePointArc((0.31975, -0.27503), (0.32059, -0.26138))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_2_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_2_interval_2.stl')