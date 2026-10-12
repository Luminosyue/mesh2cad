import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.63792, -0.04175, -0.02476), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.63703, 0.2923)
loop_1 = loop_1.lineTo(0.63924, 0.25082)
loop_1 = loop_1.lineTo(0.6292, 0.25661)
loop_1 = loop_1.lineTo(0.61107, 0.26396)
loop_1 = loop_1.lineTo(0.5821, 0.27003)
loop_1 = loop_1.lineTo(0.55313, 0.27035)
loop_1 = loop_1.lineTo(0.53396, 0.27321)
loop_1 = loop_1.lineTo(0.50499, 0.26782)
loop_1 = loop_1.lineTo(0.48582, 0.26538)
loop_1 = loop_1.lineTo(0.45684, 0.26392)
loop_1 = loop_1.lineTo(0.43767, 0.26091)
loop_1 = loop_1.threePointArc((0.4083, 0.2629), (0.3847, 0.26379))
loop_1 = loop_1.threePointArc((0.36102, 0.26506), (0.34139, 0.2662))
loop_1 = loop_1.threePointArc((0.30352, 0.26573), (0.26911, 0.26651))
loop_1 = loop_1.lineTo(0.20655, 0.26612)
loop_1 = loop_1.lineTo(0.16402, 0.26636)
loop_1 = loop_1.lineTo(0.63323, 0.29209)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_10_interval_0.stl')