import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10276, 0.9687)
loop_1 = loop_1.threePointArc((0.10977, 0.9652), (0.11695, 0.96132))
loop_1 = loop_1.threePointArc((0.10518, 0.96739), (0.09297, 0.97393))
loop_1 = loop_1.lineTo(0.0682, 0.98323)
loop_1 = loop_1.lineTo(0.05556, 0.9874)
loop_1 = loop_1.threePointArc((0.03748, 0.99174), (0.01887, 0.99644))
loop_1 = loop_1.lineTo(0.00265, 0.99792)
loop_1 = loop_1.lineTo(0.21844, 0.99753)
loop_1 = loop_1.lineTo(0.10291, 0.96873)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.55)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_65_interval_0.stl')