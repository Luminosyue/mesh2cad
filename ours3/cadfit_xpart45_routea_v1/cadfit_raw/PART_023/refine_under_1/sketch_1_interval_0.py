import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40731, -0.03128, -0.00197), normal=(-0.96875, 0.24802, -0.00174), xDir=(0.24802, 0.96876, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28593, 0.81285)
loop_1 = loop_1.lineTo(-0.28651, 0.5001)
loop_1 = loop_1.threePointArc((-0.28929, 0.51436), (-0.2915, 0.52484))
loop_1 = loop_1.lineTo(-0.30497, 0.55041)
loop_1 = loop_1.lineTo(-0.31181, 0.57584)
loop_1 = loop_1.lineTo(-0.31027, 0.59461)
loop_1 = loop_1.threePointArc((-0.30276, 0.6153), (-0.29598, 0.62642))
loop_1 = loop_1.lineTo(-0.28849, 0.64523)
loop_1 = loop_1.lineTo(-0.28701, 0.65633)
loop_1 = loop_1.threePointArc((-0.28862, 0.66722), (-0.29035, 0.67764))
loop_1 = loop_1.lineTo(-0.29243, 0.69494)
loop_1 = loop_1.lineTo(-0.29297, 0.70686)
loop_1 = loop_1.lineTo(-0.29285, 0.72068)
loop_1 = loop_1.lineTo(-0.29269, 0.7324)
loop_1 = loop_1.lineTo(-0.29113, 0.74571)
loop_1 = loop_1.threePointArc((-0.28819, 0.7778), (-0.2865, 0.8057))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_1_interval_0.stl')