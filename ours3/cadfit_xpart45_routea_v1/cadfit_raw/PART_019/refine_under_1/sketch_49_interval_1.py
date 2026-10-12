import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50626, -0.02388, 0.0309), normal=(-1.0, -0.0, -0.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.67403, -0.7284)
loop_1 = loop_1.lineTo(-0.63172, -0.73357)
loop_1 = loop_1.threePointArc((-0.57577, -0.7329), (-0.52742, -0.73326))
loop_1 = loop_1.lineTo(-0.50345, -0.73381)
loop_1 = loop_1.lineTo(-0.48928, -0.73288)
loop_1 = loop_1.lineTo(-0.41907, -0.73314)
loop_1 = loop_1.lineTo(-0.25207, -0.72972)
loop_1 = loop_1.threePointArc((-0.18932, -0.73039), (-0.13823, -0.72978))
loop_1 = loop_1.threePointArc((-0.07061, -0.73019), (-0.01486, -0.7299))
loop_1 = loop_1.lineTo(0.01274, -0.73054)
loop_1 = loop_1.lineTo(0.04683, -0.7301)
loop_1 = loop_1.lineTo(0.0659, -0.72921)
loop_1 = loop_1.threePointArc((0.10094, -0.7299), (0.12758, -0.73061))
loop_1 = loop_1.threePointArc((0.16181, -0.72962), (0.18647, -0.7284))
loop_1 = loop_1.lineTo(-0.66507, -0.7284)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_49_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_49_interval_1.stl')