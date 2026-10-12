import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99815, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08873, -0.04539)
loop_1 = loop_1.lineTo(-0.13631, -0.04554)
loop_1 = loop_1.lineTo(-0.13616, -0.11846)
loop_1 = loop_1.lineTo(-0.13463, -0.09649)
loop_1 = loop_1.threePointArc((-0.12341, -0.09406), (-0.12174, -0.0914))
loop_1 = loop_1.lineTo(-0.11342, -0.0785)
loop_1 = loop_1.threePointArc((-0.09812, -0.05776), (-0.08877, -0.04546))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_38_interval_0.stl')