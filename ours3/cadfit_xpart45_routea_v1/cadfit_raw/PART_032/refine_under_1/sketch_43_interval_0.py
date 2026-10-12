import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72274, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56893, -0.05887)
loop_1 = loop_1.lineTo(-0.82367, -0.06203)
loop_1 = loop_1.lineTo(-0.82269, -0.14547)
loop_1 = loop_1.lineTo(0.56894, -0.14159)
loop_1 = loop_1.lineTo(0.56893, -0.05985)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_43_interval_0.stl')