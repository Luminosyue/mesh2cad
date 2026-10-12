import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03636, -0.90853, -0.00774), normal=(-0.00068, 0.99993, 0.01201), xDir=(1.0, 0.00068, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33007, 0.22847)
loop_1 = loop_1.threePointArc((0.33683, 0.01926), (0.34417, -0.18156))
loop_1 = loop_1.lineTo(-0.1553, -0.18156)
loop_1 = loop_1.lineTo(-0.17795, -0.17814)
loop_1 = loop_1.lineTo(-0.20762, -0.18156)
loop_1 = loop_1.lineTo(-0.22418, -0.18156)
loop_1 = loop_1.lineTo(-0.33768, -0.18156)
loop_1 = loop_1.lineTo(-0.33704, -0.17106)
loop_1 = loop_1.threePointArc((-0.32693, -0.0126), (-0.31521, 0.15239))
loop_1 = loop_1.lineTo(-0.31464, 0.16327)
loop_1 = loop_1.lineTo(-0.31011, 0.22847)
loop_1 = loop_1.lineTo(0.31926, 0.22847)
loop_1 = loop_1.lineTo(0.33007, 0.22847)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_28_interval_0.stl')