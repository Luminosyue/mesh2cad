import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.48312, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07244, 0.94726)
loop_1 = loop_1.lineTo(0.08795, 0.96)
loop_1 = loop_1.lineTo(0.08495, -0.95682)
loop_1 = loop_1.lineTo(0.06662, -0.95402)
loop_1 = loop_1.lineTo(0.06602, 0.95031)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_60_interval_0.stl')