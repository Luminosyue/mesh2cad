import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35939, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33939, 0.77)
loop_1 = loop_1.lineTo(0.33907, 0.52134)
loop_1 = loop_1.threePointArc((0.33722, 0.54348), (0.33486, 0.5645))
loop_1 = loop_1.threePointArc((0.33137, 0.58781), (0.32734, 0.60988))
loop_1 = loop_1.threePointArc((0.3241, 0.62539), (0.32113, 0.64143))
loop_1 = loop_1.lineTo(0.3097, 0.68136)
loop_1 = loop_1.threePointArc((0.30413, 0.69838), (0.29863, 0.716))
loop_1 = loop_1.lineTo(0.28292, 0.75367)
loop_1 = loop_1.threePointArc((0.27885, 0.76167), (0.27505, 0.76999))
loop_1 = loop_1.lineTo(0.3392, 0.77)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_69_interval_0.stl')