import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03112, 0.32587, -0.26009), normal=(-0.0, -0.01499, 0.99989), xDir=(-0.0, 0.99989, 0.01499))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.47091, -0.43883)
loop_1 = loop_1.lineTo(0.51804, -0.40043)
loop_1 = loop_1.lineTo(0.54689, -0.34907)
loop_1 = loop_1.lineTo(0.56979, -0.29927)
loop_1 = loop_1.lineTo(0.57739, -0.2828)
loop_1 = loop_1.lineTo(0.55884, -0.30573)
loop_1 = loop_1.lineTo(0.54276, -0.32899)
loop_1 = loop_1.lineTo(0.51731, -0.35393)
loop_1 = loop_1.lineTo(0.50026, -0.39637)
loop_1 = loop_1.lineTo(0.4674, -0.44116)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_2_interval_0.stl')