import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04001, -0.95966)
loop_1 = loop_1.threePointArc((0.04552, -0.97003), (0.04685, -0.97129))
loop_1 = loop_1.lineTo(0.05747, -0.98042)
loop_1 = loop_1.lineTo(0.05697, -0.92846)
loop_1 = loop_1.lineTo(0.11931, -0.92446)
loop_1 = loop_1.lineTo(0.10917, -0.92084)
loop_1 = loop_1.lineTo(0.09596, -0.92039)
loop_1 = loop_1.lineTo(0.07735, -0.92042)
loop_1 = loop_1.lineTo(0.06089, -0.92356)
loop_1 = loop_1.threePointArc((0.05393, -0.92709), (0.0507, -0.9292))
loop_1 = loop_1.threePointArc((0.04178, -0.93801), (0.03973, -0.94207))
loop_1 = loop_1.lineTo(0.04001, -0.95966)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_71_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_71_interval_0.stl')