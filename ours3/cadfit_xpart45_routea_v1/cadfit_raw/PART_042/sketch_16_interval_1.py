import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4615, -0.22972, 0.02624), normal=(0.02642, -0.75494, 0.65526), xDir=(-0.99939, -0.03497, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.13717, -0.00362)
loop_1 = loop_1.lineTo(-1.17023, -0.01062)
loop_1 = loop_1.lineTo(-1.18964, -0.01843)
loop_1 = loop_1.lineTo(-1.20106, -0.02882)
loop_1 = loop_1.lineTo(-1.17086, -0.0339)
loop_1 = loop_1.threePointArc((-1.15972, -0.02891), (-1.15696, -0.02593))
loop_1 = loop_1.lineTo(-1.14568, -0.01646)
loop_1 = loop_1.lineTo(-1.13717, -0.00362)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_16_interval_1.stl')