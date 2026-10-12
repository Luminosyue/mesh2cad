import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26133, 0.00144)
loop_1 = loop_1.threePointArc((-0.25094, -0.01202), (-0.24641, -0.01595))
loop_1 = loop_1.lineTo(-0.23621, -0.01942)
loop_1 = loop_1.lineTo(-0.207, 0.06406)
loop_1 = loop_1.threePointArc((-0.22247, 0.06418), (-0.23023, 0.06349))
loop_1 = loop_1.threePointArc((-0.23817, 0.06106), (-0.2452, 0.05892))
loop_1 = loop_1.lineTo(-0.25549, 0.04886)
loop_1 = loop_1.threePointArc((-0.26454, 0.0342), (-0.26662, 0.0268))
loop_1 = loop_1.lineTo(-0.26133, 0.00144)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_15_interval_0.stl')