import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.07937), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10522, 0.98239)
loop_1 = loop_1.lineTo(0.08958, 0.96982)
loop_1 = loop_1.threePointArc((0.0798, 0.95313), (0.06875, 0.93701))
loop_1 = loop_1.threePointArc((0.0651, 0.91979), (0.0605, 0.90279))
loop_1 = loop_1.threePointArc((0.05973, 0.88124), (0.05776, 0.85954))
loop_1 = loop_1.threePointArc((0.05356, 0.81089), (0.0499, 0.76471))
loop_1 = loop_1.threePointArc((0.04895, 0.73157), (0.04699, 0.69769))
loop_1 = loop_1.threePointArc((0.04575, 0.64643), (0.04165, 0.59378))
loop_1 = loop_1.lineTo(0.03784, 0.53727)
loop_1 = loop_1.threePointArc((0.03677, 0.51622), (0.03495, 0.49493))
loop_1 = loop_1.lineTo(0.0299, 0.39324)
loop_1 = loop_1.threePointArc((0.02906, 0.34141), (0.02907, 0.29218))
loop_1 = loop_1.threePointArc((0.0276, 0.2485), (0.02509, 0.20364))
loop_1 = loop_1.lineTo(0.02638, 0.9936)
loop_1 = loop_1.lineTo(0.10475, 0.98285)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_52_interval_0.stl')