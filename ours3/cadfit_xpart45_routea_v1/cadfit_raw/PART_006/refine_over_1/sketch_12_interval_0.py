import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59654, 0.69798, -0.15527), normal=(0.62416, -0.7813, 0.00026), xDir=(-0.7813, -0.62416, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.48099, -0.24761)
loop_1 = loop_1.lineTo(0.48113, -0.70302)
loop_1 = loop_1.lineTo(0.50255, -0.68328)
loop_1 = loop_1.lineTo(0.50669, -0.65686)
loop_1 = loop_1.lineTo(0.50927, -0.63033)
loop_1 = loop_1.lineTo(0.51029, -0.60368)
loop_1 = loop_1.threePointArc((0.50902, -0.48862), (0.51031, -0.37407))
loop_1 = loop_1.threePointArc((0.51105, -0.35594), (0.51077, -0.34315))
loop_1 = loop_1.threePointArc((0.51045, -0.32536), (0.50948, -0.31294))
loop_1 = loop_1.lineTo(0.50846, -0.29749)
loop_1 = loop_1.lineTo(0.5047, -0.26729)
loop_1 = loop_1.threePointArc((0.49248, -0.25712), (0.48467, -0.25066))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_12_interval_0.stl')