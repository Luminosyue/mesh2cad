import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.33825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.72898, 0.54304)
loop_1 = loop_1.lineTo(-0.99024, 0.07443)
loop_1 = loop_1.lineTo(-0.99869, 0.05883)
loop_1 = loop_1.threePointArc((-0.99566, 0.07912), (-0.99434, 0.09841))
loop_1 = loop_1.lineTo(-0.97812, 0.14596)
loop_1 = loop_1.threePointArc((-0.97039, 0.167), (-0.96207, 0.18836))
loop_1 = loop_1.threePointArc((-0.94558, 0.22836), (-0.93064, 0.26673))
loop_1 = loop_1.lineTo(-0.91031, 0.31077)
loop_1 = loop_1.lineTo(-0.88953, 0.35128)
loop_1 = loop_1.lineTo(-0.86895, 0.38708)
loop_1 = loop_1.lineTo(-0.83289, 0.43248)
loop_1 = loop_1.lineTo(-0.79892, 0.4719)
loop_1 = loop_1.lineTo(-0.7718, 0.5005)
loop_1 = loop_1.threePointArc((-0.74944, 0.51955), (-0.7291, 0.54296))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_42_interval_0.stl')