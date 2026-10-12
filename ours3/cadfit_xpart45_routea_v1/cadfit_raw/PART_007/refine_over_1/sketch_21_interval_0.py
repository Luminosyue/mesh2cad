import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.57986, 0.24629, 0.54427), normal=(0.51906, 0.0, 0.85474), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.22656, 0.04315)
loop_1 = loop_1.lineTo(1.22948, 0.02937)
loop_1 = loop_1.lineTo(1.22826, 0.00667)
loop_1 = loop_1.lineTo(1.21255, -0.04838)
loop_1 = loop_1.threePointArc((1.19179, -0.0675), (1.17213, -0.0854))
loop_1 = loop_1.lineTo(1.13199, -0.09445)
loop_1 = loop_1.threePointArc((1.08966, -0.09349), (1.05171, -0.09196))
loop_1 = loop_1.lineTo(1.01157, -0.09325)
loop_1 = loop_1.threePointArc((0.95, -0.09371), (0.89115, -0.09304))
loop_1 = loop_1.threePointArc((0.84361, -0.09405), (0.79943, -0.09379))
loop_1 = loop_1.lineTo(0.77073, -0.09372)
loop_1 = loop_1.lineTo(0.74467, -0.0947)
loop_1 = loop_1.lineTo(1.23629, -0.0947)
loop_1 = loop_1.lineTo(1.23629, 0.03782)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_21_interval_0.stl')