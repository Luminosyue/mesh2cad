import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14164, -0.22282, -0.16338), normal=(0.56435, -0.82553, 0.00027), xDir=(-0.82553, -0.56435, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23713, 0.64516)
loop_1 = loop_1.lineTo(0.23783, -1.1424)
loop_1 = loop_1.lineTo(0.25069, -1.13091)
loop_1 = loop_1.threePointArc((0.26256, -1.11319), (0.26436, -1.1021))
loop_1 = loop_1.lineTo(0.26641, -1.09097)
loop_1 = loop_1.lineTo(0.26825, -1.0785)
loop_1 = loop_1.lineTo(0.26207, -1.04472)
loop_1 = loop_1.lineTo(0.25308, -1.01003)
loop_1 = loop_1.lineTo(0.25326, -0.99828)
loop_1 = loop_1.threePointArc((0.25367, -0.94363), (0.25585, -0.88674))
loop_1 = loop_1.threePointArc((0.25517, -0.11547), (0.25334, 0.62216))
loop_1 = loop_1.lineTo(0.24118, 0.64123)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_18_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_18_interval_1.stl')