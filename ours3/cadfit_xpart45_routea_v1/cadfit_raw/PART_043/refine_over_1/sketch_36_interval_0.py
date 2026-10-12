import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.90659, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3258, 0.02921)
loop_1 = loop_1.lineTo(-0.32558, -0.00043)
loop_1 = loop_1.threePointArc((-0.32029, -0.00527), (-0.31503, -0.00922))
loop_1 = loop_1.threePointArc((-0.30433, -0.0236), (-0.29711, -0.03524))
loop_1 = loop_1.threePointArc((-0.28596, -0.05314), (-0.2754, -0.07203))
loop_1 = loop_1.threePointArc((-0.26062, -0.09754), (-0.24613, -0.1215))
loop_1 = loop_1.lineTo(-0.22933, -0.15304)
loop_1 = loop_1.threePointArc((-0.2195, -0.17243), (-0.21013, -0.19268))
loop_1 = loop_1.lineTo(-0.18517, -0.24554)
loop_1 = loop_1.lineTo(-0.16383, -0.27266)
loop_1 = loop_1.lineTo(-0.12905, -0.30376)
loop_1 = loop_1.threePointArc((-0.11345, -0.31662), (-0.09842, -0.32842))
loop_1 = loop_1.lineTo(-0.08438, -0.3385)
loop_1 = loop_1.lineTo(-0.29469, 0.046)
loop_1 = loop_1.lineTo(-0.32553, 0.02936)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_36_interval_0.stl')