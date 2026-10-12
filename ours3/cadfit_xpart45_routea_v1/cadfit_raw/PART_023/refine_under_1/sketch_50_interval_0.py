import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.16, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29707, 0.98172)
loop_1 = loop_1.threePointArc((0.28449, 0.98123), (0.27137, 0.98134))
loop_1 = loop_1.lineTo(0.25726, 0.97597)
loop_1 = loop_1.lineTo(0.24549, 0.97454)
loop_1 = loop_1.lineTo(0.23377, 0.96882)
loop_1 = loop_1.lineTo(0.31555, 0.95961)
loop_1 = loop_1.lineTo(0.33432, 0.96)
loop_1 = loop_1.lineTo(0.51322, 0.96049)
loop_1 = loop_1.lineTo(0.50067, 0.96993)
loop_1 = loop_1.lineTo(0.48702, 0.9728)
loop_1 = loop_1.lineTo(0.47533, 0.97899)
loop_1 = loop_1.lineTo(0.46025, 0.97942)
loop_1 = loop_1.lineTo(0.44861, 0.9805)
loop_1 = loop_1.lineTo(0.41952, 0.98082)
loop_1 = loop_1.threePointArc((0.40032, 0.98077), (0.38054, 0.98122))
loop_1 = loop_1.threePointArc((0.34258, 0.98139), (0.30633, 0.98136))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_50_interval_0.stl')