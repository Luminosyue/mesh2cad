import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.69513, 0.04481, -0.02316), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.57252, 0.21267)
loop_1 = loop_1.lineTo(0.55098, -0.19733)
loop_1 = loop_1.lineTo(-0.74753, -0.19733)
loop_1 = loop_1.lineTo(-0.73358, 0.21267)
loop_1 = loop_1.lineTo(0.55533, 0.21267)
loop_1 = loop_1.lineTo(0.57252, 0.21267)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_38_interval_0.stl')