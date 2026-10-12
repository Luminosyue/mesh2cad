import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.42229), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3337, 0.97837)
loop_1 = loop_1.threePointArc((-0.3137, 0.97706), (-0.2945, 0.97607))
loop_1 = loop_1.threePointArc((-0.27873, 0.97229), (-0.26371, 0.96917))
loop_1 = loop_1.lineTo(-0.24704, 0.96039)
loop_1 = loop_1.threePointArc((-0.23522, 0.95373), (-0.22394, 0.94758))
loop_1 = loop_1.lineTo(-0.1989, 0.92007)
loop_1 = loop_1.lineTo(-0.18547, 0.90337)
loop_1 = loop_1.lineTo(-0.15676, 0.88551)
loop_1 = loop_1.lineTo(-0.12086, 0.8817)
loop_1 = loop_1.threePointArc((-0.11532, 0.88158), (-0.1102, 0.88165))
loop_1 = loop_1.lineTo(-0.11076, 0.97852)
loop_1 = loop_1.lineTo(-0.33351, 0.97831)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.62)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_47_interval_0.stl')