import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.17674), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34702, 0.9565)
loop_1 = loop_1.threePointArc((0.34771, 0.95015), (0.34825, 0.94352))
loop_1 = loop_1.threePointArc((0.34888, 0.93464), (0.34898, 0.93341))
loop_1 = loop_1.lineTo(0.35217, 0.91673)
loop_1 = loop_1.lineTo(0.36898, 0.89742)
loop_1 = loop_1.threePointArc((0.38214, 0.89178), (0.3872, 0.89127))
loop_1 = loop_1.lineTo(0.41601, 0.89651)
loop_1 = loop_1.lineTo(0.43543, 0.91331)
loop_1 = loop_1.lineTo(0.4394, 0.93467)
loop_1 = loop_1.threePointArc((0.43802, 0.94228), (0.43663, 0.94692))
loop_1 = loop_1.threePointArc((0.43512, 0.95225), (0.43345, 0.9572))
loop_1 = loop_1.lineTo(0.42218, 0.97644)
loop_1 = loop_1.lineTo(0.39736, 0.99587)
loop_1 = loop_1.lineTo(0.379, 0.9982)
loop_1 = loop_1.lineTo(0.35751, 0.9878)
loop_1 = loop_1.lineTo(0.34969, 0.97582)
loop_1 = loop_1.lineTo(0.34703, 0.95661)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_11_interval_0.stl')