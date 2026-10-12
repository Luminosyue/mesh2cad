import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14268, 0.05947)
loop_1 = loop_1.lineTo(0.113, 0.07277)
loop_1 = loop_1.lineTo(0.10091, 0.09338)
loop_1 = loop_1.lineTo(0.09868, 0.10546)
loop_1 = loop_1.lineTo(0.10669, 0.12865)
loop_1 = loop_1.lineTo(0.14237, 0.06037)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_37_interval_0.stl')