import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26154, -0.16582)
loop_1 = loop_1.threePointArc((-0.25413, -0.16571), (-0.24641, -0.16578))
loop_1 = loop_1.threePointArc((-0.23735, -0.16354), (-0.22921, -0.16159))
loop_1 = loop_1.lineTo(-0.21223, -0.15194)
loop_1 = loop_1.threePointArc((-0.20704, -0.14615), (-0.20216, -0.1405))
loop_1 = loop_1.lineTo(-0.19504, -0.12249)
loop_1 = loop_1.threePointArc((-0.19485, -0.11496), (-0.19472, -0.10772))
loop_1 = loop_1.lineTo(-0.20408, -0.09038)
loop_1 = loop_1.lineTo(-0.21444, -0.08156)
loop_1 = loop_1.threePointArc((-0.22195, -0.07816), (-0.22978, -0.07461))
loop_1 = loop_1.lineTo(-0.26561, -0.16379)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_16_interval_0.stl')