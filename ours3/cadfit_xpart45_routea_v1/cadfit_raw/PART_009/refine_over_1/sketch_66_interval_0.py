import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.175, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.9934, -0.30187)
loop_1 = loop_1.threePointArc((0.99283, -0.31689), (0.99178, -0.3325))
loop_1 = loop_1.threePointArc((0.99131, -0.3602), (0.99047, -0.38886))
loop_1 = loop_1.threePointArc((0.98944, -0.4068), (0.98867, -0.42388))
loop_1 = loop_1.threePointArc((0.98801, -0.44232), (0.98696, -0.46134))
loop_1 = loop_1.lineTo(0.98633, -0.47149)
loop_1 = loop_1.threePointArc((0.98298, -0.4896), (0.97892, -0.50835))
loop_1 = loop_1.lineTo(0.97567, -0.5226)
loop_1 = loop_1.lineTo(0.99342, -0.52963)
loop_1 = loop_1.lineTo(0.99342, -0.30203)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_66_interval_0.stl')