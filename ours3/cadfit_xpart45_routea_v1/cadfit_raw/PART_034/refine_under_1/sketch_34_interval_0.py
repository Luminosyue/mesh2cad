import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87816, -0.01823, 0.01004), normal=(0.99411, -0.10841, -0.0005), xDir=(-0.10841, -0.99411, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.19438, -0.26546)
loop_1 = loop_1.lineTo(0.17654, -0.26895)
loop_1 = loop_1.lineTo(0.16387, -0.2749)
loop_1 = loop_1.lineTo(0.15271, -0.27761)
loop_1 = loop_1.lineTo(0.14129, -0.27974)
loop_1 = loop_1.lineTo(0.09688, -0.28529)
loop_1 = loop_1.lineTo(0.08625, -0.2858)
loop_1 = loop_1.lineTo(0.04857, -0.28604)
loop_1 = loop_1.lineTo(0.02615, -0.28683)
loop_1 = loop_1.threePointArc((0.00678, -0.2855), (-0.0085, -0.28483))
loop_1 = loop_1.lineTo(-0.02733, -0.28501)
loop_1 = loop_1.lineTo(-0.05776, -0.2839)
loop_1 = loop_1.lineTo(-0.07723, -0.28415)
loop_1 = loop_1.threePointArc((-0.10415, -0.28335), (-0.12829, -0.28227))
loop_1 = loop_1.lineTo(-0.15626, -0.27814)
loop_1 = loop_1.lineTo(-0.1709, -0.2749)
loop_1 = loop_1.lineTo(-0.19475, -0.26546)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_34_interval_0.stl')