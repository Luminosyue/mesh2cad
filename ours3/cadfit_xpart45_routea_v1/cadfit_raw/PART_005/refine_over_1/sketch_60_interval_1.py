import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.56097, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.38925, -0.4192)
loop_1 = loop_1.lineTo(0.12533, -0.42184)
loop_1 = loop_1.lineTo(-0.40194, -0.47227)
loop_1 = loop_1.lineTo(-0.44413, -0.52398)
loop_1 = loop_1.lineTo(0.50196, -0.52821)
loop_1 = loop_1.threePointArc((0.49249, -0.521), (0.48447, -0.51252))
loop_1 = loop_1.threePointArc((0.46719, -0.49359), (0.45101, -0.47323))
loop_1 = loop_1.lineTo(0.4258, -0.44125)
loop_1 = loop_1.threePointArc((0.40743, -0.42956), (0.38969, -0.41976))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_60_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_60_interval_1.stl')