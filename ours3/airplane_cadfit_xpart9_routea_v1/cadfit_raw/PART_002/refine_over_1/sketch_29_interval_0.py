import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.96236, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15068, -0.04539)
loop_1 = loop_1.lineTo(-0.17067, -0.09364)
loop_1 = loop_1.lineTo(-0.17924, -0.11407)
loop_1 = loop_1.lineTo(-0.1922, -0.14411)
loop_1 = loop_1.lineTo(-0.20512, -0.17701)
loop_1 = loop_1.lineTo(-0.21316, -0.19454)
loop_1 = loop_1.lineTo(-0.21279, -0.04539)
loop_1 = loop_1.lineTo(-0.1508, -0.04539)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_29_interval_0.stl')