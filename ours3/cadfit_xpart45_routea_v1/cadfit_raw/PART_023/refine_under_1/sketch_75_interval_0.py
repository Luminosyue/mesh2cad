import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48614, -0.05842)
loop_1 = loop_1.lineTo(0.18957, -0.44488)
loop_1 = loop_1.lineTo(0.18926, -0.45514)
loop_1 = loop_1.lineTo(-0.47499, -0.07457)
loop_1 = loop_1.threePointArc((-0.4806, -0.06627), (-0.48585, -0.05884))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_75_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_75_interval_0.stl')