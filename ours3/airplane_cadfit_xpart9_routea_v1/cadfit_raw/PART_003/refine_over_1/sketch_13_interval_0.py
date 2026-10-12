import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02557, 0.02763, -0.03919), normal=(-0.1889, -0.58283, -0.79033), xDir=(-0.95128, 0.30832, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35012, 0.32799)
loop_1 = loop_1.lineTo(-0.47229, 0.35337)
loop_1 = loop_1.lineTo(-0.48501, 0.35588)
loop_1 = loop_1.lineTo(-0.74045, 0.40953)
loop_1 = loop_1.lineTo(-0.72778, 0.40572)
loop_1 = loop_1.threePointArc((-0.7176, 0.40307), (-0.70773, 0.40096))
loop_1 = loop_1.lineTo(-0.67946, 0.3904)
loop_1 = loop_1.threePointArc((-0.65957, 0.38522), (-0.64145, 0.37893))
loop_1 = loop_1.lineTo(-0.62314, 0.37552)
loop_1 = loop_1.threePointArc((-0.60182, 0.37243), (-0.58619, 0.37074))
loop_1 = loop_1.lineTo(-0.55348, 0.36635)
loop_1 = loop_1.lineTo(-0.57652, 0.36617)
loop_1 = loop_1.lineTo(-0.60263, 0.3685)
loop_1 = loop_1.lineTo(-0.35455, 0.3287)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_13_interval_0.stl')