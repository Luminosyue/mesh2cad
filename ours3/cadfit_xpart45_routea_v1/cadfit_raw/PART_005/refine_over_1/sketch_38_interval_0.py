import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.93142, -0.12367, 0.03909), normal=(0.99528, 0.09704, 0.00149), xDir=(0.09704, -0.99528, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30483, -0.37932)
loop_1 = loop_1.lineTo(0.30738, -0.32576)
loop_1 = loop_1.lineTo(0.30565, -0.27486)
loop_1 = loop_1.lineTo(0.31203, -0.22382)
loop_1 = loop_1.lineTo(0.31437, -0.16841)
loop_1 = loop_1.lineTo(0.31729, -0.12015)
loop_1 = loop_1.lineTo(0.31441, -0.49107)
loop_1 = loop_1.lineTo(0.26525, -0.49107)
loop_1 = loop_1.lineTo(0.28618, -0.47926)
loop_1 = loop_1.threePointArc((0.29468, -0.45476), (0.3026, -0.43116))
loop_1 = loop_1.lineTo(0.30473, -0.38115)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_38_interval_0.stl')