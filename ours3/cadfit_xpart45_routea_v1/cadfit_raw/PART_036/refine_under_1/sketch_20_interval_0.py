import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32536, -0.03224, -0.24188), normal=(-0.03591, 0.70778, 0.70552), xDir=(0.99872, 0.05067, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.27307, -0.03647)
loop_1 = loop_1.lineTo(1.30113, -0.0358)
loop_1 = loop_1.lineTo(1.30227, -0.04695)
loop_1 = loop_1.threePointArc((1.30197, -0.05668), (1.30162, -0.06681))
loop_1 = loop_1.lineTo(1.30108, -0.08225)
loop_1 = loop_1.lineTo(1.30021, -0.10717)
loop_1 = loop_1.lineTo(1.2885, -0.11888)
loop_1 = loop_1.lineTo(1.25524, -0.10554)
loop_1 = loop_1.lineTo(1.25556, -0.08739)
loop_1 = loop_1.lineTo(1.25508, -0.03577)
loop_1 = loop_1.lineTo(1.2689, -0.03575)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_20_interval_0.stl')