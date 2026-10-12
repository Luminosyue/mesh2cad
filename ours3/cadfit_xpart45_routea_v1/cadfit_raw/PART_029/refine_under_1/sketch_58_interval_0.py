import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.05), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1069, 0.9649)
loop_1 = loop_1.lineTo(-0.07305, 0.19817)
loop_1 = loop_1.threePointArc((-0.06558, 0.19849), (-0.059, 0.19955))
loop_1 = loop_1.lineTo(-0.07076, 0.203)
loop_1 = loop_1.lineTo(-0.10354, 0.96643)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_58_interval_0.stl')