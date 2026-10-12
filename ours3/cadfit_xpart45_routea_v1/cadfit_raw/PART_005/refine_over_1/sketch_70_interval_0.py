import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.49918, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.83785, 0.09909)
loop_1 = loop_1.threePointArc((-0.83313, 0.08751), (-0.82844, 0.07536))
loop_1 = loop_1.lineTo(-0.819, 0.05181)
loop_1 = loop_1.lineTo(-0.76259, -0.00279)
loop_1 = loop_1.lineTo(-0.76554, -0.02277)
loop_1 = loop_1.lineTo(-0.77522, -0.05119)
loop_1 = loop_1.lineTo(-0.81766, -0.07179)
loop_1 = loop_1.lineTo(-0.83786, -0.09251)
loop_1 = loop_1.lineTo(-0.83786, 0.09893)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_70_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_70_interval_0.stl')