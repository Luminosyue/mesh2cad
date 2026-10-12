import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0279, 0.21417, -0.10096), normal=(0.1889, 0.58283, 0.79033), xDir=(0.95128, -0.30832, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2103, -0.46449)
loop_1 = loop_1.lineTo(-0.34908, -0.52141)
loop_1 = loop_1.lineTo(-0.32838, -0.50709)
loop_1 = loop_1.lineTo(-0.29615, -0.4867)
loop_1 = loop_1.lineTo(-0.2209, -0.46466)
loop_1 = loop_1.lineTo(-0.20562, -0.45957)
loop_1 = loop_1.lineTo(-0.18004, -0.45313)
loop_1 = loop_1.lineTo(-0.13614, -0.44067)
loop_1 = loop_1.lineTo(-0.11937, -0.43478)
loop_1 = loop_1.lineTo(-0.08491, -0.42497)
loop_1 = loop_1.threePointArc((-0.04988, -0.4106), (-0.01783, -0.39812))
loop_1 = loop_1.lineTo(0.01526, -0.38304)
loop_1 = loop_1.lineTo(0.04812, -0.36698)
loop_1 = loop_1.lineTo(0.06979, -0.35482)
loop_1 = loop_1.lineTo(0.42757, -0.35113)
loop_1 = loop_1.lineTo(-0.20232, -0.46308)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_6_interval_1.stl')