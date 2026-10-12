import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.09357, -0.07198, -0.07155), normal=(-0.86817, 0.10861, 0.48423), xDir=(0.12413, 0.99227, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08535, 0.02325)
loop_1 = loop_1.lineTo(0.04625, 0.01315)
loop_1 = loop_1.lineTo(-0.21314, -0.054)
loop_1 = loop_1.lineTo(-0.19944, -0.05257)
loop_1 = loop_1.threePointArc((-0.18985, -0.05175), (-0.17985, -0.05109))
loop_1 = loop_1.threePointArc((-0.16219, -0.04963), (-0.14851, -0.04824))
loop_1 = loop_1.threePointArc((-0.12218, -0.04631), (-0.09785, -0.04492))
loop_1 = loop_1.threePointArc((-0.06927, -0.04233), (-0.04641, -0.03966))
loop_1 = loop_1.lineTo(-0.03413, -0.03839)
loop_1 = loop_1.threePointArc((-0.00641, -0.03421), (0.01987, -0.02839))
loop_1 = loop_1.lineTo(0.0484, -0.02165)
loop_1 = loop_1.threePointArc((0.05975, -0.01814), (0.07162, -0.01462))
loop_1 = loop_1.lineTo(0.08535, 0.02325)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_1_interval_0.stl')