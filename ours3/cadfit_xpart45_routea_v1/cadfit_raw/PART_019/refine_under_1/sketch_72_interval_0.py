import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.85), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78923, 0.51626)
loop_1 = loop_1.lineTo(0.78469, -0.60374)
loop_1 = loop_1.lineTo(0.6172, -0.6022)
loop_1 = loop_1.lineTo(0.59269, -0.60374)
loop_1 = loop_1.lineTo(0.58385, -0.59112)
loop_1 = loop_1.lineTo(0.56119, -0.60374)
loop_1 = loop_1.lineTo(-0.78172, -0.60014)
loop_1 = loop_1.lineTo(-0.77717, 0.51626)
loop_1 = loop_1.lineTo(0.78743, 0.51626)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_72_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_72_interval_0.stl')