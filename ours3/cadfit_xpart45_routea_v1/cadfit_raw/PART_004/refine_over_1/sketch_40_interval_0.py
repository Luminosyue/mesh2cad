import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.80108), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10432, -0.38827)
loop_1 = loop_1.lineTo(0.13028, -0.37844)
loop_1 = loop_1.lineTo(0.13, -0.41437)
loop_1 = loop_1.lineTo(-0.24916, -0.41361)
loop_1 = loop_1.lineTo(0.09284, -0.39205)
loop_1 = loop_1.lineTo(0.07764, -0.39722)
loop_1 = loop_1.threePointArc((0.09131, -0.39285), (0.10406, -0.38838))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.41)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_40_interval_0.stl')