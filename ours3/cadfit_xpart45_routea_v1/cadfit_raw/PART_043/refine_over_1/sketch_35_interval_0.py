import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58659, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06019, -0.34041)
loop_1 = loop_1.lineTo(0.50605, -0.45702)
loop_1 = loop_1.lineTo(0.50605, -0.47175)
loop_1 = loop_1.lineTo(0.47425, -0.4736)
loop_1 = loop_1.threePointArc((0.43544, -0.47421), (0.39543, -0.4732))
loop_1 = loop_1.threePointArc((0.36746, -0.47324), (0.33878, -0.47226))
loop_1 = loop_1.threePointArc((0.32644, -0.47137), (0.31405, -0.46992))
loop_1 = loop_1.threePointArc((0.29317, -0.46792), (0.27197, -0.46483))
loop_1 = loop_1.lineTo(0.24633, -0.46224)
loop_1 = loop_1.threePointArc((0.18959, -0.45308), (0.13132, -0.44129))
loop_1 = loop_1.lineTo(0.09301, -0.43116)
loop_1 = loop_1.threePointArc((0.0678, -0.42213), (0.04208, -0.41245))
loop_1 = loop_1.lineTo(0.01509, -0.40044)
loop_1 = loop_1.lineTo(-0.00916, -0.38793)
loop_1 = loop_1.lineTo(-0.03845, -0.3696)
loop_1 = loop_1.lineTo(-0.05997, -0.35534)
loop_1 = loop_1.lineTo(-0.06018, -0.34081)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_35_interval_0.stl')