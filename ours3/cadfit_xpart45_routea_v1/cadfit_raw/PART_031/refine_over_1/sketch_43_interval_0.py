import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30023, -0.76557, -0.08503), normal=(-0.37917, 0.92533, 0.0001), xDir=(0.92533, 0.37917, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22536, -0.57443)
loop_1 = loop_1.lineTo(-0.22536, -0.59235)
loop_1 = loop_1.lineTo(-0.08267, -0.62704)
loop_1 = loop_1.threePointArc((-0.03193, -0.66043), (0.01749, -0.69332))
loop_1 = loop_1.threePointArc((0.06458, -0.69963), (0.10666, -0.70367))
loop_1 = loop_1.lineTo(0.09777, -0.69211)
loop_1 = loop_1.threePointArc((0.08757, -0.6655), (0.07884, -0.64146))
loop_1 = loop_1.lineTo(0.0613, -0.62087)
loop_1 = loop_1.lineTo(0.03274, -0.60334)
loop_1 = loop_1.lineTo(0.01482, -0.59436)
loop_1 = loop_1.threePointArc((0.00077, -0.59456), (-0.01004, -0.59443))
loop_1 = loop_1.lineTo(-0.02782, -0.59252)
loop_1 = loop_1.lineTo(-0.04633, -0.58959)
loop_1 = loop_1.lineTo(-0.10014, -0.58948)
loop_1 = loop_1.lineTo(-0.15396, -0.58152)
loop_1 = loop_1.lineTo(-0.19239, -0.58129)
loop_1 = loop_1.threePointArc((-0.20942, -0.57765), (-0.2231, -0.57449))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_43_interval_0.stl')