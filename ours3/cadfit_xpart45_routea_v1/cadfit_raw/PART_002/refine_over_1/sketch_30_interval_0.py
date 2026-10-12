import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03241, 0.10968, 0.13009), normal=(0.00036, -0.99292, -0.11878), xDir=(-1.0, -0.00036, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.37192, 0.85147)
loop_1 = loop_1.lineTo(-0.37856, 0.83325)
loop_1 = loop_1.threePointArc((-0.38304, 0.82203), (-0.3867, 0.81264))
loop_1 = loop_1.lineTo(-0.39429, 0.79597)
loop_1 = loop_1.lineTo(-0.40305, 0.75827)
loop_1 = loop_1.lineTo(-0.40384, 0.7448)
loop_1 = loop_1.threePointArc((-0.40652, 0.75885), (-0.40893, 0.7722))
loop_1 = loop_1.lineTo(-0.42236, 0.84497)
loop_1 = loop_1.lineTo(-0.37326, 0.85147)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_30_interval_0.stl')