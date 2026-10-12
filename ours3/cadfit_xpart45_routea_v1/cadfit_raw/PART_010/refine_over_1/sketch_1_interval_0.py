import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02559, -0.58852, -0.00627), normal=(-0.00186, 1.0, -0.0021), xDir=(1.0, 0.00186, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.63495, -0.70569)
loop_1 = loop_1.lineTo(-0.7436, -0.56502)
loop_1 = loop_1.lineTo(-0.76248, -0.58508)
loop_1 = loop_1.threePointArc((-0.76751, -0.59027), (-0.77517, -0.5981))
loop_1 = loop_1.lineTo(-0.79066, -0.61651)
loop_1 = loop_1.threePointArc((-0.79754, -0.62648), (-0.80329, -0.63453))
loop_1 = loop_1.threePointArc((-0.80488, -0.65378), (-0.80652, -0.67097))
loop_1 = loop_1.threePointArc((-0.79788, -0.68678), (-0.79057, -0.70067))
loop_1 = loop_1.threePointArc((-0.76939, -0.72479), (-0.75426, -0.7407))
loop_1 = loop_1.lineTo(-0.73901, -0.74443)
loop_1 = loop_1.lineTo(-0.72657, -0.74698)
loop_1 = loop_1.lineTo(-0.69799, -0.74023)
loop_1 = loop_1.lineTo(-0.68136, -0.73342)
loop_1 = loop_1.lineTo(-0.64364, -0.70836)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_1_interval_0.stl')