import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73468, 0.34807, 0.01859), normal=(0.89238, -0.45115, -0.01107), xDir=(-0.45118, -0.89243, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40349, 0.22596)
loop_1 = loop_1.lineTo(-0.40873, 0.21417)
loop_1 = loop_1.lineTo(-0.41548, 0.16159)
loop_1 = loop_1.lineTo(-0.41785, 0.11348)
loop_1 = loop_1.lineTo(-0.41806, 0.10009)
loop_1 = loop_1.lineTo(-0.42007, 0.06163)
loop_1 = loop_1.lineTo(-0.42093, 0.01727)
loop_1 = loop_1.lineTo(-0.42032, 0.00551)
loop_1 = loop_1.threePointArc((-0.42009, -0.02105), (-0.41979, -0.04284))
loop_1 = loop_1.lineTo(-0.41756, -0.07895)
loop_1 = loop_1.lineTo(-0.41731, -0.0903)
loop_1 = loop_1.lineTo(-0.41811, -0.12705)
loop_1 = loop_1.threePointArc((-0.40795, 0.04124), (-0.40357, 0.22236))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_41_interval_0.stl')