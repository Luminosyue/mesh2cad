import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.11825, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3621, 0.25883)
loop_1 = loop_1.threePointArc((0.40509, 0.25468), (0.44641, 0.25122))
loop_1 = loop_1.lineTo(-0.18359, 0.10121)
loop_1 = loop_1.lineTo(-0.07123, 0.13122)
loop_1 = loop_1.threePointArc((-0.05056, 0.13704), (-0.03131, 0.14293))
loop_1 = loop_1.threePointArc((0.00148, 0.15408), (0.03555, 0.16435))
loop_1 = loop_1.lineTo(0.07499, 0.17971)
loop_1 = loop_1.threePointArc((0.10976, 0.1965), (0.14586, 0.21309))
loop_1 = loop_1.lineTo(0.14875, 0.22561)
loop_1 = loop_1.lineTo(0.15041, 0.24832)
loop_1 = loop_1.threePointArc((0.1373, 0.25261), (0.12447, 0.25792))
loop_1 = loop_1.threePointArc((0.15447, 0.25146), (0.18401, 0.24072))
loop_1 = loop_1.threePointArc((0.20402, 0.23792), (0.22371, 0.23265))
loop_1 = loop_1.lineTo(0.23983, 0.23527)
loop_1 = loop_1.threePointArc((0.2631, 0.23356), (0.28467, 0.23758))
loop_1 = loop_1.threePointArc((0.30659, 0.24893), (0.33019, 0.25772))
loop_1 = loop_1.threePointArc((0.34647, 0.25682), (0.36143, 0.25867))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_51_interval_0.stl')