import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14487, -0.28049)
loop_1 = loop_1.lineTo(0.1428, -0.31894)
loop_1 = loop_1.threePointArc((0.14231, -0.32541), (0.14202, -0.33155))
loop_1 = loop_1.lineTo(0.14128, -0.34354)
loop_1 = loop_1.lineTo(0.14469, -0.35765)
loop_1 = loop_1.lineTo(0.15346, -0.37639)
loop_1 = loop_1.lineTo(0.17277, -0.37891)
loop_1 = loop_1.lineTo(0.17703, -0.36125)
loop_1 = loop_1.lineTo(0.17793, -0.32429)
loop_1 = loop_1.threePointArc((0.17515, -0.31268), (0.17495, -0.31094))
loop_1 = loop_1.lineTo(0.16887, -0.27577)
loop_1 = loop_1.lineTo(0.15356, -0.27378)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_36_interval_0.stl')