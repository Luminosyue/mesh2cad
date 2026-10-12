import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26969, -0.33901, 0.12381), normal=(0.0, -0.30739, 0.95158), xDir=(-0.0, 0.95158, 0.30739))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1537, -0.77866)
loop_1 = loop_1.lineTo(-0.15359, -0.86206)
loop_1 = loop_1.lineTo(-0.14735, -0.82425)
loop_1 = loop_1.lineTo(-0.14365, -0.80909)
loop_1 = loop_1.lineTo(-0.14223, -0.7977)
loop_1 = loop_1.lineTo(-0.14018, -0.77729)
loop_1 = loop_1.lineTo(-0.13667, -0.76499)
loop_1 = loop_1.lineTo(-0.13411, -0.74809)
loop_1 = loop_1.lineTo(-0.13029, -0.73487)
loop_1 = loop_1.lineTo(-0.12666, -0.71605)
loop_1 = loop_1.threePointArc((-0.12413, -0.70513), (-0.12187, -0.69461))
loop_1 = loop_1.threePointArc((-0.1247, -0.70188), (-0.12836, -0.71139))
loop_1 = loop_1.lineTo(-0.13666, -0.73142)
loop_1 = loop_1.lineTo(-0.1537, -0.77866)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_2_interval_0.stl')