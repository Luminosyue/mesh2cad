import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.78191), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32489, 0.24997)
loop_1 = loop_1.threePointArc((0.33183, 0.23452), (0.33865, 0.21825))
loop_1 = loop_1.lineTo(0.34978, 0.18729)
loop_1 = loop_1.lineTo(0.36182, 0.1506)
loop_1 = loop_1.lineTo(0.37306, 0.11377)
loop_1 = loop_1.lineTo(0.38295, 0.08037)
loop_1 = loop_1.lineTo(0.39465, 0.04344)
loop_1 = loop_1.threePointArc((0.39661, 0.03354), (0.39811, 0.02335))
loop_1 = loop_1.lineTo(0.40058, 0.00679)
loop_1 = loop_1.lineTo(0.40066, 0.25)
loop_1 = loop_1.lineTo(0.32515, 0.25)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_91_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_91_interval_0.stl')