import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2229, 0.13495)
loop_1 = loop_1.lineTo(-0.21159, 0.12137)
loop_1 = loop_1.threePointArc((-0.2042, 0.11843), (-0.1965, 0.11536))
loop_1 = loop_1.lineTo(-0.17098, 0.11467)
loop_1 = loop_1.lineTo(-0.18729, 0.12036)
loop_1 = loop_1.lineTo(-0.16047, 0.19702)
loop_1 = loop_1.threePointArc((-0.17204, 0.1987), (-0.17986, 0.19944))
loop_1 = loop_1.lineTo(-0.19816, 0.19679)
loop_1 = loop_1.lineTo(-0.2229, 0.13495)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_17_interval_0.stl')