import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.82368, 0.0389, 0.06375), normal=(-0.9914, 0.13085, -0.00282), xDir=(0.13085, 0.9914, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.37023, 0.19061)
loop_1 = loop_1.lineTo(-0.37216, -0.12034)
loop_1 = loop_1.lineTo(-0.37562, -0.01799)
loop_1 = loop_1.lineTo(-0.3757, 0.02836)
loop_1 = loop_1.lineTo(-0.38032, 0.09288)
loop_1 = loop_1.threePointArc((-0.38128, 0.11795), (-0.38201, 0.14089))
loop_1 = loop_1.lineTo(-0.38131, 0.17525)
loop_1 = loop_1.lineTo(-0.37333, 0.18601)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_47_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_47_interval_1.stl')