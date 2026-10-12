import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80557, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.6956, 0.09804)
loop_1 = loop_1.lineTo(-0.70825, -0.00326)
loop_1 = loop_1.lineTo(-0.44327, -0.0361)
loop_1 = loop_1.threePointArc((-0.47163, -0.02877), (-0.49875, -0.02225))
loop_1 = loop_1.threePointArc((-0.51969, -0.01673), (-0.54114, -0.01053))
loop_1 = loop_1.threePointArc((-0.55476, -0.00663), (-0.56861, -0.00231))
loop_1 = loop_1.lineTo(-0.5919, 0.00415)
loop_1 = loop_1.lineTo(-0.69541, 0.09788)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_25_interval_0.stl')