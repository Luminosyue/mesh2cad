import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.40004, 0.29666, -0.18742), normal=(-0.00045, 0.01717, 0.99985), xDir=(0.0, 0.99985, -0.01717))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.295, 0.93251)
loop_1 = loop_1.lineTo(0.23682, 0.93251)
loop_1 = loop_1.threePointArc((0.24367, 0.92386), (0.24959, 0.91642))
loop_1 = loop_1.lineTo(0.27554, 0.87623)
loop_1 = loop_1.threePointArc((0.28456, 0.86143), (0.29286, 0.84692))
loop_1 = loop_1.lineTo(0.29547, 0.93251)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_4_interval_0.stl')