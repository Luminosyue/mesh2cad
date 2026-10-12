import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.76, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.79988, -0.28206)
loop_1 = loop_1.lineTo(-0.79097, -0.29267)
loop_1 = loop_1.threePointArc((-0.78629, -0.29696), (-0.78054, -0.29894))
loop_1 = loop_1.lineTo(-0.73643, -0.3156)
loop_1 = loop_1.lineTo(-0.55267, -0.31744)
loop_1 = loop_1.lineTo(-0.23945, -0.31986)
loop_1 = loop_1.lineTo(0.04905, -0.32119)
loop_1 = loop_1.threePointArc((0.26392, -0.32266), (0.46918, -0.32096))
loop_1 = loop_1.lineTo(0.69924, -0.3155)
loop_1 = loop_1.lineTo(0.73222, -0.31253)
loop_1 = loop_1.lineTo(0.78104, -0.28881)
loop_1 = loop_1.lineTo(-0.79987, -0.28206)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_52_interval_0.stl')