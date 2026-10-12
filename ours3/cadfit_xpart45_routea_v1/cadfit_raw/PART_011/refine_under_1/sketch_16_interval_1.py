import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41487, 0.04481, -0.02316), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78121, 0.19857)
loop_1 = loop_1.lineTo(-0.78556, 0.18464)
loop_1 = loop_1.lineTo(-0.78853, 0.17347)
loop_1 = loop_1.lineTo(-0.79186, 0.12815)
loop_1 = loop_1.lineTo(-0.79142, 0.07935)
loop_1 = loop_1.lineTo(-0.79157, 0.06803)
loop_1 = loop_1.threePointArc((-0.79035, 0.02088), (-0.78879, -0.02437))
loop_1 = loop_1.lineTo(-0.78843, -0.07976)
loop_1 = loop_1.lineTo(-0.78878, -0.12437)
loop_1 = loop_1.lineTo(-0.78742, -0.16869)
loop_1 = loop_1.lineTo(-0.78121, -0.17899)
loop_1 = loop_1.lineTo(-0.78121, 0.19473)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_16_interval_1.stl')