import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40778, -0.19751, -0.17125), normal=(-0.03996, 0.99725, -0.06236), xDir=(0.9992, 0.04003, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.68775, -0.05018)
loop_1 = loop_1.lineTo(-0.64, -0.05035)
loop_1 = loop_1.lineTo(-0.6362, 0.02309)
loop_1 = loop_1.lineTo(-0.66288, 0.01952)
loop_1 = loop_1.lineTo(-0.67399, 0.01634)
loop_1 = loop_1.lineTo(-0.68623, 0.00787)
loop_1 = loop_1.threePointArc((-0.68974, -0.01801), (-0.68945, -0.03925))
loop_1 = loop_1.lineTo(-0.68775, -0.05018)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_24_interval_0.stl')