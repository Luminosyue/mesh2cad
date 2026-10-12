import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07489, 0.069, 0.54018), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14019, -1.05119)
loop_1 = loop_1.lineTo(0.02944, -1.04891)
loop_1 = loop_1.threePointArc((-0.02061, -1.0441), (-0.06604, -1.03917))
loop_1 = loop_1.lineTo(-0.01603, -1.04692)
loop_1 = loop_1.lineTo(0.02966, -1.05154)
loop_1 = loop_1.lineTo(0.07319, -1.05372)
loop_1 = loop_1.lineTo(0.11089, -1.05397)
loop_1 = loop_1.lineTo(0.15326, -1.05216)
loop_1 = loop_1.lineTo(0.549, -1.05128)
loop_1 = loop_1.lineTo(0.549, -0.94332)
loop_1 = loop_1.lineTo(0.14678, -1.04945)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_20_interval_0.stl')