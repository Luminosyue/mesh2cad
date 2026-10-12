import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03468, -0.1495, -0.29885), normal=(-0.00152, -0.05475, 0.9985), xDir=(-0.0, 0.9985, 0.05475))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.59549, 0.45817)
loop_1 = loop_1.lineTo(-0.55717, 0.50252)
loop_1 = loop_1.lineTo(-0.82418, 0.02328)
loop_1 = loop_1.lineTo(-0.82123, 0.04238)
loop_1 = loop_1.lineTo(-0.81982, 0.06178)
loop_1 = loop_1.lineTo(-0.8062, 0.10342)
loop_1 = loop_1.lineTo(-0.78968, 0.14758)
loop_1 = loop_1.threePointArc((-0.77202, 0.19035), (-0.75738, 0.22778))
loop_1 = loop_1.lineTo(-0.73837, 0.27001)
loop_1 = loop_1.lineTo(-0.71802, 0.31027)
loop_1 = loop_1.lineTo(-0.69473, 0.35105)
loop_1 = loop_1.lineTo(-0.66193, 0.39263)
loop_1 = loop_1.lineTo(-0.62712, 0.43324)
loop_1 = loop_1.lineTo(-0.59816, 0.46457)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_22_interval_0.stl')