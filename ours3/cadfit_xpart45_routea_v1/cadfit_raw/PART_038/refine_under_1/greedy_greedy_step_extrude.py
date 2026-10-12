import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02925, -0.2045, -0.12403), normal=(0.0, -1e-05, 1.0), xDir=(-0.0, 1.0, 1e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01879, 1.0219)
loop_1 = loop_1.lineTo(-0.00018, 1.0215)
loop_1 = loop_1.lineTo(0.00915, 1.00863)
loop_1 = loop_1.lineTo(0.00664, 0.81887)
loop_1 = loop_1.lineTo(0.00606, 0.64467)
loop_1 = loop_1.lineTo(0.00506, 0.56201)
loop_1 = loop_1.lineTo(-0.00431, -0.57732)
loop_1 = loop_1.lineTo(-0.01432, -0.57723)
loop_1 = loop_1.lineTo(-0.0217, -0.55248)
loop_1 = loop_1.threePointArc((-0.03008, -0.52076), (-0.03874, -0.49325))
loop_1 = loop_1.threePointArc((-0.04188, -0.48105), (-0.04352, -0.47093))
loop_1 = loop_1.lineTo(-0.03073, 1.02201)
loop_1 = loop_1.lineTo(-0.02039, 1.02192)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/greedy_greedy_step_extrude.stl')