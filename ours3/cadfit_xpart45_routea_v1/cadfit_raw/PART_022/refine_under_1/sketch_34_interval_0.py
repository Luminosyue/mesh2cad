import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8836, -0.18689, 0.03318), normal=(0.99097, 0.13358, 0.01143), xDir=(0.13359, -0.99104, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29381, -0.22649)
loop_1 = loop_1.lineTo(-0.30662, 0.18354)
loop_1 = loop_1.lineTo(0.3061, 0.18354)
loop_1 = loop_1.lineTo(0.31885, -0.22649)
loop_1 = loop_1.lineTo(-0.29321, -0.22649)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.78)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_34_interval_0.stl')