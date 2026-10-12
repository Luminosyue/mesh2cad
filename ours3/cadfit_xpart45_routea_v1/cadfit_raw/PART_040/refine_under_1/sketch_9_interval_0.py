import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31146, -0.58308)
loop_1 = loop_1.threePointArc((-0.30404, -0.58346), (-0.29633, -0.58407))
loop_1 = loop_1.threePointArc((-0.28709, -0.58198), (-0.27969, -0.58027))
loop_1 = loop_1.threePointArc((-0.27323, -0.57637), (-0.26798, -0.57336))
loop_1 = loop_1.threePointArc((-0.25855, -0.56216), (-0.25512, -0.55677))
loop_1 = loop_1.threePointArc((-0.25283, -0.54755), (-0.2511, -0.54013))
loop_1 = loop_1.threePointArc((-0.25184, -0.53121), (-0.25235, -0.5235))
loop_1 = loop_1.lineTo(-0.26474, -0.50365)
loop_1 = loop_1.threePointArc((-0.27246, -0.49933), (-0.27993, -0.49526))
loop_1 = loop_1.threePointArc((-0.28847, -0.49326), (-0.2957, -0.4915))
loop_1 = loop_1.lineTo(-0.31146, -0.58308)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_9_interval_0.stl')