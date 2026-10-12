import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94555, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56896, 0.04636)
loop_1 = loop_1.lineTo(-0.56883, -0.00392)
loop_1 = loop_1.lineTo(-0.50513, -0.00378)
loop_1 = loop_1.threePointArc((-0.50939, 0.00707), (-0.51363, 0.00936))
loop_1 = loop_1.threePointArc((-0.5218, 0.01356), (-0.5296, 0.01752))
loop_1 = loop_1.threePointArc((-0.53541, 0.02038), (-0.54097, 0.023))
loop_1 = loop_1.lineTo(-0.56232, 0.03864)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.92)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_57_interval_0.stl')