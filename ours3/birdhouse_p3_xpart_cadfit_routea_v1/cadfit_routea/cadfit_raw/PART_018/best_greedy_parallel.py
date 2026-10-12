import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.96, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18448, 0.30571)
loop_1 = loop_1.lineTo(0.18621, 0.2879)
loop_1 = loop_1.lineTo(0.18572, 0.27234)
loop_1 = loop_1.lineTo(0.17788, 0.25878)
loop_1 = loop_1.lineTo(0.16108, 0.25146)
loop_1 = loop_1.lineTo(0.0942, 0.25135)
loop_1 = loop_1.threePointArc((-0.0175, 0.24966), (-0.12446, 0.24681))
loop_1 = loop_1.lineTo(-0.17321, 0.24642)
loop_1 = loop_1.lineTo(-0.18582, 0.25631)
loop_1 = loop_1.lineTo(-0.1745, 0.273)
loop_1 = loop_1.threePointArc((-0.10111, 0.27406), (-0.03468, 0.27544))
loop_1 = loop_1.threePointArc((0.0183, 0.27601), (0.06888, 0.27733))
loop_1 = loop_1.lineTo(0.13386, 0.27861)
loop_1 = loop_1.lineTo(0.1451, 0.27948)
loop_1 = loop_1.lineTo(0.15665, 0.28979)
loop_1 = loop_1.lineTo(0.15903, 0.30642)
loop_1 = loop_1.threePointArc((0.1698, 0.31021), (0.17806, 0.31126))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.94)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_018/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_018/sketch_14_interval_0.stl')