import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01507, -0.4615, -0.21112), normal=(0.00016, -0.00325, 0.99999), xDir=(-0.0, 0.99999, 0.00325))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.01625, -0.57231)
loop_1 = loop_1.lineTo(1.08441, -0.57231)
loop_1 = loop_1.lineTo(1.0844, -0.48046)
loop_1 = loop_1.lineTo(1.05613, -0.52322)
loop_1 = loop_1.threePointArc((1.04996, -0.53099), (1.04723, -0.53459))
loop_1 = loop_1.threePointArc((1.04029, -0.54285), (1.03453, -0.54995))
loop_1 = loop_1.lineTo(1.01712, -0.57124)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_40_interval_0.stl')