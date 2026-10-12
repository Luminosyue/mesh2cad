import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.28048, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23892, 0.8)
loop_1 = loop_1.lineTo(0.30525, 0.79984)
loop_1 = loop_1.lineTo(0.27112, 0.76968)
loop_1 = loop_1.lineTo(0.23906, 0.79403)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_34_interval_0.stl')