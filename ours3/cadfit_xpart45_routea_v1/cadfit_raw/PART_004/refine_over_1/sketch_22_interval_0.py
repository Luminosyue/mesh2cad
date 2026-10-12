import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40615, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06057, 0.78926)
loop_1 = loop_1.lineTo(-0.07348, 0.7846)
loop_1 = loop_1.lineTo(-0.08789, 0.7751)
loop_1 = loop_1.lineTo(-0.10821, 0.77576)
loop_1 = loop_1.lineTo(-0.1284, 0.78629)
loop_1 = loop_1.lineTo(-0.14307, 0.7811)
loop_1 = loop_1.lineTo(-0.15783, 0.78804)
loop_1 = loop_1.threePointArc((-0.1635, 0.79382), (-0.16913, 0.79998))
loop_1 = loop_1.lineTo(-0.05442, 0.8)
loop_1 = loop_1.lineTo(-0.06057, 0.78926)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.81)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_22_interval_0.stl')