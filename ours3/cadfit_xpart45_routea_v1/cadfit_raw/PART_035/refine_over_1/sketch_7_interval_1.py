import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01503, -0.11768, -0.07225), normal=(0.91418, -0.40517, -0.01069), xDir=(-0.40519, -0.91423, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17348, -0.2351)
loop_1 = loop_1.lineTo(0.15394, 0.06869)
loop_1 = loop_1.lineTo(0.15521, 0.01379)
loop_1 = loop_1.threePointArc((0.15568, -0.01969), (0.15694, -0.04906))
loop_1 = loop_1.threePointArc((0.1591, -0.07597), (0.16054, -0.10067))
loop_1 = loop_1.lineTo(0.16078, -0.12048)
loop_1 = loop_1.lineTo(0.16015, -0.13316)
loop_1 = loop_1.lineTo(0.15946, -0.14322)
loop_1 = loop_1.lineTo(0.15672, -0.16016)
loop_1 = loop_1.lineTo(0.15477, -0.18189)
loop_1 = loop_1.lineTo(0.16747, -0.22259)
loop_1 = loop_1.lineTo(0.17345, -0.23498)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_7_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_7_interval_1.stl')