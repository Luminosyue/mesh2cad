import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94242, -0.05958, 0.08079), normal=(0.99961, -0.00128, 0.02794), xDir=(-0.00128, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78199, -0.3127)
loop_1 = loop_1.lineTo(-0.78202, 0.44604)
loop_1 = loop_1.lineTo(0.66798, 0.44579)
loop_1 = loop_1.lineTo(0.66801, -0.3096)
loop_1 = loop_1.lineTo(-0.76001, -0.31265)
loop_1 = loop_1.lineTo(-0.78199, -0.3127)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_42_interval_0.stl')