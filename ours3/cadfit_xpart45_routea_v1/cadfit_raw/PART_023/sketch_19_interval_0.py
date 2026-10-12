import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.33865, -0.02794, -0.18426), normal=(-0.86274, 0.50566, 0.00027), xDir=(0.50566, 0.86274, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.42012, 0.19694)
loop_1 = loop_1.lineTo(0.40999, 0.19659)
loop_1 = loop_1.lineTo(0.39212, 0.1913)
loop_1 = loop_1.lineTo(0.37585, 0.17147)
loop_1 = loop_1.lineTo(0.37788, 0.15043)
loop_1 = loop_1.lineTo(0.38301, 0.13839)
loop_1 = loop_1.lineTo(0.40614, 0.11276)
loop_1 = loop_1.lineTo(0.45338, 0.09114)
loop_1 = loop_1.lineTo(0.47524, 0.0924)
loop_1 = loop_1.lineTo(0.49417, 0.10211)
loop_1 = loop_1.lineTo(0.50682, 0.11286)
loop_1 = loop_1.lineTo(0.50766, 0.13839)
loop_1 = loop_1.lineTo(0.49636, 0.16178)
loop_1 = loop_1.lineTo(0.4849, 0.17467)
loop_1 = loop_1.lineTo(0.46513, 0.18738)
loop_1 = loop_1.threePointArc((0.45787, 0.19005), (0.45261, 0.19187))
loop_1 = loop_1.lineTo(0.42012, 0.19694)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/sketch_19_interval_0.stl')