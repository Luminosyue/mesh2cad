import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11844, 0.27894, -0.40366), normal=(-0.00126, -0.97705, -0.213), xDir=(-1.0, 0.00129, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0519, 0.28698)
loop_1 = loop_1.lineTo(0.02459, 0.28353)
loop_1 = loop_1.lineTo(0.01286, 0.28178)
loop_1 = loop_1.lineTo(-0.01802, 0.27662)
loop_1 = loop_1.threePointArc((-0.04119, 0.273), (-0.05897, 0.27013))
loop_1 = loop_1.lineTo(-0.08872, 0.26305)
loop_1 = loop_1.lineTo(-0.10948, 0.25696)
loop_1 = loop_1.lineTo(-0.13301, 0.2492)
loop_1 = loop_1.lineTo(-0.14227, 0.28634)
loop_1 = loop_1.lineTo(0.04969, 0.28697)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_28_interval_0.stl')