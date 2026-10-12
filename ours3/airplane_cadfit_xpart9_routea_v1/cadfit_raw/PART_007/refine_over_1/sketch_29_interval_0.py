import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.0221, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98173, 0.01444)
loop_1 = loop_1.lineTo(0.96761, -0.00758)
loop_1 = loop_1.threePointArc((0.96281, -0.01312), (0.95709, -0.01757))
loop_1 = loop_1.lineTo(0.94329, -0.02838)
loop_1 = loop_1.threePointArc((0.93321, -0.0338), (0.92265, -0.03846))
loop_1 = loop_1.lineTo(0.90023, -0.04067)
loop_1 = loop_1.threePointArc((0.85591, -0.04194), (0.81376, -0.04418))
loop_1 = loop_1.threePointArc((0.7931, -0.04435), (0.77197, -0.04403))
loop_1 = loop_1.threePointArc((0.75148, -0.04421), (0.73054, -0.04339))
loop_1 = loop_1.threePointArc((0.72103, -0.0423), (0.71154, -0.04096))
loop_1 = loop_1.lineTo(0.69097, -0.03709)
loop_1 = loop_1.lineTo(0.67008, -0.03498)
loop_1 = loop_1.threePointArc((0.63438, -0.03439), (0.60045, -0.03453))
loop_1 = loop_1.threePointArc((0.56059, -0.03473), (0.51946, -0.03444))
loop_1 = loop_1.threePointArc((0.49912, -0.03498), (0.47832, -0.03484))
loop_1 = loop_1.lineTo(0.97647, -0.05905)
loop_1 = loop_1.threePointArc((0.97922, -0.02157), (0.98171, 0.01407))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_29_interval_0.stl')