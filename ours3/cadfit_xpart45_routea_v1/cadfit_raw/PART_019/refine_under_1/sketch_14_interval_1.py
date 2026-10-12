import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05072, -0.03649, 0.84054), normal=(-0.10409, -0.00089, 0.99457), xDir=(-0.0, 1.0, 0.00089))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.46218, -0.35014)
loop_1 = loop_1.threePointArc((-0.41815, -0.35382), (-0.37234, -0.35826))
loop_1 = loop_1.lineTo(-0.28452, -0.36167)
loop_1 = loop_1.threePointArc((-0.22747, -0.36479), (-0.18106, -0.36651))
loop_1 = loop_1.lineTo(-0.12715, -0.36547)
loop_1 = loop_1.threePointArc((-0.09231, -0.36749), (-0.06546, -0.36905))
loop_1 = loop_1.threePointArc((-0.03096, -0.3677), (-0.00377, -0.36674))
loop_1 = loop_1.threePointArc((0.03116, -0.36811), (0.05791, -0.3692))
loop_1 = loop_1.threePointArc((0.09201, -0.36659), (0.1196, -0.36498))
loop_1 = loop_1.lineTo(0.13054, -0.36489)
loop_1 = loop_1.threePointArc((0.17958, -0.36521), (0.23064, -0.36683))
loop_1 = loop_1.lineTo(0.24297, -0.36702)
loop_1 = loop_1.threePointArc((0.28692, -0.36362), (0.33275, -0.361))
loop_1 = loop_1.lineTo(0.45146, -0.35169)
loop_1 = loop_1.lineTo(-0.4531, -0.35006)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_14_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_14_interval_1.stl')