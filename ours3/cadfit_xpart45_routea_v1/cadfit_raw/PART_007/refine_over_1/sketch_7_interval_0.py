import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.57374, 0.12147, -0.55542), normal=(-0.0455, 3e-05, 0.99896), xDir=(0.0, 1.0, -3e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.1115, 0.27419)
loop_1 = loop_1.lineTo(-1.1115, -0.11107)
loop_1 = loop_1.lineTo(-1.08062, -0.11107)
loop_1 = loop_1.lineTo(-1.09281, -0.08706)
loop_1 = loop_1.lineTo(-1.09918, -0.06759)
loop_1 = loop_1.threePointArc((-1.10127, -0.03048), (-1.10274, 0.00443))
loop_1 = loop_1.threePointArc((-1.10395, 0.03211), (-1.1042, 0.05695))
loop_1 = loop_1.lineTo(-1.10638, 0.17351)
loop_1 = loop_1.lineTo(-1.10734, 0.18466)
loop_1 = loop_1.threePointArc((-1.10867, 0.21766), (-1.11016, 0.24933))
loop_1 = loop_1.lineTo(-1.11137, 0.27013)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_7_interval_0.stl')