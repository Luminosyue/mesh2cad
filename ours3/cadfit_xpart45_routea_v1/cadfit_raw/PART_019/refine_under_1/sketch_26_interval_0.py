import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03191, 0.78237, -0.01475), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.39866, -0.93101)
loop_1 = loop_1.lineTo(0.25486, -0.96742)
loop_1 = loop_1.lineTo(0.22141, -0.97605)
loop_1 = loop_1.lineTo(0.15972, -0.98652)
loop_1 = loop_1.lineTo(0.0948, -0.98931)
loop_1 = loop_1.lineTo(0.06892, -0.98923)
loop_1 = loop_1.lineTo(0.10269, -0.99057)
loop_1 = loop_1.lineTo(0.16804, -0.98693)
loop_1 = loop_1.lineTo(0.22902, -0.97951)
loop_1 = loop_1.threePointArc((0.27065, -0.97013), (0.30398, -0.96243))
loop_1 = loop_1.lineTo(0.34608, -0.9505)
loop_1 = loop_1.lineTo(0.3899, -0.93562)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.55)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_26_interval_0.stl')