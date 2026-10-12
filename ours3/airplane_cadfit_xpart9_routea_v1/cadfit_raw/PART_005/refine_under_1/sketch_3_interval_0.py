import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14136, -0.01672, 0.00933), normal=(-0.99992, 0.0086, 0.00942), xDir=(0.0086, 0.99996, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97957, 0.15505)
loop_1 = loop_1.lineTo(0.94034, 0.12104)
loop_1 = loop_1.lineTo(0.67615, 0.12104)
loop_1 = loop_1.lineTo(0.68887, 0.12389)
loop_1 = loop_1.lineTo(0.70172, 0.12703)
loop_1 = loop_1.lineTo(0.72643, 0.13238)
loop_1 = loop_1.threePointArc((0.73791, 0.1345), (0.74991, 0.13643))
loop_1 = loop_1.lineTo(0.77825, 0.14112)
loop_1 = loop_1.lineTo(0.79092, 0.1439)
loop_1 = loop_1.lineTo(0.80368, 0.14622)
loop_1 = loop_1.lineTo(0.81534, 0.14866)
loop_1 = loop_1.lineTo(0.82866, 0.15182)
loop_1 = loop_1.lineTo(0.85058, 0.15566)
loop_1 = loop_1.lineTo(0.97957, 0.15505)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_3_interval_0.stl')