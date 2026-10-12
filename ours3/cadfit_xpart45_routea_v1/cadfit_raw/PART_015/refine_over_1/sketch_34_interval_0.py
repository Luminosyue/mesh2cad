import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.80009, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12298, -0.25693)
loop_1 = loop_1.threePointArc((-0.33002, -0.25685), (-0.52878, -0.25848))
loop_1 = loop_1.lineTo(-0.61886, -0.26044)
loop_1 = loop_1.threePointArc((-0.6406, -0.25689), (-0.66187, -0.25188))
loop_1 = loop_1.lineTo(-0.66095, -0.26205)
loop_1 = loop_1.lineTo(0.64576, -0.25975)
loop_1 = loop_1.threePointArc((0.61744, -0.25546), (0.58886, -0.25495))
loop_1 = loop_1.threePointArc((0.55765, -0.2571), (0.52619, -0.2563))
loop_1 = loop_1.threePointArc((0.36364, -0.25736), (0.19957, -0.25662))
loop_1 = loop_1.lineTo(-0.22041, -0.25734)
loop_1 = loop_1.lineTo(-0.24271, -0.25694)
loop_1 = loop_1.lineTo(-0.12401, -0.25674)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_34_interval_0.stl')