import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0075, 0.43, 0.07756), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.88675, -0.04999)
loop_1 = loop_1.lineTo(0.88644, 0.22355)
loop_1 = loop_1.lineTo(0.88033, -0.02986)
loop_1 = loop_1.lineTo(0.84325, 0.00891)
loop_1 = loop_1.lineTo(0.81796, 0.02197)
loop_1 = loop_1.lineTo(0.81441, 0.07381)
loop_1 = loop_1.lineTo(0.83992, 0.107)
loop_1 = loop_1.lineTo(0.85315, 0.12564)
loop_1 = loop_1.lineTo(0.87671, 0.17747)
loop_1 = loop_1.lineTo(0.88554, 0.22382)
loop_1 = loop_1.lineTo(0.88675, 0.23567)
loop_1 = loop_1.lineTo(0.88675, -0.0442)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.92)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_19_interval_0.stl')