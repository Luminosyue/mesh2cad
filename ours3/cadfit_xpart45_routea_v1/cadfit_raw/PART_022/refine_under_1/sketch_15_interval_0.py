import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08699, 0.88378, 0.01065), normal=(0.00017, -1.0, -0.00093), xDir=(-1.0, -0.00017, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.43941, 0.18885)
loop_1 = loop_1.lineTo(-0.24267, 0.18398)
loop_1 = loop_1.lineTo(-0.24199, 0.17249)
loop_1 = loop_1.threePointArc((-0.23388, 0.04915), (-0.22524, -0.06919))
loop_1 = loop_1.lineTo(-0.22465, -0.08002)
loop_1 = loop_1.lineTo(-0.21267, -0.2494)
loop_1 = loop_1.lineTo(0.4197, -0.2494)
loop_1 = loop_1.lineTo(0.43593, 0.10004)
loop_1 = loop_1.lineTo(0.43897, 0.17775)
loop_1 = loop_1.lineTo(0.43941, 0.18885)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_15_interval_0.stl')