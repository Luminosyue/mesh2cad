import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21347), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.93367, 0.14624)
loop_1 = loop_1.lineTo(0.94612, 0.04918)
loop_1 = loop_1.threePointArc((0.9302, 0.02928), (0.91527, 0.01003))
loop_1 = loop_1.lineTo(0.9336, 0.14355)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_66_interval_0.stl')