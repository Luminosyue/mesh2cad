import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00443, 0.04091)
loop_1 = loop_1.lineTo(-0.02842, -0.00693)
loop_1 = loop_1.threePointArc((-0.04731, -0.04357), (-0.0652, -0.07884))
loop_1 = loop_1.lineTo(-0.07142, -0.09128)
loop_1 = loop_1.lineTo(-0.07024, -0.10136)
loop_1 = loop_1.lineTo(0.04188, 0.03197)
loop_1 = loop_1.lineTo(-0.00442, 0.0409)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_43_interval_0.stl')