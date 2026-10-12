import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.89966, 0.02546, -0.14831), normal=(-0.99919, 0.0005, 0.04016), xDir=(0.00051, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23315, -0.57633)
loop_1 = loop_1.lineTo(-0.71044, -0.57749)
loop_1 = loop_1.lineTo(-0.68106, -0.5829)
loop_1 = loop_1.lineTo(-0.61937, -0.5846)
loop_1 = loop_1.lineTo(-0.55768, -0.58443)
loop_1 = loop_1.lineTo(-0.496, -0.58518)
loop_1 = loop_1.threePointArc((-0.4555, -0.58498), (-0.42533, -0.58474))
loop_1 = loop_1.lineTo(-0.37262, -0.58703)
loop_1 = loop_1.lineTo(-0.31953, -0.58435)
loop_1 = loop_1.threePointArc((-0.25051, -0.58443), (-0.18757, -0.58572))
loop_1 = loop_1.threePointArc((-0.11465, -0.5834), (-0.04799, -0.58267))
loop_1 = loop_1.lineTo(0.00182, -0.58008)
loop_1 = loop_1.lineTo(0.06453, -0.58111)
loop_1 = loop_1.threePointArc((0.12712, -0.57956), (0.18255, -0.57952))
loop_1 = loop_1.lineTo(0.22299, -0.57694)
loop_1 = loop_1.lineTo(0.23315, -0.57633)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_44_interval_0.stl')