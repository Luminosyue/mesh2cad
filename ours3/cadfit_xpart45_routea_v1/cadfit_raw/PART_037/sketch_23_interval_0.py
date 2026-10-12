import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45952, 0.0908, 0.26553), normal=(-0.00174, 0.42485, -0.90526), xDir=(0.0, -0.90526, -0.42485))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26286, -0.56775)
loop_1 = loop_1.threePointArc((0.25953, -0.57387), (0.25603, -0.58024))
loop_1 = loop_1.lineTo(0.23849, -0.59136)
loop_1 = loop_1.lineTo(0.22309, -0.59417)
loop_1 = loop_1.lineTo(0.20964, -0.59276)
loop_1 = loop_1.lineTo(0.19592, -0.5187)
loop_1 = loop_1.threePointArc((0.20259, -0.51605), (0.20958, -0.51342))
loop_1 = loop_1.threePointArc((0.21768, -0.51363), (0.22464, -0.51404))
loop_1 = loop_1.threePointArc((0.23269, -0.51781), (0.23971, -0.52128))
loop_1 = loop_1.threePointArc((0.25065, -0.5305), (0.25479, -0.53465))
loop_1 = loop_1.threePointArc((0.26095, -0.54563), (0.26372, -0.55165))
loop_1 = loop_1.lineTo(0.26286, -0.56775)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_23_interval_0.stl')