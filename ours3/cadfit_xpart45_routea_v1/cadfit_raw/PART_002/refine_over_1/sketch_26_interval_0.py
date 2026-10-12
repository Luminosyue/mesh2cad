import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28071, -0.32374, 0.30858), normal=(0.922, 0.3872, -0.00028), xDir=(0.3872, -0.922, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0587, 0.06077)
loop_1 = loop_1.lineTo(0.14108, 0.89586)
loop_1 = loop_1.lineTo(0.14002, -0.19089)
loop_1 = loop_1.lineTo(0.11182, -0.16083)
loop_1 = loop_1.lineTo(0.08921, -0.12432)
loop_1 = loop_1.lineTo(0.07822, -0.0873)
loop_1 = loop_1.lineTo(0.06665, -0.01787)
loop_1 = loop_1.lineTo(0.06169, 0.01457)
loop_1 = loop_1.lineTo(0.06009, 0.03373)
loop_1 = loop_1.lineTo(0.05804, 0.04823)
loop_1 = loop_1.lineTo(0.0587, 0.06077)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_26_interval_0.stl')