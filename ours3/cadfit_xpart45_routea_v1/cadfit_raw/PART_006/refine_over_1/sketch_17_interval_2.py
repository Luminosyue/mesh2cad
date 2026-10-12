import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76335, 0.4772, -0.01325), normal=(0.84361, 0.53695, 0.00035), xDir=(0.53695, -0.84361, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.32147, -0.35371)
loop_1 = loop_1.lineTo(-0.32164, -0.54261)
loop_1 = loop_1.lineTo(-0.28093, -0.54261)
loop_1 = loop_1.lineTo(-0.31204, -0.50227)
loop_1 = loop_1.threePointArc((-0.3166, -0.49483), (-0.32011, -0.48934))
loop_1 = loop_1.lineTo(-0.32007, -0.44611)
loop_1 = loop_1.lineTo(-0.3203, -0.43514)
loop_1 = loop_1.lineTo(-0.31978, -0.39442)
loop_1 = loop_1.threePointArc((-0.32034, -0.37814), (-0.32101, -0.3647))
loop_1 = loop_1.lineTo(-0.32147, -0.35371)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_17_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_17_interval_2.stl')