import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12863, -0.71702, -0.00396), normal=(0.00014, -0.99998, 0.00576), xDir=(-1.0, -0.00014, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34096, -0.19958)
loop_1 = loop_1.lineTo(-0.41345, -0.19959)
loop_1 = loop_1.lineTo(-0.41345, 0.26066)
loop_1 = loop_1.lineTo(-0.38058, 0.20933)
loop_1 = loop_1.lineTo(-0.3682, 0.26065)
loop_1 = loop_1.lineTo(-0.33411, 0.26065)
loop_1 = loop_1.threePointArc((-0.35267, 0.2448), (-0.37018, 0.22934))
loop_1 = loop_1.lineTo(-0.37961, 0.20933)
loop_1 = loop_1.lineTo(-0.39113, 0.1799)
loop_1 = loop_1.lineTo(-0.39131, 0.15467)
loop_1 = loop_1.lineTo(-0.34506, -0.18768)
loop_1 = loop_1.lineTo(-0.34096, -0.19958)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_6_interval_1.stl')