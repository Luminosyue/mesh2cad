import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87369, -0.18556, 0.0333), normal=(0.99097, 0.13358, 0.01143), xDir=(0.13359, -0.99104, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06238, 0.26439)
loop_1 = loop_1.lineTo(-0.00508, 0.26401)
loop_1 = loop_1.lineTo(-0.01869, 0.26435)
loop_1 = loop_1.threePointArc((-0.05163, 0.26352), (-0.08125, 0.26334))
loop_1 = loop_1.threePointArc((-0.11637, 0.2622), (-0.14557, 0.2608))
loop_1 = loop_1.lineTo(-0.16147, 0.25984)
loop_1 = loop_1.lineTo(-0.18095, 0.2579)
loop_1 = loop_1.lineTo(-0.20381, 0.25449)
loop_1 = loop_1.lineTo(-0.21678, 0.25291)
loop_1 = loop_1.lineTo(-0.24923, 0.24536)
loop_1 = loop_1.lineTo(-0.26253, 0.24288)
loop_1 = loop_1.lineTo(-0.27444, 0.23974)
loop_1 = loop_1.lineTo(0.20289, 0.25461)
loop_1 = loop_1.lineTo(0.14865, 0.26043)
loop_1 = loop_1.threePointArc((0.12416, 0.26185), (0.1046, 0.263))
loop_1 = loop_1.lineTo(0.06695, 0.26421)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_33_interval_0.stl')