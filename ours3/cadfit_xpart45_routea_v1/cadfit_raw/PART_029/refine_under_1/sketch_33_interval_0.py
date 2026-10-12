import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19377, -0.0794, 0.19482), normal=(-0.0, -0.78921, -0.61412), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00522, 0.08687)
loop_1 = loop_1.lineTo(0.01338, 0.07408)
loop_1 = loop_1.threePointArc((0.01443, 0.06302), (0.01479, 0.05849))
loop_1 = loop_1.lineTo(0.01228, 0.04727)
loop_1 = loop_1.lineTo(0.00798, 0.03684)
loop_1 = loop_1.threePointArc((-0.00494, 0.02746), (-0.01151, 0.02435))
loop_1 = loop_1.threePointArc((-0.01933, 0.02556), (-0.02589, 0.02648))
loop_1 = loop_1.lineTo(-0.03886, 0.03868)
loop_1 = loop_1.lineTo(-0.04445, 0.05587)
loop_1 = loop_1.threePointArc((-0.04409, 0.06546), (-0.04368, 0.07408))
loop_1 = loop_1.threePointArc((-0.03616, 0.08683), (-0.03274, 0.09083))
loop_1 = loop_1.threePointArc((-0.01882, 0.09708), (-0.01253, 0.09779))
loop_1 = loop_1.lineTo(0.00522, 0.08687)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_33_interval_0.stl')