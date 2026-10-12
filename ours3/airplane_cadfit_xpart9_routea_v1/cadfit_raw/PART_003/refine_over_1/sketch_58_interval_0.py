import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.16517), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20703, 0.72141)
loop_1 = loop_1.lineTo(0.25589, 0.8737)
loop_1 = loop_1.lineTo(0.22548, 0.905)
loop_1 = loop_1.lineTo(0.22724, 0.88505)
loop_1 = loop_1.lineTo(0.22575, 0.84903)
loop_1 = loop_1.lineTo(0.22269, 0.81443)
loop_1 = loop_1.threePointArc((0.21894, 0.78725), (0.21554, 0.76852))
loop_1 = loop_1.lineTo(0.21079, 0.74295)
loop_1 = loop_1.lineTo(0.20706, 0.72155)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_58_interval_0.stl')