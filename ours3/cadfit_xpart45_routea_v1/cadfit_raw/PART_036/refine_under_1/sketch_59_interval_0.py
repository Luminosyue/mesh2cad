import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.01, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16966, -0.04262)
loop_1 = loop_1.lineTo(-0.18174, -0.04567)
loop_1 = loop_1.lineTo(-0.19924, -0.0459)
loop_1 = loop_1.lineTo(-0.21658, -0.04436)
loop_1 = loop_1.lineTo(-0.23399, -0.04437)
loop_1 = loop_1.lineTo(-0.25125, -0.03506)
loop_1 = loop_1.threePointArc((-0.25843, -0.02433), (-0.25883, -0.02344))
loop_1 = loop_1.lineTo(-0.15613, -0.02024)
loop_1 = loop_1.lineTo(-0.16966, -0.04262)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_59_interval_0.stl')