import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19008, 0.0625, -0.15795), normal=(-0.07595, -0.98701, 0.14157), xDir=(-0.99705, 0.07672, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.17202, -0.28394)
loop_1 = loop_1.lineTo(0.8088, -0.48136)
loop_1 = loop_1.threePointArc((0.84015, -0.4843), (0.86558, -0.48613))
loop_1 = loop_1.lineTo(0.90502, -0.48851)
loop_1 = loop_1.lineTo(0.94161, -0.4894)
loop_1 = loop_1.lineTo(0.97788, -0.49137)
loop_1 = loop_1.lineTo(1.01394, -0.49425)
loop_1 = loop_1.threePointArc((1.03872, -0.49427), (1.05847, -0.49342))
loop_1 = loop_1.lineTo(1.09081, -0.4837)
loop_1 = loop_1.lineTo(1.10241, -0.47447)
loop_1 = loop_1.lineTo(1.11957, -0.45917)
loop_1 = loop_1.threePointArc((1.14328, -0.42929), (1.15708, -0.40793))
loop_1 = loop_1.lineTo(1.16301, -0.39481)
loop_1 = loop_1.lineTo(1.16814, -0.38195)
loop_1 = loop_1.threePointArc((1.17543, -0.35994), (1.18009, -0.34218))
loop_1 = loop_1.lineTo(1.17887, -0.30919)
loop_1 = loop_1.lineTo(1.17316, -0.28815)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_18_interval_0.stl')