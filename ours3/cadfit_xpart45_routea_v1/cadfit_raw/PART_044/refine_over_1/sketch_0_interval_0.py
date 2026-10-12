import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50412, 0.09843, 0.38594), normal=(-0.54607, -0.83419, 0.077), xDir=(-0.83668, 0.54769, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08431, 0.16851)
loop_1 = loop_1.lineTo(-0.06788, 0.15731)
loop_1 = loop_1.lineTo(-0.05318, 0.10067)
loop_1 = loop_1.lineTo(-0.04892, -0.29402)
loop_1 = loop_1.threePointArc((-0.05236, -0.33432), (-0.05581, -0.3713))
loop_1 = loop_1.lineTo(-0.04039, -0.38135)
loop_1 = loop_1.lineTo(-0.03293, -0.39734)
loop_1 = loop_1.lineTo(-0.02097, -0.39791)
loop_1 = loop_1.lineTo(-0.00794, -0.40655)
loop_1 = loop_1.lineTo(-0.08916, -0.40678)
loop_1 = loop_1.lineTo(-0.08889, 0.16953)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_0_interval_0.stl')