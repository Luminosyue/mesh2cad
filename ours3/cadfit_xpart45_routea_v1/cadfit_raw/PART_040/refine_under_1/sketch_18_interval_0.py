import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21312, -0.0262)
loop_1 = loop_1.threePointArc((-0.20464, -0.02582), (-0.1965, -0.02542))
loop_1 = loop_1.lineTo(-0.1791, -0.01519)
loop_1 = loop_1.lineTo(-0.16831, 0.00231)
loop_1 = loop_1.lineTo(-0.16323, 0.02402)
loop_1 = loop_1.lineTo(-0.16972, 0.04218)
loop_1 = loop_1.threePointArc((-0.17518, 0.04806), (-0.18, 0.0534))
loop_1 = loop_1.lineTo(-0.21679, -0.02449)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_18_interval_0.stl')