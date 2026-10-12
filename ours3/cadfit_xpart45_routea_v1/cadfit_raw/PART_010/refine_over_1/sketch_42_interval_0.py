import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.06458, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.62578, 0.38633)
loop_1 = loop_1.threePointArc((-0.63104, 0.37945), (-0.63588, 0.37268))
loop_1 = loop_1.threePointArc((-0.6275, 0.38406), (-0.61951, 0.39526))
loop_1 = loop_1.lineTo(-0.58993, 0.43311)
loop_1 = loop_1.threePointArc((-0.57699, 0.44888), (-0.56503, 0.46416))
loop_1 = loop_1.lineTo(-0.54605, 0.48646)
loop_1 = loop_1.lineTo(-0.52876, 0.50378)
loop_1 = loop_1.threePointArc((-0.51976, 0.51197), (-0.5104, 0.52022))
loop_1 = loop_1.lineTo(-0.69973, 0.52684)
loop_1 = loop_1.lineTo(-0.62592, 0.38654)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_42_interval_0.stl')