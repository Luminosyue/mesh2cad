import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.68663, -0.17758, 0.00465), normal=(-0.33791, 0.94111, 0.01131), xDir=(0.94117, 0.33793, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00418, 0.08928)
loop_1 = loop_1.lineTo(-0.01428, 0.08919)
loop_1 = loop_1.lineTo(-0.08487, 0.06361)
loop_1 = loop_1.lineTo(0.06525, -0.07911)
loop_1 = loop_1.lineTo(0.07574, -0.07845)
loop_1 = loop_1.lineTo(0.14168, -0.06908)
loop_1 = loop_1.lineTo(0.13657, -0.0524)
loop_1 = loop_1.lineTo(-0.00418, 0.08928)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_4_interval_0.stl')