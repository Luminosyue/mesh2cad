import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07687, -0.15353, 0.11392), normal=(-0.0362, 0.88964, -0.45522), xDir=(0.99917, 0.04065, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41295, -0.07019)
loop_1 = loop_1.lineTo(0.64533, -0.07019)
loop_1 = loop_1.lineTo(0.65556, -0.07019)
loop_1 = loop_1.lineTo(0.97377, -0.06987)
loop_1 = loop_1.threePointArc((0.96814, -0.06355), (0.96271, -0.05745))
loop_1 = loop_1.lineTo(0.9754, 0.00351)
loop_1 = loop_1.threePointArc((0.97766, 0.02142), (0.97863, 0.03594))
loop_1 = loop_1.lineTo(0.79232, 0.04051)
loop_1 = loop_1.lineTo(0.39125, 0.03983)
loop_1 = loop_1.threePointArc((0.38956, 0.01604), (0.38996, 0.00267))
loop_1 = loop_1.threePointArc((0.39285, -0.01433), (0.39639, -0.02827))
loop_1 = loop_1.threePointArc((0.40317, -0.04348), (0.40803, -0.05701))
loop_1 = loop_1.lineTo(0.41295, -0.07019)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_4_interval_0.stl')