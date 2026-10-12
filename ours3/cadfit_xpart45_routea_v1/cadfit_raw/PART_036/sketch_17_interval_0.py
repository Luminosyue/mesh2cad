import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.21364, -0.05329, -0.24874), normal=(0.00882, -0.29957, 0.95403), xDir=(-0.0, 0.95407, 0.29958))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23688, -0.7368)
loop_1 = loop_1.lineTo(0.24012, -0.74683)
loop_1 = loop_1.lineTo(0.26253, -0.76841)
loop_1 = loop_1.lineTo(0.27998, -0.77165)
loop_1 = loop_1.threePointArc((0.28765, -0.76997), (0.29171, -0.76866))
loop_1 = loop_1.threePointArc((0.30733, -0.75992), (0.31349, -0.75423))
loop_1 = loop_1.lineTo(0.31829, -0.74337)
loop_1 = loop_1.lineTo(0.31798, -0.71938)
loop_1 = loop_1.lineTo(0.30507, -0.70196)
loop_1 = loop_1.lineTo(0.28916, -0.69609)
loop_1 = loop_1.lineTo(0.26351, -0.7004)
loop_1 = loop_1.lineTo(0.24532, -0.71524)
loop_1 = loop_1.lineTo(0.23688, -0.7368)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_17_interval_0.stl')