import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01014, 0.49016)
loop_1 = loop_1.threePointArc((0.01584, 0.48271), (0.02134, 0.47557))
loop_1 = loop_1.threePointArc((0.02971, 0.47018), (0.03701, 0.46536))
loop_1 = loop_1.threePointArc((0.04548, 0.46197), (0.05288, 0.45882))
loop_1 = loop_1.lineTo(0.06805, 0.45856)
loop_1 = loop_1.lineTo(0.09099, 0.47596)
loop_1 = loop_1.threePointArc((0.09401, 0.4838), (0.09672, 0.49139))
loop_1 = loop_1.threePointArc((0.09656, 0.50062), (0.09637, 0.50803))
loop_1 = loop_1.threePointArc((0.09406, 0.51762), (0.09211, 0.52537))
loop_1 = loop_1.threePointArc((0.08911, 0.53209), (0.08666, 0.53767))
loop_1 = loop_1.lineTo(0.06851, 0.554)
loop_1 = loop_1.lineTo(0.05306, 0.55758)
loop_1 = loop_1.lineTo(0.03527, 0.55089)
loop_1 = loop_1.lineTo(0.02117, 0.5413)
loop_1 = loop_1.threePointArc((0.01391, 0.53007), (0.01032, 0.52436))
loop_1 = loop_1.threePointArc((0.00813, 0.51635), (0.00619, 0.5094))
loop_1 = loop_1.lineTo(0.01014, 0.49016)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_22_interval_0.stl')