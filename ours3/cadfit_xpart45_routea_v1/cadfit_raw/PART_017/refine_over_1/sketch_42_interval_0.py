import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01208, 0.37588, -0.42116), normal=(-0.0, 0.98993, -0.14155), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34989, 0.04474)
loop_1 = loop_1.lineTo(0.36223, 0.03129)
loop_1 = loop_1.lineTo(0.37849, 0.01173)
loop_1 = loop_1.lineTo(0.39208, -0.00696)
loop_1 = loop_1.lineTo(0.39208, 0.16295)
loop_1 = loop_1.lineTo(0.11746, 0.16295)
loop_1 = loop_1.lineTo(0.14666, 0.15586)
loop_1 = loop_1.lineTo(0.18529, 0.14797)
loop_1 = loop_1.lineTo(0.22408, 0.13379)
loop_1 = loop_1.lineTo(0.26854, 0.10747)
loop_1 = loop_1.threePointArc((0.28665, 0.09605), (0.30121, 0.08696))
loop_1 = loop_1.lineTo(0.32339, 0.07032)
loop_1 = loop_1.lineTo(0.33985, 0.05568)
loop_1 = loop_1.lineTo(0.34989, 0.04474)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_42_interval_0.stl')