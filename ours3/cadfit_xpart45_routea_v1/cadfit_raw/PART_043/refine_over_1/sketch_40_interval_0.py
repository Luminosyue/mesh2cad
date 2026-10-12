import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57924, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40774, -0.01482)
loop_1 = loop_1.lineTo(-0.4075, -0.11)
loop_1 = loop_1.lineTo(-0.30509, -0.10976)
loop_1 = loop_1.threePointArc((-0.316, -0.0945), (-0.32645, -0.08831))
loop_1 = loop_1.threePointArc((-0.33273, -0.08446), (-0.33899, -0.08027))
loop_1 = loop_1.lineTo(-0.35523, -0.06949)
loop_1 = loop_1.lineTo(-0.36552, -0.06207)
loop_1 = loop_1.lineTo(-0.37847, -0.04676)
loop_1 = loop_1.threePointArc((-0.38546, -0.0388), (-0.38812, -0.03461))
loop_1 = loop_1.threePointArc((-0.39642, -0.02048), (-0.39885, -0.01649))
loop_1 = loop_1.lineTo(-0.40774, -0.0007)
loop_1 = loop_1.lineTo(-0.40774, -0.01469)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_40_interval_0.stl')