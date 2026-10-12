import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72191, -0.57479, 0.45998), normal=(0.71211, 0.70206, -0.00011), xDir=(0.70206, -0.71211, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17518, 0.43842)
loop_1 = loop_1.threePointArc((0.17535, 0.47661), (0.17483, 0.51326))
loop_1 = loop_1.lineTo(0.17489, 0.52649)
loop_1 = loop_1.lineTo(0.17502, 0.54292)
loop_1 = loop_1.lineTo(0.1747, 0.56674)
loop_1 = loop_1.lineTo(0.17474, 0.59253)
loop_1 = loop_1.lineTo(0.17415, 0.6217)
loop_1 = loop_1.threePointArc((0.17468, 0.63609), (0.17506, 0.64732))
loop_1 = loop_1.threePointArc((0.17618, 0.66114), (0.17728, 0.67293))
loop_1 = loop_1.lineTo(0.18389, 0.68331)
loop_1 = loop_1.lineTo(0.17552, 0.46555)
loop_1 = loop_1.lineTo(0.17523, 0.44089)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_16_interval_0.stl')