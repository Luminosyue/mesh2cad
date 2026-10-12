import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06971, 0.18898)
loop_1 = loop_1.lineTo(0.04505, 0.22295)
loop_1 = loop_1.threePointArc((0.04468, 0.23091), (0.0443, 0.23855))
loop_1 = loop_1.threePointArc((0.04735, 0.24753), (0.04983, 0.25519))
loop_1 = loop_1.threePointArc((0.06165, 0.26476), (0.069, 0.27004))
loop_1 = loop_1.lineTo(0.09851, 0.1857)
loop_1 = loop_1.lineTo(0.06971, 0.18898)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_39_interval_0.stl')