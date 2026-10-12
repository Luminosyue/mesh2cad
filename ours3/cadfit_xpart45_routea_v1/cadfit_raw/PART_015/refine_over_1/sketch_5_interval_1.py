import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07539, -0.04647, -0.04907), normal=(0.69558, -0.71845, -6e-05), xDir=(-0.71845, -0.69558, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17142, -0.25934)
loop_1 = loop_1.lineTo(0.12323, -0.26129)
loop_1 = loop_1.lineTo(0.1047, -0.26206)
loop_1 = loop_1.lineTo(0.07656, -0.2618)
loop_1 = loop_1.lineTo(0.07657, -0.30577)
loop_1 = loop_1.lineTo(0.12853, -0.29785)
loop_1 = loop_1.threePointArc((0.15856, -0.27635), (0.1869, -0.25575))
loop_1 = loop_1.lineTo(0.17142, -0.25934)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_5_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_5_interval_1.stl')