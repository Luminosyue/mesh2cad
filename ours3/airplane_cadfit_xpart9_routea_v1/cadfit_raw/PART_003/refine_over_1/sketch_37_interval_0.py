import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.79208, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24942, -0.01933)
loop_1 = loop_1.lineTo(0.14419, -0.01963)
loop_1 = loop_1.threePointArc((0.15118, -0.03334), (0.15803, -0.04763))
loop_1 = loop_1.threePointArc((0.1724, -0.07694), (0.18642, -0.10478))
loop_1 = loop_1.threePointArc((0.19098, -0.11435), (0.19557, -0.12325))
loop_1 = loop_1.lineTo(0.20367, -0.13907)
loop_1 = loop_1.lineTo(0.22569, -0.17275)
loop_1 = loop_1.lineTo(0.24942, -0.20845)
loop_1 = loop_1.lineTo(0.24942, -0.0195)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_37_interval_0.stl')