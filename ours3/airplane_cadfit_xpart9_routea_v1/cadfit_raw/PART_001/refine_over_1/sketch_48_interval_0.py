import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01673, 0.37919, -0.20879), normal=(0.0, 0.73822, 0.67456), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86644, -0.24124)
loop_1 = loop_1.threePointArc((-0.87881, -0.24185), (-0.89171, -0.242))
loop_1 = loop_1.lineTo(-0.9062, -0.25767)
loop_1 = loop_1.lineTo(-0.92043, -0.28862)
loop_1 = loop_1.lineTo(-0.93146, -0.31068)
loop_1 = loop_1.lineTo(-0.93587, -0.32504)
loop_1 = loop_1.lineTo(-0.4531, -0.32504)
loop_1 = loop_1.lineTo(-0.60584, -0.29526)
loop_1 = loop_1.lineTo(-0.67444, -0.28013)
loop_1 = loop_1.lineTo(-0.76825, -0.25727)
loop_1 = loop_1.threePointArc((-0.80161, -0.25076), (-0.83117, -0.24597))
loop_1 = loop_1.lineTo(-0.86216, -0.24181)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_48_interval_0.stl')