import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02527, 0.10851, 0.12253), normal=(-0.09231, -8e-05, -0.99573), xDir=(0.0, -1.0, 8e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.81694, -0.00285)
loop_1 = loop_1.lineTo(0.81649, 0.00719)
loop_1 = loop_1.threePointArc((0.81702, 0.01431), (0.81754, 0.02076))
loop_1 = loop_1.threePointArc((0.82049, 0.03272), (0.82192, 0.03748))
loop_1 = loop_1.lineTo(0.82883, 0.04857)
loop_1 = loop_1.lineTo(0.84441, 0.04736)
loop_1 = loop_1.lineTo(0.8537, 0.02615)
loop_1 = loop_1.lineTo(0.85623, 0.01554)
loop_1 = loop_1.lineTo(0.85903, -0.00448)
loop_1 = loop_1.threePointArc((0.85377, -0.00943), (0.84886, -0.01384))
loop_1 = loop_1.lineTo(0.81694, -0.00285)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_13_interval_0.stl')