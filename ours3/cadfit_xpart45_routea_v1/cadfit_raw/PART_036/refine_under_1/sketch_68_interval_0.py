import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.17741), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16805, 0.16415)
loop_1 = loop_1.threePointArc((-0.16237, 0.16334), (-0.15802, 0.16294))
loop_1 = loop_1.lineTo(-0.11706, 0.16025)
loop_1 = loop_1.lineTo(-0.10899, 0.12745)
loop_1 = loop_1.lineTo(-0.11449, 0.13944)
loop_1 = loop_1.lineTo(-0.11716, 0.11881)
loop_1 = loop_1.lineTo(-0.13471, 0.11856)
loop_1 = loop_1.lineTo(-0.15131, 0.11756)
loop_1 = loop_1.threePointArc((-0.15873, 0.11489), (-0.16649, 0.1122))
loop_1 = loop_1.lineTo(-0.17147, 0.16499)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_68_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_68_interval_0.stl')