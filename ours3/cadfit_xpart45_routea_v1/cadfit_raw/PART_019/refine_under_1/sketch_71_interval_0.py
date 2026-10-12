import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.33), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.71192, 0.98214)
loop_1 = loop_1.lineTo(0.31277, 0.98305)
loop_1 = loop_1.threePointArc((0.24144, 0.98381), (0.17366, 0.98344))
loop_1 = loop_1.threePointArc((0.03054, 0.98439), (-0.10615, 0.98372))
loop_1 = loop_1.threePointArc((-0.17346, 0.985), (-0.23739, 0.98439))
loop_1 = loop_1.threePointArc((-0.3318, 0.9854), (-0.42173, 0.98478))
loop_1 = loop_1.threePointArc((-0.49927, 0.98689), (-0.57303, 0.98721))
loop_1 = loop_1.threePointArc((-0.61807, 0.98813), (-0.66063, 0.98792))
loop_1 = loop_1.lineTo(-0.71123, 0.98221)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_71_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_71_interval_0.stl')