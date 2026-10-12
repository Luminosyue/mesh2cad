import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21188), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58631, -0.55731)
loop_1 = loop_1.lineTo(0.63304, -0.55718)
loop_1 = loop_1.lineTo(0.63288, -0.492)
loop_1 = loop_1.lineTo(0.62312, -0.50613)
loop_1 = loop_1.threePointArc((0.60593, -0.53046), (0.59188, -0.54971))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_61_interval_0.stl')