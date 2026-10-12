import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.15488, -0.02223, -0.26182), normal=(0.0004, 0.00703, 0.99998), xDir=(0.0, 0.99998, -0.00703))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20252, 0.31972)
loop_1 = loop_1.lineTo(0.20207, 0.33632)
loop_1 = loop_1.lineTo(0.19164, 0.36273)
loop_1 = loop_1.lineTo(0.16643, 0.35631)
loop_1 = loop_1.lineTo(0.16557, 0.33632)
loop_1 = loop_1.lineTo(0.16572, 0.3189)
loop_1 = loop_1.lineTo(0.18385, 0.30424)
loop_1 = loop_1.threePointArc((0.19275, 0.30997), (0.20058, 0.31511))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_23_interval_0.stl')