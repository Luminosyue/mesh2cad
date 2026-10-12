import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.13121, -0.13328)
loop_1 = loop_1.lineTo(-0.19557, -0.13857)
loop_1 = loop_1.lineTo(-0.18262, -0.16431)
loop_1 = loop_1.lineTo(-0.16817, -0.17063)
loop_1 = loop_1.threePointArc((-0.16088, -0.17085), (-0.15387, -0.17096))
loop_1 = loop_1.lineTo(-0.13121, -0.13328)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_53_interval_0.stl')