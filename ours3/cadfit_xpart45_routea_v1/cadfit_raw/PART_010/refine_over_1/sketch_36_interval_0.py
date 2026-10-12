import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.7933, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10648, -0.55055)
loop_1 = loop_1.lineTo(0.15016, -0.55421)
loop_1 = loop_1.lineTo(0.18615, -0.56946)
loop_1 = loop_1.lineTo(0.2022, -0.59235)
loop_1 = loop_1.lineTo(0.22364, -0.61594)
loop_1 = loop_1.lineTo(0.23727, -0.62817)
loop_1 = loop_1.threePointArc((0.2454, -0.6344), (0.25332, -0.64127))
loop_1 = loop_1.lineTo(0.28477, -0.65796)
loop_1 = loop_1.lineTo(0.10625, -0.65713)
loop_1 = loop_1.lineTo(0.10648, -0.55071)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_36_interval_0.stl')