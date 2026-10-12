import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0125, -0.28579, -0.12479), normal=(-0.57108, 0.8209, 0.00186), xDir=(0.8209, 0.57108, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77274, 0.82972)
loop_1 = loop_1.lineTo(0.77304, 0.49374)
loop_1 = loop_1.lineTo(0.77344, 0.50412)
loop_1 = loop_1.lineTo(0.77578, 0.5257)
loop_1 = loop_1.lineTo(0.77952, 0.55853)
loop_1 = loop_1.lineTo(0.77901, 0.59311)
loop_1 = loop_1.lineTo(0.77718, 0.606)
loop_1 = loop_1.lineTo(0.77654, 0.6272)
loop_1 = loop_1.lineTo(0.77405, 0.65411)
loop_1 = loop_1.threePointArc((0.77319, 0.68344), (0.77284, 0.70505))
loop_1 = loop_1.lineTo(0.77441, 0.71538)
loop_1 = loop_1.threePointArc((0.77499, 0.73577), (0.77521, 0.75536))
loop_1 = loop_1.lineTo(0.77772, 0.77942)
loop_1 = loop_1.lineTo(0.78023, 0.80347)
loop_1 = loop_1.lineTo(0.77976, 0.81364)
loop_1 = loop_1.lineTo(0.77412, 0.82657)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_28_interval_0.stl')