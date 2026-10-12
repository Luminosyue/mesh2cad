import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.9838, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.54863, 0.42294)
loop_1 = loop_1.threePointArc((-0.56543, 0.3964), (-0.57917, 0.36956))
loop_1 = loop_1.lineTo(-0.6141, 0.28774)
loop_1 = loop_1.threePointArc((-0.63234, 0.22563), (-0.64117, 0.16476))
loop_1 = loop_1.threePointArc((-0.65006, 0.06786), (-0.64538, -0.02477))
loop_1 = loop_1.lineTo(-0.64436, -0.00284)
loop_1 = loop_1.threePointArc((-0.64248, -0.02058), (-0.6394, -0.03676))
loop_1 = loop_1.threePointArc((-0.63388, -0.0717), (-0.62655, -0.10419))
loop_1 = loop_1.lineTo(-0.60868, -0.15841)
loop_1 = loop_1.lineTo(-0.17545, 0.62375)
loop_1 = loop_1.threePointArc((-0.23787, 0.61513), (-0.2958, 0.60028))
loop_1 = loop_1.threePointArc((-0.33886, 0.59338), (-0.37847, 0.58224))
loop_1 = loop_1.threePointArc((-0.45349, 0.52713), (-0.51463, 0.46309))
loop_1 = loop_1.threePointArc((-0.53314, 0.44315), (-0.54862, 0.42294))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_52_interval_0.stl')