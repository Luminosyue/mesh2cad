import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05594, -0.11311, 0.5599), normal=(-0.08258, -6e-05, 0.99658), xDir=(-0.0, 1.0, 6e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.65217, -0.40214)
loop_1 = loop_1.lineTo(-0.69342, -0.40807)
loop_1 = loop_1.lineTo(-0.72403, -0.42432)
loop_1 = loop_1.lineTo(-0.39327, -0.42415)
loop_1 = loop_1.lineTo(-0.41133, -0.42043)
loop_1 = loop_1.lineTo(-0.42269, -0.41948)
loop_1 = loop_1.lineTo(-0.45147, -0.41329)
loop_1 = loop_1.lineTo(-0.49694, -0.41343)
loop_1 = loop_1.lineTo(-0.50893, -0.40807)
loop_1 = loop_1.lineTo(-0.52875, -0.40506)
loop_1 = loop_1.lineTo(-0.56989, -0.40607)
loop_1 = loop_1.lineTo(-0.60844, -0.40447)
loop_1 = loop_1.lineTo(-0.64944, -0.40237)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_20_interval_0.stl')