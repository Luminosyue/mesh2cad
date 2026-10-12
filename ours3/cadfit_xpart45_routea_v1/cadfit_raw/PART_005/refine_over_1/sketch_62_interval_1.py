import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.46903, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.8356, 0.12547)
loop_1 = loop_1.lineTo(-0.82938, 0.09899)
loop_1 = loop_1.threePointArc((-0.81825, 0.07233), (-0.80729, 0.04704))
loop_1 = loop_1.lineTo(-0.77458, -0.00426)
loop_1 = loop_1.threePointArc((-0.77374, -0.02335), (-0.77318, -0.04308))
loop_1 = loop_1.lineTo(-0.77285, -0.05569)
loop_1 = loop_1.lineTo(-0.81752, -0.081)
loop_1 = loop_1.lineTo(-0.8356, -0.10031)
loop_1 = loop_1.lineTo(-0.8356, 0.1253)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_62_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_62_interval_1.stl')