import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.71114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.65966, -0.52237)
loop_1 = loop_1.lineTo(-0.69184, -0.55165)
loop_1 = loop_1.lineTo(-0.11146, -0.55135)
loop_1 = loop_1.lineTo(-0.13436, -0.53517)
loop_1 = loop_1.lineTo(-0.66683, -0.52873)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/greedy_greedy_step_extrude.stl')