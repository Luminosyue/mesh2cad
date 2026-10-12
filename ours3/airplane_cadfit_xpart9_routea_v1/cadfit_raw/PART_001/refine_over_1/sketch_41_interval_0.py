import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.48603, -0.01102, 0.10762), normal=(0.0, 0.20198, 0.97939), xDir=(0.0, 0.97939, -0.20198))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11635, 1.37998)
loop_1 = loop_1.lineTo(0.11081, 1.35489)
loop_1 = loop_1.lineTo(0.10635, 1.33054)
loop_1 = loop_1.lineTo(0.0924, 1.33303)
loop_1 = loop_1.lineTo(0.07763, 1.34564)
loop_1 = loop_1.lineTo(0.06279, 1.35006)
loop_1 = loop_1.threePointArc((0.05794, 1.35704), (0.05299, 1.36439))
loop_1 = loop_1.lineTo(0.05017, 1.3752)
loop_1 = loop_1.lineTo(0.03789, 1.38345)
loop_1 = loop_1.lineTo(0.0333, 1.39669)
loop_1 = loop_1.lineTo(0.03132, 1.40954)
loop_1 = loop_1.lineTo(0.03618, 1.42108)
loop_1 = loop_1.lineTo(0.12439, 1.42603)
loop_1 = loop_1.lineTo(0.11635, 1.37998)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_41_interval_0.stl')