import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45951, 0.08656, 0.27458), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28239, -0.36297)
loop_1 = loop_1.lineTo(0.2157, -0.29305)
loop_1 = loop_1.lineTo(0.22579, -0.28771)
loop_1 = loop_1.threePointArc((0.23281, -0.2856), (0.23952, -0.28348))
loop_1 = loop_1.lineTo(0.25637, -0.28382)
loop_1 = loop_1.lineTo(0.26967, -0.28779)
loop_1 = loop_1.lineTo(0.29015, -0.3091)
loop_1 = loop_1.threePointArc((0.29202, -0.31494), (0.29386, -0.32105))
loop_1 = loop_1.lineTo(0.28239, -0.36297)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_17_interval_0.stl')