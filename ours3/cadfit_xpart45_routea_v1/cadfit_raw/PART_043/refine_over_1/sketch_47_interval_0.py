import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.12573, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14516, 0.14)
loop_1 = loop_1.lineTo(0.16206, 0.1399)
loop_1 = loop_1.lineTo(0.16202, 0.12385)
loop_1 = loop_1.lineTo(0.16243, 0.10894)
loop_1 = loop_1.lineTo(0.16224, 0.09379)
loop_1 = loop_1.threePointArc((0.16258, 0.08372), (0.16281, 0.07334))
loop_1 = loop_1.lineTo(0.1639, 0.0576)
loop_1 = loop_1.lineTo(0.16291, 0.03297)
loop_1 = loop_1.lineTo(0.16022, 0.02107)
loop_1 = loop_1.lineTo(0.15379, 0.00789)
loop_1 = loop_1.lineTo(0.14516, 0.1399)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_47_interval_0.stl')