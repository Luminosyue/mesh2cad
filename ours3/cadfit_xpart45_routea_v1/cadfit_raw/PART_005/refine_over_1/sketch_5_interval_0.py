import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04402, -0.19485, 0.55959), normal=(-0.00136, -0.00047, -1.0), xDir=(0.0, -1.0, 0.00047))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.61536, -0.91011)
loop_1 = loop_1.lineTo(-0.61536, -0.8046)
loop_1 = loop_1.lineTo(-0.59718, -0.81724)
loop_1 = loop_1.lineTo(-0.57053, -0.82716)
loop_1 = loop_1.lineTo(-0.54593, -0.8383)
loop_1 = loop_1.lineTo(-0.51869, -0.84701)
loop_1 = loop_1.lineTo(-0.49982, -0.85425)
loop_1 = loop_1.lineTo(-0.47198, -0.86421)
loop_1 = loop_1.lineTo(-0.44226, -0.87483)
loop_1 = loop_1.lineTo(-0.41503, -0.8796)
loop_1 = loop_1.lineTo(-0.39042, -0.88591)
loop_1 = loop_1.threePointArc((-0.36266, -0.89063), (-0.3386, -0.89549))
loop_1 = loop_1.threePointArc((-0.31086, -0.89891), (-0.28676, -0.90236))
loop_1 = loop_1.threePointArc((-0.25904, -0.90562), (-0.23492, -0.90881))
loop_1 = loop_1.threePointArc((-0.21852, -0.90956), (-0.20542, -0.91023))
loop_1 = loop_1.lineTo(-0.61063, -0.91011)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_5_interval_0.stl')