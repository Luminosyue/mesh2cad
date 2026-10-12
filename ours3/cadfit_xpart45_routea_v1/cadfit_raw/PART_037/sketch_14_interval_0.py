import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.09469, 0.08426, 0.2791), normal=(-0.00112, -0.82059, -0.57152), xDir=(-1.0, 0.00137, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.48037, 0.17321)
loop_1 = loop_1.threePointArc((0.49429, 0.17291), (0.50765, 0.17282))
loop_1 = loop_1.lineTo(0.5213, 0.17281)
loop_1 = loop_1.lineTo(0.53097, 0.11301)
loop_1 = loop_1.threePointArc((0.52663, 0.10654), (0.52266, 0.10019))
loop_1 = loop_1.lineTo(0.50759, 0.08839)
loop_1 = loop_1.threePointArc((0.50067, 0.08682), (0.49395, 0.0853))
loop_1 = loop_1.lineTo(0.4793, 0.0902)
loop_1 = loop_1.lineTo(0.46667, 0.1002)
loop_1 = loop_1.lineTo(0.45685, 0.11322)
loop_1 = loop_1.lineTo(0.44418, 0.14697)
loop_1 = loop_1.threePointArc((0.44747, 0.1549), (0.45104, 0.16309))
loop_1 = loop_1.lineTo(0.46546, 0.17139)
loop_1 = loop_1.lineTo(0.48037, 0.17321)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_14_interval_0.stl')