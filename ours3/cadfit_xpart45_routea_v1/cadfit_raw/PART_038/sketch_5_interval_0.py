import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.83187, 0.13354, 0.03902), normal=(-0.36974, 0.92873, 0.02751), xDir=(0.92908, 0.36988, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.00613, 0.03073)
loop_1 = loop_1.lineTo(-0.99502, 0.02464)
loop_1 = loop_1.lineTo(-0.98123, 0.02042)
loop_1 = loop_1.lineTo(-0.96916, 0.02243)
loop_1 = loop_1.lineTo(-0.95237, 0.04229)
loop_1 = loop_1.threePointArc((-0.95296, 0.04738), (-0.95351, 0.05268))
loop_1 = loop_1.threePointArc((-0.96321, 0.06495), (-0.96716, 0.06738))
loop_1 = loop_1.lineTo(-1.00613, 0.03073)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/sketch_5_interval_0.stl')