import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.43369, -0.25392, 0.03988), normal=(-0.03396, 0.17229, 0.98446), xDir=(0.0, 0.98503, -0.17239))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26401, -0.04819)
loop_1 = loop_1.lineTo(-0.27895, -0.03606)
loop_1 = loop_1.threePointArc((-0.29416, -0.26475), (-0.30541, -0.47908))
loop_1 = loop_1.lineTo(-0.30703, -0.50694)
loop_1 = loop_1.lineTo(-0.17863, -0.50694)
loop_1 = loop_1.lineTo(-0.22587, -0.24506)
loop_1 = loop_1.lineTo(-0.26327, -0.05202)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_interval_0.stl')