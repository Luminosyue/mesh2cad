import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41562, -0.47954, 0.73437), normal=(-0.00015, -0.00396, 0.99999), xDir=(-0.0, 0.99999, 0.00396))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25659, -0.70433)
loop_1 = loop_1.lineTo(0.26778, -0.68495)
loop_1 = loop_1.lineTo(0.26777, -0.75563)
loop_1 = loop_1.lineTo(0.21781, -0.75563)
loop_1 = loop_1.lineTo(0.22857, -0.74275)
loop_1 = loop_1.lineTo(0.24899, -0.71511)
loop_1 = loop_1.lineTo(0.25659, -0.70433)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_19_interval_1.stl')