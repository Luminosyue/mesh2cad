import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.55471, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.83064, 0.11308)
loop_1 = loop_1.lineTo(0.83026, -0.11437)
loop_1 = loop_1.lineTo(0.81645, -0.08962)
loop_1 = loop_1.threePointArc((0.80462, -0.07945), (0.80193, -0.07762))
loop_1 = loop_1.lineTo(0.76892, -0.05526)
loop_1 = loop_1.threePointArc((0.76737, -0.04873), (0.76575, -0.04268))
loop_1 = loop_1.lineTo(0.76041, -0.02503)
loop_1 = loop_1.threePointArc((0.75768, -0.01454), (0.75501, -0.00376))
loop_1 = loop_1.lineTo(0.80181, 0.03834)
loop_1 = loop_1.threePointArc((0.80937, 0.04521), (0.81183, 0.04837))
loop_1 = loop_1.lineTo(0.82677, 0.09306)
loop_1 = loop_1.threePointArc((0.83005, 0.10688), (0.83063, 0.11291))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_84_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_84_interval_0.stl')