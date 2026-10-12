import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.21303, 0.03948, -0.00743), normal=(0.0, -0.78914, 0.61421), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11807, -0.06229)
loop_1 = loop_1.lineTo(-0.35809, -0.06229)
loop_1 = loop_1.lineTo(-0.67423, -0.06229)
loop_1 = loop_1.lineTo(-0.67684, -0.02308)
loop_1 = loop_1.lineTo(-0.55632, -0.01233)
loop_1 = loop_1.lineTo(-0.51424, -0.00858)
loop_1 = loop_1.lineTo(-0.49902, -0.00722)
loop_1 = loop_1.lineTo(-0.46581, -0.00426)
loop_1 = loop_1.lineTo(-0.31572, 0.00913)
loop_1 = loop_1.lineTo(-0.28388, 0.01197)
loop_1 = loop_1.lineTo(-0.09801, 0.02854)
loop_1 = loop_1.lineTo(-0.09798, 0.01371)
loop_1 = loop_1.threePointArc((-0.10024, -0.00366), (-0.10337, -0.0193))
loop_1 = loop_1.threePointArc((-0.11029, -0.03744), (-0.11531, -0.05387))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_8_interval_0.stl')