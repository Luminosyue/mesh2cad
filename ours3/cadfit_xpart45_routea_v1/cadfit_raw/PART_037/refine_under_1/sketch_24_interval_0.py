import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.18917, 0.03772, 0.07386), normal=(-0.00191, -0.94596, 0.32428), xDir=(-1.0, 0.00202, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89483, 0.02851)
loop_1 = loop_1.lineTo(0.91048, -0.0009)
loop_1 = loop_1.threePointArc((0.90704, -0.00753), (0.90397, -0.01253))
loop_1 = loop_1.lineTo(-0.8052, -0.01033)
loop_1 = loop_1.lineTo(-0.80683, 0.003)
loop_1 = loop_1.threePointArc((-0.80707, 0.0243), (-0.80821, 0.04206))
loop_1 = loop_1.lineTo(-0.47164, 0.0418)
loop_1 = loop_1.threePointArc((-0.44975, 0.04178), (-0.43577, 0.04177))
loop_1 = loop_1.lineTo(0.88585, 0.03848)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_24_interval_0.stl')