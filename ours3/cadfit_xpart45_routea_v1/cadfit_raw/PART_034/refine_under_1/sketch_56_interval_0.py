import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.82, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.67019, -0.27258)
loop_1 = loop_1.threePointArc((-0.66423, -0.28017), (-0.65731, -0.28632))
loop_1 = loop_1.threePointArc((-0.63624, -0.29691), (-0.61589, -0.30457))
loop_1 = loop_1.threePointArc((-0.58715, -0.30652), (-0.56044, -0.30651))
loop_1 = loop_1.threePointArc((-0.52098, -0.30895), (-0.48391, -0.30919))
loop_1 = loop_1.lineTo(-0.30853, -0.31323)
loop_1 = loop_1.lineTo(-0.22124, -0.31477)
loop_1 = loop_1.threePointArc((-0.13228, -0.31507), (-0.04774, -0.31345))
loop_1 = loop_1.lineTo(0.06002, -0.31351)
loop_1 = loop_1.threePointArc((0.22305, -0.313), (0.37869, -0.31133))
loop_1 = loop_1.lineTo(0.52646, -0.31091)
loop_1 = loop_1.threePointArc((0.56427, -0.30841), (0.59941, -0.30322))
loop_1 = loop_1.threePointArc((0.61326, -0.3012), (0.62488, -0.29647))
loop_1 = loop_1.threePointArc((0.64063, -0.29033), (0.65441, -0.28358))
loop_1 = loop_1.lineTo(-0.66936, -0.27263)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_56_interval_0.stl')