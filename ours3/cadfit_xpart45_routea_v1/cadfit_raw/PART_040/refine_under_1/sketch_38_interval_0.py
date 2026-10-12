import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14202, 0.22178)
loop_1 = loop_1.lineTo(0.13804, 0.21177)
loop_1 = loop_1.lineTo(0.1174, 0.19227)
loop_1 = loop_1.lineTo(0.08773, 0.27704)
loop_1 = loop_1.lineTo(0.10411, 0.27731)
loop_1 = loop_1.lineTo(0.11429, 0.27338)
loop_1 = loop_1.threePointArc((0.12839, 0.26082), (0.13281, 0.25585))
loop_1 = loop_1.lineTo(0.14081, 0.2375)
loop_1 = loop_1.threePointArc((0.14134, 0.23004), (0.14194, 0.22288))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_38_interval_0.stl')