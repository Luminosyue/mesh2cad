import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.93092, -0.02344, 0.13122), normal=(-0.99993, -0.0005, 0.01148), xDir=(-0.0005, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04107, 0.0646)
loop_1 = loop_1.lineTo(0.41345, 0.0643)
loop_1 = loop_1.lineTo(0.41344, -0.44794)
loop_1 = loop_1.lineTo(0.04273, -0.44767)
loop_1 = loop_1.lineTo(0.09308, -0.44133)
loop_1 = loop_1.lineTo(0.12499, -0.4349)
loop_1 = loop_1.lineTo(0.14508, -0.43214)
loop_1 = loop_1.lineTo(0.18361, -0.42015)
loop_1 = loop_1.lineTo(0.22212, -0.40626)
loop_1 = loop_1.lineTo(0.04462, 0.05536)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_39_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_39_interval_1.stl')