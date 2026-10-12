import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64875, -0.62055, -0.00499), normal=(-0.78932, -0.61398, 0.00017), xDir=(-0.61398, 0.78932, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30571, 0.12361)
loop_1 = loop_1.lineTo(-0.31555, -0.18096)
loop_1 = loop_1.threePointArc((-0.31775, -0.15537), (-0.31981, -0.13425))
loop_1 = loop_1.lineTo(-0.32014, -0.10525)
loop_1 = loop_1.lineTo(-0.32187, -0.08753)
loop_1 = loop_1.lineTo(-0.32317, -0.0604)
loop_1 = loop_1.lineTo(-0.32211, -0.04082)
loop_1 = loop_1.lineTo(-0.32441, -0.01444)
loop_1 = loop_1.lineTo(-0.32475, 0.00589)
loop_1 = loop_1.threePointArc((-0.32357, 0.03149), (-0.32283, 0.0526))
loop_1 = loop_1.threePointArc((-0.32114, 0.07725), (-0.31925, 0.09931))
loop_1 = loop_1.lineTo(-0.31415, 0.13962)
loop_1 = loop_1.lineTo(-0.29508, 0.13962)
loop_1 = loop_1.lineTo(-0.3049, 0.12533)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_20_interval_0.stl')