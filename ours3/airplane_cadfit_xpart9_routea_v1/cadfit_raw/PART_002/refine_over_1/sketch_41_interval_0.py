import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.21039, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25755, 0.34253)
loop_1 = loop_1.lineTo(-0.06932, 0.19331)
loop_1 = loop_1.threePointArc((0.01014, 0.17452), (0.08708, 0.16261))
loop_1 = loop_1.threePointArc((0.13001, 0.15728), (0.17393, 0.15055))
loop_1 = loop_1.threePointArc((0.22618, 0.1448), (0.27577, 0.13972))
loop_1 = loop_1.lineTo(0.34192, 0.13649)
loop_1 = loop_1.threePointArc((0.37184, 0.13649), (0.39997, 0.13726))
loop_1 = loop_1.lineTo(0.20128, 0.15021)
loop_1 = loop_1.lineTo(0.47236, 0.1409)
loop_1 = loop_1.lineTo(0.50704, 0.14155)
loop_1 = loop_1.lineTo(0.5408, 0.1463)
loop_1 = loop_1.lineTo(0.57466, 0.15406)
loop_1 = loop_1.lineTo(0.60224, 0.16245)
loop_1 = loop_1.lineTo(0.26256, 0.34469)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_41_interval_0.stl')