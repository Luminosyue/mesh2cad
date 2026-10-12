import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40578, 0.79245, 0.01353), normal=(-0.46464, 0.88545, -0.00887), xDir=(0.88549, 0.46466, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36805, 0.16794)
loop_1 = loop_1.lineTo(0.38914, 0.13608)
loop_1 = loop_1.lineTo(0.38907, 0.08973)
loop_1 = loop_1.lineTo(0.38454, 0.04221)
loop_1 = loop_1.lineTo(0.3809, -0.0024)
loop_1 = loop_1.lineTo(0.37943, -0.01393)
loop_1 = loop_1.lineTo(0.37617, -0.04827)
loop_1 = loop_1.threePointArc((0.37555, -0.07437), (0.37532, -0.09668))
loop_1 = loop_1.threePointArc((0.37428, -0.11524), (0.37378, -0.13019))
loop_1 = loop_1.lineTo(0.3681, 0.16494)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_19_interval_1.stl')