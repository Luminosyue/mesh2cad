import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1481, -0.06202, 0.09127), normal=(-0.01736, -0.13025, -0.99133), xDir=(0.0, -0.99148, 0.13027))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82465, 0.34235)
loop_1 = loop_1.threePointArc((-0.83209, 0.05204), (-0.83725, -0.2267))
loop_1 = loop_1.lineTo(-0.84132, -0.47733)
loop_1 = loop_1.lineTo(-0.83701, -0.50537)
loop_1 = loop_1.lineTo(-0.83589, -0.52628)
loop_1 = loop_1.lineTo(-0.8261, 0.18517)
loop_1 = loop_1.lineTo(-0.82513, 0.29304)
loop_1 = loop_1.lineTo(-0.82488, 0.32002)
loop_1 = loop_1.lineTo(-0.82317, 0.35646)
loop_1 = loop_1.lineTo(-0.82465, 0.34235)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_14_interval_0.stl')