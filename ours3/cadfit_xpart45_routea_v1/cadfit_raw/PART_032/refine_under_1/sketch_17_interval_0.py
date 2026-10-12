import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04954, -0.90234, -0.11874), normal=(0.01187, 0.99992, -0.00524), xDir=(0.99993, -0.01187, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35579, -0.31278)
loop_1 = loop_1.lineTo(0.34219, -0.34479)
loop_1 = loop_1.threePointArc((0.33387, -0.37048), (0.32703, -0.39167))
loop_1 = loop_1.lineTo(0.31406, -0.41349)
loop_1 = loop_1.lineTo(0.29338, -0.43647)
loop_1 = loop_1.lineTo(0.26975, -0.45117)
loop_1 = loop_1.lineTo(0.23191, -0.46121)
loop_1 = loop_1.lineTo(0.21902, -0.46255)
loop_1 = loop_1.lineTo(0.18445, -0.46199)
loop_1 = loop_1.lineTo(0.17209, -0.46117)
loop_1 = loop_1.lineTo(0.13705, -0.45245)
loop_1 = loop_1.lineTo(0.11967, -0.44541)
loop_1 = loop_1.lineTo(0.08365, -0.39844)
loop_1 = loop_1.lineTo(0.06393, -0.33709)
loop_1 = loop_1.lineTo(0.05384, -0.30835)
loop_1 = loop_1.lineTo(0.35358, -0.30834)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_17_interval_0.stl')