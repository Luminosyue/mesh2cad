import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.91317, 0.03776, -0.24624), normal=(-0.99192, -0.00307, 0.12685), xDir=(-0.0031, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28382, -0.19975)
loop_1 = loop_1.lineTo(0.07613, 0.3174)
loop_1 = loop_1.lineTo(0.35237, 0.31617)
loop_1 = loop_1.lineTo(0.35214, -0.26366)
loop_1 = loop_1.lineTo(0.32607, -0.14338)
loop_1 = loop_1.lineTo(0.29184, -0.19113)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_26_interval_0.stl')