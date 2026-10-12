import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76488, -0.43076, -0.01474), normal=(-0.89584, 0.44438, 0.00038), xDir=(0.44438, 0.89584, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15235, -0.23452)
loop_1 = loop_1.lineTo(-0.13615, -0.24516)
loop_1 = loop_1.lineTo(-0.11975, -0.24813)
loop_1 = loop_1.lineTo(-0.10777, -0.24563)
loop_1 = loop_1.lineTo(-0.09584, -0.24708)
loop_1 = loop_1.lineTo(-0.08447, -0.24767)
loop_1 = loop_1.lineTo(-0.04132, -0.24759)
loop_1 = loop_1.lineTo(-0.02875, -0.25363)
loop_1 = loop_1.lineTo(-0.01151, -0.25515)
loop_1 = loop_1.lineTo(0.02281, -0.2493)
loop_1 = loop_1.lineTo(0.06457, -0.2468)
loop_1 = loop_1.lineTo(0.07864, -0.25231)
loop_1 = loop_1.lineTo(0.09674, -0.25382)
loop_1 = loop_1.lineTo(0.11299, -0.24979)
loop_1 = loop_1.lineTo(0.12755, -0.24641)
loop_1 = loop_1.lineTo(-0.14987, -0.23462)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_4_interval_0.stl')