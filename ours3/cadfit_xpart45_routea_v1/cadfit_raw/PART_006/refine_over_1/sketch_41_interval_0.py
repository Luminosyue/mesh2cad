import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.94896, -0.02249, 0.10963), normal=(-0.99993, -0.0005, 0.01148), xDir=(-0.0005, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24505, 0.65123)
loop_1 = loop_1.lineTo(-0.2587, 0.64456)
loop_1 = loop_1.lineTo(-0.45655, 0.69771)
loop_1 = loop_1.lineTo(-0.08802, 0.69732)
loop_1 = loop_1.lineTo(-0.10657, 0.69542)
loop_1 = loop_1.lineTo(-0.16695, 0.68108)
loop_1 = loop_1.lineTo(-0.21008, 0.66715)
loop_1 = loop_1.lineTo(-0.22222, 0.66225)
loop_1 = loop_1.lineTo(-0.24179, 0.65281)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_41_interval_0.stl')