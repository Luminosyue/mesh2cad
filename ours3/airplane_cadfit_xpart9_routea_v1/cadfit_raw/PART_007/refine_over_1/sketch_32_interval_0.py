import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.10742), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0054, 0.08038)
loop_1 = loop_1.lineTo(0.06361, -0.09124)
loop_1 = loop_1.threePointArc((0.06473, -0.07697), (0.06511, -0.07139))
loop_1 = loop_1.threePointArc((0.06561, -0.0628), (0.06637, -0.05401))
loop_1 = loop_1.lineTo(0.07098, -0.02442)
loop_1 = loop_1.lineTo(0.07137, -0.00311)
loop_1 = loop_1.threePointArc((0.07204, 0.00746), (0.07296, 0.01829))
loop_1 = loop_1.lineTo(0.07725, 0.03918)
loop_1 = loop_1.lineTo(0.08004, 0.05886)
loop_1 = loop_1.threePointArc((0.07482, 0.06812), (0.06965, 0.06887))
loop_1 = loop_1.threePointArc((0.06257, 0.07018), (0.05544, 0.07191))
loop_1 = loop_1.lineTo(-0.00526, 0.08037)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_32_interval_0.stl')