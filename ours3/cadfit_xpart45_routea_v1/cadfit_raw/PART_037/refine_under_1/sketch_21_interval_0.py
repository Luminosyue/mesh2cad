import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.79816, -0.21151, -0.05048), normal=(-0.88165, 0.4719, 0.0), xDir=(0.4719, 0.88165, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22888, -0.19944)
loop_1 = loop_1.lineTo(0.22952, -0.14944)
loop_1 = loop_1.lineTo(0.12583, -0.14766)
loop_1 = loop_1.threePointArc((0.11469, -0.13699), (0.10516, -0.13503))
loop_1 = loop_1.threePointArc((0.09418, -0.13302), (0.08401, -0.13165))
loop_1 = loop_1.lineTo(0.06457, -0.12961)
loop_1 = loop_1.threePointArc((0.05854, -0.12905), (0.05273, -0.12876))
loop_1 = loop_1.lineTo(0.04504, -0.14627)
loop_1 = loop_1.lineTo(-0.15552, -0.14286)
loop_1 = loop_1.lineTo(-0.15617, -0.19282)
loop_1 = loop_1.lineTo(0.22644, -0.1994)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.72)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_21_interval_0.stl')