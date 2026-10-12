import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52271), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48, -0.88253)
loop_1 = loop_1.lineTo(-0.47945, -0.9939)
loop_1 = loop_1.lineTo(-0.13626, -0.99341)
loop_1 = loop_1.lineTo(-0.19392, -0.98509)
loop_1 = loop_1.lineTo(-0.24611, -0.97322)
loop_1 = loop_1.lineTo(-0.29989, -0.95719)
loop_1 = loop_1.lineTo(-0.35914, -0.9367)
loop_1 = loop_1.threePointArc((-0.38061, -0.92881), (-0.40246, -0.92005))
loop_1 = loop_1.lineTo(-0.44516, -0.90014)
loop_1 = loop_1.threePointArc((-0.45324, -0.89644), (-0.46116, -0.8922))
loop_1 = loop_1.lineTo(-0.47976, -0.88266)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_81_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_81_interval_0.stl')