import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11182, 0.91498, -0.08663), normal=(-0.18861, 0.98205, 0.0), xDir=(0.98205, 0.18861, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34048, 0.43319)
loop_1 = loop_1.lineTo(-0.34029, 0.22032)
loop_1 = loop_1.lineTo(-0.33957, 0.23172)
loop_1 = loop_1.lineTo(-0.33565, 0.27245)
loop_1 = loop_1.lineTo(-0.33391, 0.2841)
loop_1 = loop_1.lineTo(-0.32787, 0.32087)
loop_1 = loop_1.threePointArc((-0.3209, 0.3497), (-0.3141, 0.37611))
loop_1 = loop_1.threePointArc((-0.29396, 0.40576), (-0.2787, 0.42793))
loop_1 = loop_1.lineTo(-0.3378, 0.43319)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_40_interval_0.stl')