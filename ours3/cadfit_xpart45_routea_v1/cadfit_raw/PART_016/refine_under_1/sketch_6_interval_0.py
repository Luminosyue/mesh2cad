import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05834, 0.77186, -0.04849), normal=(-0.00029, -0.99999, -0.0052), xDir=(-1.0, 0.00029, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31881, -0.15658)
loop_1 = loop_1.threePointArc((0.31672, 0.01689), (0.31444, 0.18342))
loop_1 = loop_1.lineTo(-0.28047, 0.18342)
loop_1 = loop_1.lineTo(-0.28426, -0.15658)
loop_1 = loop_1.lineTo(0.30856, -0.15658)
loop_1 = loop_1.lineTo(0.31881, -0.15658)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.66)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_6_interval_0.stl')