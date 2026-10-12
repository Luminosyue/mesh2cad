import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14769, 0.4261, -0.00114), normal=(0.29564, -0.9552, -0.01409), xDir=(-0.95529, -0.29567, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10927, 0.21308)
loop_1 = loop_1.lineTo(0.11157, -0.31397)
loop_1 = loop_1.lineTo(0.08707, -0.27959)
loop_1 = loop_1.lineTo(0.04829, -0.23)
loop_1 = loop_1.lineTo(0.03695, -0.20815)
loop_1 = loop_1.lineTo(0.02892, -0.18616)
loop_1 = loop_1.lineTo(0.02421, -0.16407)
loop_1 = loop_1.lineTo(0.02285, -0.14193)
loop_1 = loop_1.lineTo(0.02482, -0.11977)
loop_1 = loop_1.lineTo(0.03013, -0.09766)
loop_1 = loop_1.lineTo(0.03666, -0.05206)
loop_1 = loop_1.lineTo(0.04912, -0.00596)
loop_1 = loop_1.lineTo(0.06738, 0.0406)
loop_1 = loop_1.lineTo(0.08306, 0.08773)
loop_1 = loop_1.lineTo(0.09476, 0.13758)
loop_1 = loop_1.lineTo(0.10168, 0.18635)
loop_1 = loop_1.lineTo(0.10775, 0.20773)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_42_interval_0.stl')