import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19421, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.5254, 0.16016)
loop_1 = loop_1.threePointArc((-0.50256, 0.15377), (-0.48364, 0.14927))
loop_1 = loop_1.threePointArc((-0.43631, 0.14229), (-0.39123, 0.13703))
loop_1 = loop_1.threePointArc((-0.13412, 0.10464), (0.11232, 0.07478))
loop_1 = loop_1.lineTo(0.21069, 0.0621)
loop_1 = loop_1.lineTo(0.29907, 0.0524)
loop_1 = loop_1.lineTo(-0.13235, 0.10952)
loop_1 = loop_1.lineTo(-0.16215, 0.11268)
loop_1 = loop_1.lineTo(-0.52476, 0.16018)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_22_interval_0.stl')