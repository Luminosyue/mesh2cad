import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.25), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78887, 0.51487)
loop_1 = loop_1.lineTo(0.73233, 0.51844)
loop_1 = loop_1.threePointArc((0.63051, 0.6357), (0.51594, 0.72947))
loop_1 = loop_1.threePointArc((0.38718, 0.80653), (0.25561, 0.86271))
loop_1 = loop_1.lineTo(0.21611, 0.87701)
loop_1 = loop_1.threePointArc((0.18934, 0.88339), (0.16442, 0.88807))
loop_1 = loop_1.threePointArc((0.06809, 0.89996), (-0.02363, 0.90855))
loop_1 = loop_1.threePointArc((-0.14735, 0.89934), (-0.26414, 0.8825))
loop_1 = loop_1.threePointArc((-0.38877, 0.83445), (-0.5036, 0.78005))
loop_1 = loop_1.threePointArc((-0.53415, 0.75875), (-0.56206, 0.73831))
loop_1 = loop_1.threePointArc((-0.63817, 0.67452), (-0.70668, 0.60974))
loop_1 = loop_1.threePointArc((-0.75121, 0.56291), (-0.7887, 0.5148))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_68_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_68_interval_0.stl')