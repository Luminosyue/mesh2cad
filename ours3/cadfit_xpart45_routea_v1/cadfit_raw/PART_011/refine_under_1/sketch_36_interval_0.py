import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73468, 0.34807, 0.01859), normal=(0.89238, -0.45115, -0.01107), xDir=(-0.45118, -0.89243, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.39146, 0.2235)
loop_1 = loop_1.lineTo(0.40014, -0.13711)
loop_1 = loop_1.lineTo(0.40932, -0.12388)
loop_1 = loop_1.lineTo(0.406, -0.07895)
loop_1 = loop_1.threePointArc((0.4047, -0.01506), (0.40267, 0.04276))
loop_1 = loop_1.lineTo(0.40186, 0.06097)
loop_1 = loop_1.lineTo(0.40166, 0.10867)
loop_1 = loop_1.lineTo(0.40223, 0.2097)
loop_1 = loop_1.lineTo(0.39356, 0.2208)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_36_interval_0.stl')