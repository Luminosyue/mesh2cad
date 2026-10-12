import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.43191), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34641, -0.26)
loop_1 = loop_1.lineTo(0.40126, -0.25968)
loop_1 = loop_1.lineTo(0.40098, -0.05227)
loop_1 = loop_1.lineTo(0.39968, -0.06725)
loop_1 = loop_1.threePointArc((0.39657, -0.08617), (0.39308, -0.10567))
loop_1 = loop_1.lineTo(0.38497, -0.14315)
loop_1 = loop_1.threePointArc((0.38116, -0.15755), (0.37699, -0.17232))
loop_1 = loop_1.threePointArc((0.3745, -0.18097), (0.37165, -0.18972))
loop_1 = loop_1.lineTo(0.36297, -0.21708)
loop_1 = loop_1.lineTo(0.35009, -0.25248)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_92_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_92_interval_0.stl')