import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28243, 0.93369, -0.07385), normal=(0.27454, -0.96158, 0.00016), xDir=(-0.96158, -0.27454, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11462, -0.14607)
loop_1 = loop_1.lineTo(0.18664, 0.01556)
loop_1 = loop_1.lineTo(0.18642, -0.16274)
loop_1 = loop_1.lineTo(0.16515, -0.16098)
loop_1 = loop_1.threePointArc((0.13378, -0.1561), (0.10869, -0.15234))
loop_1 = loop_1.threePointArc((0.07516, -0.14892), (0.04641, -0.14549))
loop_1 = loop_1.lineTo(0.03302, -0.14562)
loop_1 = loop_1.lineTo(-0.01723, -0.14772)
loop_1 = loop_1.lineTo(-0.04516, -0.15143)
loop_1 = loop_1.lineTo(-0.0713, -0.14865)
loop_1 = loop_1.lineTo(-0.1141, -0.14812)
loop_1 = loop_1.lineTo(-0.12537, -0.14915)
loop_1 = loop_1.lineTo(-0.11462, -0.14607)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_4_interval_0.stl')