import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.43988, -0.81907, 0.02967), normal=(-0.46464, 0.88545, -0.00887), xDir=(0.88549, 0.46466, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35893, -0.20503)
loop_1 = loop_1.lineTo(0.29815, -0.20503)
loop_1 = loop_1.lineTo(0.29731, 0.18499)
loop_1 = loop_1.lineTo(-0.3605, 0.18499)
loop_1 = loop_1.lineTo(-0.35897, -0.19444)
loop_1 = loop_1.lineTo(-0.35893, -0.20503)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_18_interval_0.stl')