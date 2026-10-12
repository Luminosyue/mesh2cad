import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.45571, -0.84151, 0.03477), normal=(-0.45204, 0.892, -0.00016), xDir=(0.892, 0.45204, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30055, 0.19043)
loop_1 = loop_1.lineTo(0.21346, 0.19043)
loop_1 = loop_1.lineTo(0.2018, -0.19957)
loop_1 = loop_1.lineTo(-0.27658, -0.19957)
loop_1 = loop_1.lineTo(-0.29451, 0.06477)
loop_1 = loop_1.lineTo(-0.30012, 0.18166)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_22_interval_0.stl')