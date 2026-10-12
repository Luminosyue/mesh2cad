import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4728, -0.04168, 0.22473), normal=(-0.67104, 0.74142, -0.00038), xDir=(0.74142, 0.67104, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15099, 1.06465)
loop_1 = loop_1.lineTo(-0.07084, 1.06465)
loop_1 = loop_1.lineTo(-0.07096, 0.80575)
loop_1 = loop_1.lineTo(-0.07632, 0.84361)
loop_1 = loop_1.lineTo(-0.09784, 0.84806)
loop_1 = loop_1.lineTo(-0.10898, 0.82875)
loop_1 = loop_1.lineTo(-0.11807, 0.80926)
loop_1 = loop_1.lineTo(-0.12703, 0.79411)
loop_1 = loop_1.lineTo(-0.13206, 0.78343)
loop_1 = loop_1.lineTo(-0.14379, 0.75471)
loop_1 = loop_1.lineTo(-0.14709, 0.74085)
loop_1 = loop_1.lineTo(-0.15077, 0.72659)
loop_1 = loop_1.lineTo(-0.15098, 1.06031)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_9_interval_0.stl')