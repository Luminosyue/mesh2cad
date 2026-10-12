import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.53487, 0.05404, -0.01855), normal=(-0.12306, 0.9924, 0.00064), xDir=(0.9924, 0.12306, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26863, 0.15271)
loop_1 = loop_1.lineTo(0.26802, 0.04294)
loop_1 = loop_1.lineTo(0.26952, 0.2321)
loop_1 = loop_1.lineTo(0.2243, 0.2321)
loop_1 = loop_1.lineTo(0.23747, 0.21491)
loop_1 = loop_1.lineTo(0.24779, 0.20355)
loop_1 = loop_1.lineTo(0.26004, 0.19067)
loop_1 = loop_1.lineTo(0.26697, 0.17768)
loop_1 = loop_1.lineTo(0.26867, 0.1591)
loop_1 = loop_1.lineTo(0.26694, 0.14674)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_11_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_11_interval_1.stl')