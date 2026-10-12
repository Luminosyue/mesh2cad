import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.53187, 0.0771, -0.02347), normal=(0.67102, -0.74143, 0.00244), xDir=(-0.74143, -0.67103, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10898, -0.2875)
loop_1 = loop_1.lineTo(0.10925, -0.35895)
loop_1 = loop_1.threePointArc((0.13127, -0.35815), (0.15107, -0.35742))
loop_1 = loop_1.threePointArc((0.1697, -0.3546), (0.18784, -0.35194))
loop_1 = loop_1.lineTo(0.19964, -0.34905)
loop_1 = loop_1.lineTo(0.17867, -0.33704)
loop_1 = loop_1.lineTo(0.16701, -0.32873)
loop_1 = loop_1.threePointArc((0.15673, -0.31244), (0.15326, -0.30586))
loop_1 = loop_1.lineTo(0.14285, -0.29601)
loop_1 = loop_1.threePointArc((0.13238, -0.29127), (0.12283, -0.28689))
loop_1 = loop_1.lineTo(0.10898, -0.2875)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_22_interval_0.stl')