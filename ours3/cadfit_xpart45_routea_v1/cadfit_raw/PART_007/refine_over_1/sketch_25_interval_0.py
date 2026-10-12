import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.56627, 0.14645, -0.06679), normal=(-0.99999, 0.00379, -3e-05), xDir=(0.00379, 0.99999, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.43228, 0.26693)
loop_1 = loop_1.lineTo(-1.10044, 0.35321)
loop_1 = loop_1.lineTo(0.84297, 0.35188)
loop_1 = loop_1.lineTo(0.84297, 0.16688)
loop_1 = loop_1.lineTo(0.83828, 0.19845)
loop_1 = loop_1.lineTo(0.83381, 0.2188)
loop_1 = loop_1.lineTo(0.82344, 0.23716)
loop_1 = loop_1.lineTo(0.82344, 0.27033)
loop_1 = loop_1.lineTo(0.45287, 0.26711)
loop_1 = loop_1.lineTo(0.43228, 0.26693)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_25_interval_0.stl')