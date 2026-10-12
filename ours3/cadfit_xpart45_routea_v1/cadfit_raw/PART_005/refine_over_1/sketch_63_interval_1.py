import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04903, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01118, -0.42126)
loop_1 = loop_1.lineTo(-0.29822, -0.41036)
loop_1 = loop_1.lineTo(-0.32154, -0.41325)
loop_1 = loop_1.lineTo(-0.35102, -0.415)
loop_1 = loop_1.lineTo(-0.08805, -0.42103)
loop_1 = loop_1.threePointArc((-0.03967, -0.42148), (0.00703, -0.42117))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_63_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_63_interval_1.stl')