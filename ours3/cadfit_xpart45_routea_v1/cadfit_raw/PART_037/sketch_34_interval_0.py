import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.16308), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05301, -0.3936)
loop_1 = loop_1.threePointArc((-0.05256, -0.40017), (-0.05225, -0.40703))
loop_1 = loop_1.lineTo(0.016, -0.44356)
loop_1 = loop_1.threePointArc((0.02287, -0.44233), (0.02943, -0.44102))
loop_1 = loop_1.lineTo(0.04312, -0.43441)
loop_1 = loop_1.threePointArc((0.04951, -0.42743), (0.05329, -0.42274))
loop_1 = loop_1.lineTo(0.0543, -0.40078)
loop_1 = loop_1.threePointArc((0.04984, -0.39363), (0.04532, -0.38691))
loop_1 = loop_1.lineTo(0.03526, -0.37942)
loop_1 = loop_1.threePointArc((0.02903, -0.37599), (0.02274, -0.37209))
loop_1 = loop_1.lineTo(0.00979, -0.36585)
loop_1 = loop_1.lineTo(-0.01237, -0.36275)
loop_1 = loop_1.threePointArc((-0.01845, -0.36369), (-0.02423, -0.36486))
loop_1 = loop_1.lineTo(-0.03941, -0.37285)
loop_1 = loop_1.lineTo(-0.05033, -0.37975)
loop_1 = loop_1.lineTo(-0.053, -0.3935)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_34_interval_0.stl')