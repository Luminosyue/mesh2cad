import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.85941, 0.02055, 0.06457), normal=(-0.99056, -0.13708, 0.00122), xDir=(-0.13708, 0.99056, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08054, 0.29212)
loop_1 = loop_1.lineTo(0.01879, 0.28936)
loop_1 = loop_1.lineTo(0.006, 0.28948)
loop_1 = loop_1.lineTo(-0.02891, 0.28809)
loop_1 = loop_1.lineTo(-0.0465, 0.28882)
loop_1 = loop_1.threePointArc((-0.08045, 0.28712), (-0.10864, 0.28518))
loop_1 = loop_1.threePointArc((-0.14597, 0.28313), (-0.1772, 0.2812))
loop_1 = loop_1.lineTo(-0.21862, 0.27587)
loop_1 = loop_1.lineTo(-0.23269, 0.27476)
loop_1 = loop_1.lineTo(0.21822, 0.27746)
loop_1 = loop_1.lineTo(0.18296, 0.2856)
loop_1 = loop_1.lineTo(0.16879, 0.28567)
loop_1 = loop_1.lineTo(0.1256, 0.29114)
loop_1 = loop_1.lineTo(0.08539, 0.292)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_42_interval_0.stl')