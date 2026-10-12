import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40869, 0.88802, 0.01843), normal=(0.41839, -0.90827, 9e-05), xDir=(-0.90827, -0.41839, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21448, 0.12484)
loop_1 = loop_1.lineTo(-0.08521, -0.05297)
loop_1 = loop_1.lineTo(-0.02758, -0.05454)
loop_1 = loop_1.lineTo(0.02075, -0.05075)
loop_1 = loop_1.lineTo(0.03385, -0.05117)
loop_1 = loop_1.lineTo(0.08643, -0.05659)
loop_1 = loop_1.lineTo(0.11068, -0.06166)
loop_1 = loop_1.lineTo(0.14367, -0.06008)
loop_1 = loop_1.lineTo(0.16333, -0.06083)
loop_1 = loop_1.lineTo(0.20091, -0.07055)
loop_1 = loop_1.lineTo(0.21324, -0.07296)
loop_1 = loop_1.lineTo(0.21445, 0.12053)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_20_interval_0.stl')