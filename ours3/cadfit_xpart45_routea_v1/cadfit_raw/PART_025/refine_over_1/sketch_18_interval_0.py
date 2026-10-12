import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19758, -0.22684, 0.12393), normal=(0.00186, 1.0, -0.00035), xDir=(1.0, -0.00186, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.52812, -0.34318)
loop_1 = loop_1.threePointArc((-0.5118, -0.35157), (-0.49512, -0.36092))
loop_1 = loop_1.lineTo(-0.47705, -0.37042)
loop_1 = loop_1.threePointArc((-0.46678, -0.3767), (-0.45965, -0.3808))
loop_1 = loop_1.threePointArc((-0.43067, -0.39831), (-0.41128, -0.41096))
loop_1 = loop_1.threePointArc((-0.38805, -0.42587), (-0.36806, -0.43958))
loop_1 = loop_1.threePointArc((-0.35316, -0.4491), (-0.3422, -0.4566))
loop_1 = loop_1.lineTo(-0.32431, -0.47113)
loop_1 = loop_1.lineTo(-0.30739, -0.4802)
loop_1 = loop_1.lineTo(-0.29055, -0.47987)
loop_1 = loop_1.threePointArc((-0.26538, -0.4764), (-0.24323, -0.47398))
loop_1 = loop_1.threePointArc((-0.21008, -0.47082), (-0.1773, -0.46902))
loop_1 = loop_1.lineTo(-0.15388, -0.4677)
loop_1 = loop_1.lineTo(-0.51367, -0.34978)
loop_1 = loop_1.lineTo(-0.52812, -0.34318)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_18_interval_0.stl')