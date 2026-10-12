import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.4827, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.90181, -0.02073)
loop_1 = loop_1.lineTo(-0.90453, -0.03252)
loop_1 = loop_1.lineTo(-0.91185, -0.0557)
loop_1 = loop_1.lineTo(-0.9548, -0.0819)
loop_1 = loop_1.lineTo(-0.9743, -0.10764)
loop_1 = loop_1.lineTo(-0.97601, -0.1189)
loop_1 = loop_1.lineTo(-0.97543, 0.14422)
loop_1 = loop_1.lineTo(-0.90843, 0.00886)
loop_1 = loop_1.lineTo(-0.92249, 0.02683)
loop_1 = loop_1.lineTo(-0.90152, -0.01901)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.91)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_78_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_78_interval_0.stl')