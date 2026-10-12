import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03635, -0.88853, -0.0075), normal=(-0.00068, 0.99993, 0.01201), xDir=(1.0, 0.00068, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35781, 0.21456)
loop_1 = loop_1.lineTo(-0.36659, 0.18819)
loop_1 = loop_1.lineTo(-0.36312, 0.15511)
loop_1 = loop_1.lineTo(-0.36184, 0.1338)
loop_1 = loop_1.lineTo(-0.36093, 0.1048)
loop_1 = loop_1.threePointArc((-0.35928, 0.08581), (-0.35747, 0.06946))
loop_1 = loop_1.lineTo(-0.35551, 0.05128)
loop_1 = loop_1.lineTo(-0.35496, 0.03952)
loop_1 = loop_1.lineTo(-0.35216, 0.01629)
loop_1 = loop_1.lineTo(-0.35776, 0.21256)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_26_interval_0.stl')