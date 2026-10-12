import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.17511, -0.08505, 0.53116), normal=(0.06723, 0.02988, 0.99729), xDir=(0.0, 0.99955, -0.02995))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17973, 0.31788)
loop_1 = loop_1.lineTo(0.17952, 0.41877)
loop_1 = loop_1.lineTo(-0.10139, 0.4054)
loop_1 = loop_1.threePointArc((-0.09008, 0.39901), (-0.08135, 0.39397))
loop_1 = loop_1.lineTo(-0.04985, 0.38318)
loop_1 = loop_1.threePointArc((-0.03567, 0.37927), (-0.02461, 0.37655))
loop_1 = loop_1.lineTo(-0.01395, 0.37411)
loop_1 = loop_1.lineTo(0.0018, 0.3693)
loop_1 = loop_1.lineTo(0.01741, 0.3661)
loop_1 = loop_1.threePointArc((0.04436, 0.35859), (0.06704, 0.35275))
loop_1 = loop_1.lineTo(0.08347, 0.34833)
loop_1 = loop_1.threePointArc((0.11271, 0.34017), (0.13781, 0.33373))
loop_1 = loop_1.threePointArc((0.14997, 0.33148), (0.16108, 0.32923))
loop_1 = loop_1.lineTo(0.17973, 0.31788)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_7_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_7_interval_1.stl')