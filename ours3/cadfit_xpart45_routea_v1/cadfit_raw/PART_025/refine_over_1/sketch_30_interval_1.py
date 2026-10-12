import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.683, -0.07398, -0.41253), normal=(-0.50572, 0.1306, -0.85275), xDir=(0.25005, 0.96823, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07608, -0.31689)
loop_1 = loop_1.lineTo(0.10382, -0.31792)
loop_1 = loop_1.lineTo(0.10379, -0.33259)
loop_1 = loop_1.lineTo(-0.09928, -0.33223)
loop_1 = loop_1.lineTo(-0.08442, -0.33061)
loop_1 = loop_1.threePointArc((-0.06107, -0.32944), (-0.0384, -0.32843))
loop_1 = loop_1.lineTo(-0.0192, -0.32694)
loop_1 = loop_1.lineTo(0.00905, -0.32411)
loop_1 = loop_1.lineTo(0.05329, -0.32082)
loop_1 = loop_1.lineTo(0.07403, -0.31728)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_30_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_30_interval_1.stl')