import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02775, 0.15329, 0.10056), normal=(-0.7264, 0.00158, -0.68727), xDir=(0.00218, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.9054, 0.04188)
loop_1 = loop_1.threePointArc((-0.89938, 0.04182), (-0.8936, 0.04181))
loop_1 = loop_1.lineTo(-0.78591, 0.00957)
loop_1 = loop_1.threePointArc((-0.78516, 0.00438), (-0.78441, -0.0006))
loop_1 = loop_1.lineTo(-0.8079, -0.00697)
loop_1 = loop_1.lineTo(-0.8267, -0.00674)
loop_1 = loop_1.lineTo(-0.8553, -0.0203)
loop_1 = loop_1.lineTo(-0.89418, -0.03188)
loop_1 = loop_1.lineTo(-0.91535, -0.01239)
loop_1 = loop_1.lineTo(-0.92301, 0.00168)
loop_1 = loop_1.lineTo(-0.9054, 0.04188)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_11_interval_0.stl')