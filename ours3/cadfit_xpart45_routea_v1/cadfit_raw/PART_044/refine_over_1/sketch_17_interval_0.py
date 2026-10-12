import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.20344, 0.04043, 0.16942), normal=(-0.92575, -0.37811, -0.00386), xDir=(-0.37811, 0.92576, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0189, 1.00823)
loop_1 = loop_1.lineTo(0.03135, 1.00823)
loop_1 = loop_1.threePointArc((0.03218, 0.96741), (0.03373, 0.93138))
loop_1 = loop_1.threePointArc((0.03409, 0.9196), (0.03432, 0.91107))
loop_1 = loop_1.lineTo(0.03749, 0.86076)
loop_1 = loop_1.lineTo(0.03874, 0.84365)
loop_1 = loop_1.lineTo(0.03899, 0.83282)
loop_1 = loop_1.lineTo(0.04051, 0.81235)
loop_1 = loop_1.threePointArc((0.03984, 0.78592), (0.03903, 0.76238))
loop_1 = loop_1.threePointArc((0.03756, 0.73934), (0.03591, 0.7185))
loop_1 = loop_1.threePointArc((0.03225, 0.70445), (0.02944, 0.6937))
loop_1 = loop_1.lineTo(0.02358, 0.67629)
loop_1 = loop_1.lineTo(0.0189, 1.00477)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_17_interval_0.stl')