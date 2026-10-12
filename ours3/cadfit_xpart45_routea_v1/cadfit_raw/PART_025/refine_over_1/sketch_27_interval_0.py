import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05298, -0.06557, 0.39245), normal=(-0.51381, 0.02913, -0.85741), xDir=(0.0566, 0.9984, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03904, -0.38516)
loop_1 = loop_1.lineTo(0.04221, -0.39916)
loop_1 = loop_1.lineTo(0.03374, -0.41512)
loop_1 = loop_1.lineTo(0.00945, -0.43263)
loop_1 = loop_1.lineTo(-0.00239, -0.43785)
loop_1 = loop_1.threePointArc((-0.01785, -0.4416), (-0.03216, -0.4475))
loop_1 = loop_1.lineTo(-0.04348, -0.45078)
loop_1 = loop_1.threePointArc((-0.05282, -0.45377), (-0.06178, -0.45667))
loop_1 = loop_1.lineTo(-0.0789, -0.46123)
loop_1 = loop_1.lineTo(0.042, -0.43489)
loop_1 = loop_1.lineTo(0.11515, -0.41615)
loop_1 = loop_1.lineTo(0.09499, -0.29668)
loop_1 = loop_1.lineTo(0.04469, -0.36515)
loop_1 = loop_1.threePointArc((0.05836, -0.36515), (0.06879, -0.36515))
loop_1 = loop_1.lineTo(0.05324, -0.37508)
loop_1 = loop_1.lineTo(0.04141, -0.38348)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_27_interval_0.stl')