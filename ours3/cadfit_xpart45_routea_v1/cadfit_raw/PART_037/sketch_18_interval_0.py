import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45951, 0.08656, 0.27458), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.29116, -0.22556)
loop_1 = loop_1.lineTo(0.28744, -0.23726)
loop_1 = loop_1.lineTo(0.26818, -0.25706)
loop_1 = loop_1.lineTo(0.25804, -0.26059)
loop_1 = loop_1.lineTo(0.23787, -0.2612)
loop_1 = loop_1.threePointArc((0.23104, -0.25854), (0.22443, -0.25611))
loop_1 = loop_1.lineTo(0.19556, -0.21062)
loop_1 = loop_1.threePointArc((0.19627, -0.20457), (0.19705, -0.19828))
loop_1 = loop_1.lineTo(0.21374, -0.17735)
loop_1 = loop_1.lineTo(0.22436, -0.16964)
loop_1 = loop_1.threePointArc((0.23285, -0.16663), (0.23942, -0.16417))
loop_1 = loop_1.lineTo(0.25101, -0.16572)
loop_1 = loop_1.lineTo(0.26254, -0.17178)
loop_1 = loop_1.lineTo(0.28688, -0.19903)
loop_1 = loop_1.lineTo(0.29089, -0.21192)
loop_1 = loop_1.lineTo(0.2909, -0.22217)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_18_interval_0.stl')