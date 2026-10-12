import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50164, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.79746, 0.52064)
loop_1 = loop_1.lineTo(-0.81029, 0.45572)
loop_1 = loop_1.threePointArc((-0.81339, 0.40024), (-0.81521, 0.3474))
loop_1 = loop_1.threePointArc((-0.81508, 0.31322), (-0.81591, 0.27814))
loop_1 = loop_1.lineTo(-0.81655, 0.19137)
loop_1 = loop_1.lineTo(-0.81482, 0.14564)
loop_1 = loop_1.threePointArc((-0.80925, 0.12091), (-0.80425, 0.0955))
loop_1 = loop_1.threePointArc((-0.79298, 0.07235), (-0.78171, 0.05093))
loop_1 = loop_1.threePointArc((-0.7548, 0.01603), (-0.73257, -0.00806))
loop_1 = loop_1.lineTo(-0.74727, -0.06043)
loop_1 = loop_1.lineTo(-0.76139, -0.06843)
loop_1 = loop_1.lineTo(-0.79895, -0.09788)
loop_1 = loop_1.threePointArc((-0.805, -0.10465), (-0.81169, -0.11062))
loop_1 = loop_1.lineTo(-0.82065, -0.15617)
loop_1 = loop_1.lineTo(-0.81913, 0.52064)
loop_1 = loop_1.lineTo(-0.7978, 0.52064)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_64_interval_0.stl')