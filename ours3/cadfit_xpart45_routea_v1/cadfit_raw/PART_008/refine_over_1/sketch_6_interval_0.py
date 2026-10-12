import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.72978, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.85551, 0.34719)
loop_1 = loop_1.lineTo(0.85691, 0.28784)
loop_1 = loop_1.lineTo(0.82902, 0.30235)
loop_1 = loop_1.lineTo(0.78756, 0.30939)
loop_1 = loop_1.lineTo(0.76778, 0.31326)
loop_1 = loop_1.lineTo(0.53014, 0.31159)
loop_1 = loop_1.lineTo(0.38037, 0.31139)
loop_1 = loop_1.lineTo(0.13874, 0.31231)
loop_1 = loop_1.threePointArc((-0.03536, 0.31245), (-0.21594, 0.31334))
loop_1 = loop_1.lineTo(0.85477, 0.34717)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_interval_0.stl')