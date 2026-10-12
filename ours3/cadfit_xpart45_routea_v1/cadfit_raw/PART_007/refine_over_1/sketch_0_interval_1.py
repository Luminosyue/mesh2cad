import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07313, 0.0, -0.09635), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48304, 0.31563)
loop_1 = loop_1.threePointArc((-0.46181, 0.34468), (-0.43673, 0.37253))
loop_1 = loop_1.threePointArc((-0.37321, 0.43702), (-0.30206, 0.48716))
loop_1 = loop_1.threePointArc((-0.25919, 0.49845), (-0.22157, 0.50444))
loop_1 = loop_1.threePointArc((-0.18279, 0.5149), (-0.14889, 0.52192))
loop_1 = loop_1.threePointArc((-0.12161, 0.52552), (-0.09934, 0.52761))
loop_1 = loop_1.lineTo(-0.06635, 0.52982)
loop_1 = loop_1.lineTo(-0.5428, 0.13636)
loop_1 = loop_1.lineTo(-0.52717, 0.20966)
loop_1 = loop_1.lineTo(-0.50874, 0.24947)
loop_1 = loop_1.threePointArc((-0.49893, 0.27289), (-0.49131, 0.29001))
loop_1 = loop_1.threePointArc((-0.48318, 0.30286), (-0.48291, 0.31001))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_0_interval_1.stl')