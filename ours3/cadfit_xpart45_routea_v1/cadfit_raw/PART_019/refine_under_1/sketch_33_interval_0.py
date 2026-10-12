import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.54432, 0.00073, -0.82372), normal=(-0.51315, -0.0004, 0.8583), xDir=(-0.00078, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.72184, 0.28547)
loop_1 = loop_1.lineTo(0.72156, -0.13193)
loop_1 = loop_1.lineTo(0.72154, -0.16833)
loop_1 = loop_1.lineTo(0.72144, -0.3111)
loop_1 = loop_1.lineTo(-0.72856, -0.3088)
loop_1 = loop_1.lineTo(-0.72816, 0.28893)
loop_1 = loop_1.lineTo(0.70446, 0.28552)
loop_1 = loop_1.lineTo(0.72184, 0.28547)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_33_interval_0.stl')