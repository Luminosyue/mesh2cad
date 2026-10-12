import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.46832, 0.44893, 0.43424), normal=(-0.03157, 0.00039, -0.9995), xDir=(0.0, -1.0, -0.00039))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.43831, 0.82707)
loop_1 = loop_1.lineTo(1.43766, 0.8519)
loop_1 = loop_1.lineTo(1.43362, 0.86446)
loop_1 = loop_1.lineTo(1.43208, 0.89199)
loop_1 = loop_1.lineTo(1.42097, 0.92132)
loop_1 = loop_1.lineTo(1.41193, 0.93257)
loop_1 = loop_1.lineTo(1.39499, 0.94285)
loop_1 = loop_1.lineTo(1.43929, 0.94283)
loop_1 = loop_1.lineTo(1.43929, 0.82002)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_4_interval_0.stl')