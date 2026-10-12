import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05675, -0.26337, 0.0049), normal=(-0.26995, -0.52965, -0.80411), xDir=(-0.89096, 0.45409, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0753, 0.12538)
loop_1 = loop_1.threePointArc((0.07297, 0.11766), (0.07041, 0.10966))
loop_1 = loop_1.threePointArc((0.05582, 0.10786), (0.04201, 0.10608))
loop_1 = loop_1.lineTo(-0.01434, 0.10072)
loop_1 = loop_1.threePointArc((-0.04853, 0.09739), (-0.082, 0.09482))
loop_1 = loop_1.threePointArc((-0.10686, 0.09236), (-0.1286, 0.09001))
loop_1 = loop_1.lineTo(0.07437, 0.12954)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_18_interval_0.stl')